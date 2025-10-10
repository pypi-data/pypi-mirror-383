"""Pydantic schemas for aprs.fi API requests and responses."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# API Request Models

class APRSRequest(BaseModel):
    """Base APRS API request."""

    name: str = Field(..., description="Station name(s), comma-separated for multiple (max 20)")
    what: Literal["loc", "wx", "msg"] = Field(..., description="Type of data to query")
    apikey: str = Field(..., description="API key from aprs.fi")
    format: Literal["json", "xml"] = Field(default="json", description="Response format")


class LocationRequest(APRSRequest):
    """Location data request."""

    what: Literal["loc"] = "loc"


class WeatherRequest(APRSRequest):
    """Weather data request."""

    what: Literal["wx"] = "wx"


class MessageRequest(BaseModel):
    """Message query request."""

    what: Literal["msg"] = "msg"
    dst: str = Field(..., description="Message recipient(s), comma-separated (max 10)")
    apikey: str = Field(..., description="API key from aprs.fi")
    format: Literal["json", "xml"] = Field(default="json", description="Response format")


# API Response Models

class APRSResponseBase(BaseModel):
    """Base APRS API response."""

    command: str = Field(..., description="API command that was called")
    result: Literal["ok", "fail"] = Field(..., description="Result status")
    description: Optional[str] = Field(None, description="Error description if result=fail")


class LocationEntry(BaseModel):
    """APRS location entry."""

    # Required fields
    name: str = Field(..., description="Station name, object, item or vessel")
    type: str = Field(..., description="Type: a=AIS, l=APRS station, i=item, o=object, w=weather")
    time: int = Field(..., description="Unix timestamp when target first reported this position")
    lasttime: int = Field(..., description="Unix timestamp when target last reported this position")
    lat: float | str = Field(..., description="Latitude in decimal degrees, north is positive")
    lng: float | str = Field(..., description="Longitude in decimal degrees, east is positive")

    # Optional common fields
    class_: Optional[str] = Field(None, alias="class", description="Class of station: a=APRS, i=AIS, w=Web")
    showname: Optional[str] = Field(None, description="Displayed name (may differ from unique name)")
    course: Optional[int | float] = Field(None, description="Course over ground in degrees")
    speed: Optional[str | int | float] = Field(None, description="Speed in km/h")
    altitude: Optional[str | int | float] = Field(None, description="Altitude in meters")
    symbol: Optional[str] = Field(None, description="APRS symbol table and code")
    srccall: Optional[str] = Field(None, description="Source callsign")
    dstcall: Optional[str] = Field(None, description="APRS destination callsign")
    comment: Optional[str] = Field(None, description="APRS comment or AIS destination/ETA")
    path: Optional[str] = Field(None, description="APRS/AIS packet path")
    phg: Optional[str] = Field(None, description="APRS PHG value")
    status: Optional[str] = Field(None, description="Last status message")
    status_lasttime: Optional[int] = Field(None, description="Unix timestamp of last status message")

    # AIS-specific fields
    mmsi: Optional[str] = Field(None, description="AIS vessel MMSI number")
    imo: Optional[str] = Field(None, description="AIS vessel IMO number")
    vesselclass: Optional[str] = Field(None, description="AIS vessel class code")
    navstat: Optional[str] = Field(None, description="AIS navigational status code")
    heading: Optional[int | str] = Field(None, description="Heading (may be invalid >359)")
    length: Optional[int | str] = Field(None, description="AIS vessel length in meters")
    width: Optional[int | str] = Field(None, description="AIS vessel width in meters")
    draught: Optional[float | str] = Field(None, description="AIS vessel draught in meters")
    ref_front: Optional[int | str] = Field(None, description="AIS position reference from front")
    ref_left: Optional[int | str] = Field(None, description="AIS position reference from left")

    @field_validator("lat", "lng", mode="before")
    @classmethod
    def parse_coordinate(cls, v):
        """Parse coordinate string to float."""
        if isinstance(v, str):
            return float(v)
        return v

    @field_validator("speed", "altitude", mode="before")
    @classmethod
    def parse_numeric_string(cls, v):
        """Parse numeric strings to float."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return None
        return v

    @property
    def latitude(self) -> float:
        """Get latitude as float."""
        return float(self.lat) if isinstance(self.lat, str) else self.lat

    @property
    def longitude(self) -> float:
        """Get longitude as float."""
        return float(self.lng) if isinstance(self.lng, str) else self.lng

    @property
    def speed_kmh(self) -> Optional[float]:
        """Get speed in km/h as float."""
        if self.speed is None:
            return None
        return float(self.speed) if isinstance(self.speed, str) else self.speed

    @property
    def speed_knots(self) -> Optional[float]:
        """Get speed in knots."""
        if self.speed_kmh is None:
            return None
        return self.speed_kmh * 0.539957  # Convert km/h to knots

    @property
    def timestamp(self) -> datetime:
        """Get timestamp as datetime."""
        return datetime.fromtimestamp(self.time)

    @property
    def last_timestamp(self) -> datetime:
        """Get last update timestamp as datetime."""
        return datetime.fromtimestamp(self.lasttime)


