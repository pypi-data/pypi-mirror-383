"""APRS.fi API client with rate limiting and caching."""

import time
from datetime import datetime
from typing import Any
from pathlib import Path

import httpx
from pydantic import BaseModel, Field
from .config import get_settings
from .vessels import VESSELS, Vessel
from .schemas import (
    LocationRequest,
    LocationResponse,
    LocationEntry,
    WeatherRequest,
    WeatherResponse,
    WeatherEntry,
    MessageRequest,
    MessageResponse,
)


class FerryPosition(BaseModel):
    """Ferry position and status from APRS."""

    mmsi: str
    vessel: Vessel
    latitude: float
    longitude: float
    speed_knots: float | None = None
    course_degrees: float | None = None
    altitude_meters: float | None = None
    timestamp: datetime
    comment: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)

    @property
    def age_seconds(self) -> float:
        """How many seconds old is this position."""
        return (datetime.now() - self.timestamp).total_seconds()

    @classmethod
    def from_location_entry(cls, entry: LocationEntry, vessel: Vessel) -> "FerryPosition":
        """Create FerryPosition from LocationEntry schema."""
        return cls(
            mmsi=entry.mmsi or entry.name,
            vessel=vessel,
            latitude=entry.latitude,
            longitude=entry.longitude,
            speed_knots=entry.speed_knots,
            course_degrees=entry.course,
            altitude_meters=float(entry.altitude) if entry.altitude else None,
            timestamp=entry.timestamp,
            comment=entry.comment,
            raw_data=entry.model_dump(),
        )


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, max_per_minute: int = 10):
        self.max_per_minute = max_per_minute
        self.requests: list[float] = []

    def wait_if_needed(self) -> None:
        """Block if we're exceeding rate limit."""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req for req in self.requests if now - req < 60]

        if len(self.requests) >= self.max_per_minute:
            # Calculate how long to wait
            oldest = self.requests[0]
            wait_time = 60 - (now - oldest)
            if wait_time > 0:
                time.sleep(wait_time)
                self.wait_if_needed()  # Recursive check
        else:
            self.requests.append(now)


class APRSClient:
    """Client for aprs.fi API with caching and rate limiting."""

    def __init__(self, api_key: str | None = None):
        """Initialize APRS client.

        Args:
            api_key: aprs.fi API key. If None, loads from settings/env.
        """
        self.settings = get_settings()
        if api_key:
            self.settings.api_key = api_key

        self.client = httpx.Client(
            base_url=self.settings.api_base_url,
            headers={"User-Agent": self.settings.user_agent},
            timeout=30.0,
        )
        self.rate_limiter = RateLimiter(self.settings.max_requests_per_minute)

        # Setup simple in-memory cache (dict with timestamps)
        self.cache: dict[str, tuple[Any, float]] = {}

    def _make_request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make API request with rate limiting.

        Args:
            endpoint: API endpoint (e.g., "get")
            params: Query parameters

        Returns:
            API response data

        Raises:
            httpx.HTTPError: If request fails
            ValueError: If API returns error
        """
        self.rate_limiter.wait_if_needed()

        params["apikey"] = self.settings.api_key
        params["format"] = "json"

        response = self.client.get(endpoint, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("result") != "ok":
            raise ValueError(f"API error: {data.get('description', 'Unknown error')}")

        return data

    def query_location(self, name: str, use_cache: bool = True) -> LocationResponse:
        """Query location data using typed schema.

        Args:
            name: Station name(s), comma-separated for multiple (max 20)
            use_cache: Whether to use cached data

        Returns:
            LocationResponse with typed entries
        """
        cache_key = f"location:{name}"

        if use_cache:
            cached_item = self.cache.get(cache_key)
            if cached_item is not None:
                data, timestamp = cached_item
                if time.time() - timestamp < self.settings.cache_ttl_seconds:
                    return LocationResponse(**data)

        try:
            data = self._make_request("get", {"name": name, "what": "loc"})
            response = LocationResponse(**data)

            # Cache the result as dict with timestamp
            self.cache[cache_key] = (data, time.time())

            return response
        except (httpx.HTTPError, ValueError) as e:
            # Return empty response on error
            return LocationResponse(
                command="get",
                result="fail",
                what="loc",
                found=0,
                description=str(e),
            )

    def query_weather(self, name: str, use_cache: bool = True) -> WeatherResponse:
        """Query weather data using typed schema.

        Args:
            name: Station name(s), comma-separated for multiple
            use_cache: Whether to use cached data

        Returns:
            WeatherResponse with typed entries
        """
        cache_key = f"weather:{name}"

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            data = self._make_request("get", {"name": name, "what": "wx"})
            response = WeatherResponse(**data)

            # Cache the result
            self.cache.set(cache_key, response, expire=self.settings.cache_ttl_seconds)

            return response
        except (httpx.HTTPError, ValueError) as e:
            return WeatherResponse(
                command="get",
                result="fail",
                what="wx",
                found=0,
                description=str(e),
            )

    def query_messages(self, dst: str, use_cache: bool = True) -> MessageResponse:
        """Query messages using typed schema.

        Args:
            dst: Message recipient(s), comma-separated (max 10)
            use_cache: Whether to use cached data

        Returns:
            MessageResponse with typed entries
        """
        cache_key = f"messages:{dst}"

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            data = self._make_request("get", {"what": "msg", "dst": dst})
            response = MessageResponse(**data)

            # Cache the result (shorter TTL for messages)
            self.cache.set(cache_key, response, expire=60)  # 1 minute

            return response
        except (httpx.HTTPError, ValueError) as e:
            return MessageResponse(
                command="get",
                result="fail",
                what="msg",
                found=0,
                description=str(e),
            )

    def get_vessel_position(
        self, mmsi: str, use_cache: bool = True
    ) -> FerryPosition | None:
        """Get current position for a vessel by MMSI.

        Args:
            mmsi: Vessel MMSI number
            use_cache: Whether to use cached data if available

        Returns:
            FerryPosition if found, None otherwise
        """
        if mmsi not in VESSELS:
            raise ValueError(f"Unknown vessel MMSI: {mmsi}")

        # Use typed query method
        response = self.query_location(mmsi, use_cache=use_cache)

        if response.result != "ok" or not response.entries:
            return None

        # Take most recent entry
        entry = response.entries[0]

        # Convert to FerryPosition
        return FerryPosition.from_location_entry(entry, VESSELS[mmsi])

    def get_all_ferries(self, use_cache: bool = True) -> list[FerryPosition]:
        """Get positions for all known Boston Harbor ferries.

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            List of ferry positions (may be empty if none found)
        """
        positions = []
        for mmsi in VESSELS:
            pos = self.get_vessel_position(mmsi, use_cache=use_cache)
            if pos:
                positions.append(pos)
        return positions

    def get_nearby_vessels(
        self, lat: float, lon: float, radius_km: float = 5.0
    ) -> list[dict[str, Any]]:
        """Get all APRS vessels near a location.

        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers

        Returns:
            List of vessel data from aprs.fi
        """
        try:
            data = self._make_request(
                "get",
                {
                    "lat": lat,
                    "lng": lon,
                    "distance": radius_km,
                    "what": "loc",
                    "format": "json",
                },
            )
            return data.get("entries", [])
        except (httpx.HTTPError, ValueError) as e:
            print(f"Error fetching nearby vessels: {e}")
            return []

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "path": "in-memory",
            "ttl_seconds": self.settings.cache_ttl_seconds,
        }

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