class LocationResponse(APRSResponseBase):
    """Location query response."""

    what: Literal["loc"] = "loc"
    found: int = Field(..., description="Number of entries returned")
    entries: list[LocationEntry] = Field(default_factory=list, description="Location entries")


class WeatherEntry(BaseModel):
    """APRS weather data entry."""

    name: str = Field(..., description="Station name")
    time: int = Field(..., description="Unix timestamp of weather report")

    # Weather fields (all optional)
    temp: Optional[str] = Field(None, description="Temperature in degrees Celsius")
    pressure: Optional[str] = Field(None, description="Atmospheric pressure in millibars")
    humidity: Optional[str] = Field(None, description="Relative humidity in %")
    wind_direction: Optional[str] = Field(None, description="Average wind direction in degrees")
    wind_speed: Optional[str] = Field(None, description="Average wind speed in m/s")
    wind_gust: Optional[str] = Field(None, description="Wind gust in m/s")
    rain_1h: Optional[str] = Field(None, description="Rainfall past 1h in mm")
    rain_24h: Optional[str] = Field(None, description="Rainfall past 24h in mm")
    rain_mn: Optional[str] = Field(None, description="Rainfall since midnight in mm")
    luminosity: Optional[str] = Field(None, description="Luminosity in W/m²")

    @field_validator("temp", "pressure", "humidity", "wind_speed", "wind_gust",
                     "rain_1h", "rain_24h", "rain_mn", "luminosity", mode="before")
    @classmethod
    def parse_numeric(cls, v):
        """Parse numeric weather fields."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return None
        return v

    @property
    def temperature_c(self) -> Optional[float]:
        """Get temperature in Celsius."""
        if self.temp is None:
            return None
        return float(self.temp) if isinstance(self.temp, str) else self.temp

    @property
    def timestamp(self) -> datetime:
        """Get timestamp as datetime."""
        return datetime.fromtimestamp(self.time)


class WeatherResponse(APRSResponseBase):
    """Weather query response."""

    what: Literal["wx"] = "wx"
    found: int = Field(..., description="Number of entries returned")
    entries: list[WeatherEntry] = Field(default_factory=list, description="Weather entries")


class MessageEntry(BaseModel):
    """APRS message entry."""

    messageid: str = Field(..., description="Incrementing message ID")
    time: int = Field(..., description="Unix timestamp when message was received")
    srccall: str = Field(..., description="Source callsign")
    dst: str = Field(..., description="APRS message destination")
    message: str = Field(..., description="Message contents")

    @property
    def timestamp(self) -> datetime:
        """Get timestamp as datetime."""
        return datetime.fromtimestamp(self.time)


class MessageResponse(APRSResponseBase):
    """Message query response."""

    what: Literal["msg"] = "msg"
    found: int = Field(..., description="Number of messages returned")
    entries: list[MessageEntry] = Field(default_factory=list, description="Message entries")


# Union type for all possible responses
APRSResponse = LocationResponse | WeatherResponse | MessageResponse


# APRS Symbol parsing (from APRS spec)

APRS_SYMBOL_TABLES = {
    "/": "Primary",
    "\\": "Alternate",
    "0-9": "Overlay",
    "A-Z": "Overlay",
}

# Common APRS symbols for maritime use
MARITIME_SYMBOLS = {
    "/#": "Digipeater",
    "/s": "Ship (power boat)",
    "/Y": "Yacht (sail boat)",
    "\\s": "Ship (side view)",
    "/v": "Van",
}


def parse_aprs_symbol(symbol: str) -> dict[str, str]:
    """Parse APRS symbol code.

    Args:
        symbol: Two-character APRS symbol (table + code)

    Returns:
        Dictionary with table and code information
    """
    if not symbol or len(symbol) != 2:
        return {"table": "unknown", "code": "unknown", "description": "Unknown"}

    table_char = symbol[0]
    symbol_char = symbol[1]

    table_name = APRS_SYMBOL_TABLES.get(table_char, "Unknown")

    # Check if it's a known maritime symbol
    description = MARITIME_SYMBOLS.get(symbol, f"Symbol {symbol_char}")

    return {
        "table": table_name,
        "code": symbol_char,
        "description": description,
        "raw": symbol,
    }
