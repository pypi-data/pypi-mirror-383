"""APRS packet parser - Python port of Ham::APRS::FAP functionality.

This module provides basic APRS packet parsing capabilities inspired by
the Perl Ham::APRS::FAP library (https://metacpan.org/dist/Ham-APRS-FAP).

Note: This is a simplified implementation focused on the most common
APRS packet types used in maritime tracking (position reports).
"""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class APRSPosition(BaseModel):
    """Parsed APRS position report."""

    # Source information
    source: str = Field(..., description="Source callsign")
    destination: str = Field(..., description="Destination callsign")
    path: list[str] = Field(default_factory=list, description="Digipeater path")

    # Position data
    latitude: Optional[float] = Field(None, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, description="Longitude in decimal degrees")
    altitude: Optional[float] = Field(None, description="Altitude in meters")

    # Symbol and type
    symbol_table: Optional[str] = Field(None, description="APRS symbol table")
    symbol_code: Optional[str] = Field(None, description="APRS symbol code")
    packet_type: str = Field(..., description="Type of APRS packet")

    # Movement data
    course: Optional[int] = Field(None, description="Course in degrees")
    speed: Optional[float] = Field(None, description="Speed in km/h")

    # Status and comment
    comment: Optional[str] = Field(None, description="APRS comment")
    status: Optional[str] = Field(None, description="Status text")

    # Timestamp
    timestamp: Optional[datetime] = Field(None, description="Packet timestamp")

    # Radio metadata
    phg: Optional[str] = Field(None, description="PHG (Power-Height-Gain)")
    frequency: Optional[float] = Field(None, description="Frequency in MHz")

    # Raw data
    raw_packet: str = Field(..., description="Original raw packet")


class APRSParser:
    """Parse APRS packets into structured data.

    Based on APRS 1.01 specification and Ham::APRS::FAP Perl module.
    """

    # APRS data type identifiers
    DATA_TYPE_POSITION = "!"  # Position without timestamp (no messaging)
    DATA_TYPE_POSITION_MSG = "="  # Position without timestamp (with messaging)
    DATA_TYPE_POSITION_TS = "/"  # Position with timestamp (no messaging)
    DATA_TYPE_POSITION_TS_MSG = "@"  # Position with timestamp (with messaging)
    DATA_TYPE_STATUS = ">"  # Status report
    DATA_TYPE_MESSAGE = ":"  # Message
    DATA_TYPE_OBJECT = ";"  # Object
    DATA_TYPE_ITEM = ")"  # Item

    # Regex patterns
    PACKET_PATTERN = re.compile(
        r"^([A-Z0-9-]+)>([A-Z0-9-]+)(?:,([^:]+))?:(.+)$"
    )

    # Position patterns (compressed and uncompressed)
    # Uncompressed: !DDMM.MMN/DDDMM.MME$
    UNCOMPRESSED_LAT = re.compile(r"(\d{2})(\d{2}\.\d{2})([NS])")
    UNCOMPRESSED_LON = re.compile(r"(\d{3})(\d{2}\.\d{2})([EW])")

    @staticmethod
    def parse_packet(packet: str) -> Optional[APRSPosition]:
        """Parse an APRS packet string.

        Args:
            packet: Raw APRS packet (AX.25 UI frame format)

        Returns:
            APRSPosition object if parsing succeeds, None otherwise

        Example:
            >>> parser = APRSParser()
            >>> pos = parser.parse_packet("N0CALL>APRS,WIDE1-1:!4903.50N/07201.75W-Test")
        """
        match = APRSParser.PACKET_PATTERN.match(packet)
        if not match:
            return None

        source = match.group(1)
        destination = match.group(2)
        path_str = match.group(3) or ""
        payload = match.group(4)

        path = [p.strip() for p in path_str.split(",") if p.strip()]

        # Extract data type identifier
        if not payload:
            return None

        data_type = payload[0]
        data = payload[1:]

        # Parse based on data type
        if data_type in (
            APRSParser.DATA_TYPE_POSITION,
            APRSParser.DATA_TYPE_POSITION_MSG,
            APRSParser.DATA_TYPE_POSITION_TS,
            APRSParser.DATA_TYPE_POSITION_TS_MSG,
        ):
            return APRSParser._parse_position(
                source, destination, path, data_type, data, packet
            )
        elif data_type == APRSParser.DATA_TYPE_STATUS:
            return APRSParser._parse_status(
                source, destination, path, data, packet
            )

        # Unsupported packet type
        return APRSPosition(
            source=source,
            destination=destination,
            path=path,
            packet_type="unknown",
            raw_packet=packet,
        )

    @staticmethod
    def _parse_position(
        source: str,
        destination: str,
        path: list[str],
        data_type: str,
        data: str,
        raw_packet: str,
    ) -> Optional[APRSPosition]:
        """Parse position report packet."""
        timestamp = None
        offset = 0

        # Check if packet has timestamp
        if data_type in (
            APRSParser.DATA_TYPE_POSITION_TS,
            APRSParser.DATA_TYPE_POSITION_TS_MSG,
        ):
            # Parse timestamp (7 characters: DHMz or HMSz)
            if len(data) >= 7:
                ts_str = data[:7]
                # TODO: Parse timestamp properly
                offset = 7

        # Position should be at offset
        if len(data) < offset + 19:  # Minimum for uncompressed position
            return None

        pos_data = data[offset:]

        # Try to parse uncompressed position
        # Format: DDMM.MMN/DDDMM.MME$ where $ is symbol table/code
        lat_match = APRSParser.UNCOMPRESSED_LAT.search(pos_data[:9])
        if not lat_match:
            return None

        lon_start = 9
        if len(pos_data) > lon_start:
            # Symbol table is at position 8 (between lat and lon)
            symbol_table = pos_data[8] if len(pos_data) > 8 else None

            lon_match = APRSParser.UNCOMPRESSED_LON.search(pos_data[lon_start : lon_start + 10])
            if not lon_match:
                return None

            # Parse latitude
            lat_deg = int(lat_match.group(1))
            lat_min = float(lat_match.group(2))
            lat_ns = lat_match.group(3)
            latitude = lat_deg + (lat_min / 60.0)
            if lat_ns == "S":
                latitude = -latitude

            # Parse longitude
            lon_deg = int(lon_match.group(1))
            lon_min = float(lon_match.group(2))
            lon_ew = lon_match.group(3)
            longitude = lon_deg + (lon_min / 60.0)
            if lon_ew == "W":
                longitude = -longitude

            # Symbol code is after longitude
            symbol_code = pos_data[lon_start + 10] if len(pos_data) > lon_start + 10 else None

            # Comment/status starts after symbol
            comment_start = lon_start + 11
            comment = pos_data[comment_start:].strip() if len(pos_data) > comment_start else None

            # Parse course/speed if present in comment
            course, speed = APRSParser._parse_course_speed(comment)

            return APRSPosition(
                source=source,
                destination=destination,
                path=path,
                latitude=latitude,
                longitude=longitude,
                symbol_table=symbol_table,
                symbol_code=symbol_code,
                packet_type="position",
                course=course,
                speed=speed,
                comment=comment,
                timestamp=timestamp,
                raw_packet=raw_packet,
            )

        return None

    @staticmethod
    def _parse_status(
        source: str,
        destination: str,
        path: list[str],
        data: str,
        raw_packet: str,
    ) -> APRSPosition:
        """Parse status report packet."""
        return APRSPosition(
            source=source,
            destination=destination,
            path=path,
            packet_type="status",
            status=data,
            raw_packet=raw_packet,
        )

    @staticmethod
    def _parse_course_speed(comment: Optional[str]) -> tuple[Optional[int], Optional[float]]:
        """Extract course and speed from comment if present.

        Format: CSE/SPD where CSE is 3 digits (degrees) and SPD is 3 digits (knots)
        Example: "090/036" = course 90°, speed 36 knots
        """
        if not comment:
            return None, None

        course_speed_pattern = re.compile(r"(\d{3})/(\d{3})")
        match = course_speed_pattern.search(comment)
        if match:
            course = int(match.group(1))
            speed_knots = int(match.group(2))
            speed_kmh = speed_knots * 1.852  # Convert knots to km/h
            return course, speed_kmh

        return None, None

    @staticmethod
    def dms_to_decimal(degrees: int, minutes: float, direction: str) -> float:
        """Convert degrees/minutes/direction to decimal degrees.

        Args:
            degrees: Degrees (0-180)
            minutes: Minutes (0.00-59.99)
            direction: N/S for latitude, E/W for longitude

        Returns:
            Decimal degrees (negative for S/W)
        """
        decimal = degrees + (minutes / 60.0)
        if direction in ("S", "W"):
            decimal = -decimal
        return decimal

    @staticmethod
    def decimal_to_dms(
        decimal: float, is_latitude: bool = True
    ) -> tuple[int, float, str]:
        """Convert decimal degrees to degrees/minutes/direction.

        Args:
            decimal: Decimal degrees
            is_latitude: True for latitude (N/S), False for longitude (E/W)

        Returns:
            Tuple of (degrees, minutes, direction)
        """
        is_negative = decimal < 0
        decimal = abs(decimal)

        degrees = int(decimal)
        minutes = (decimal - degrees) * 60.0

        if is_latitude:
            direction = "S" if is_negative else "N"
        else:
            direction = "W" if is_negative else "E"

        return degrees, minutes, direction


# Utility functions for working with APRS data

def format_aprs_position(
    latitude: float,
    longitude: float,
    symbol_table: str = "/",
    symbol_code: str = "-",
    comment: str = "",
) -> str:
    """Format a position as an APRS position string.

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        symbol_table: APRS symbol table character
        symbol_code: APRS symbol code character
        comment: Optional comment

    Returns:
        APRS position string (without data type identifier)
    """
    lat_deg, lat_min, lat_dir = APRSParser.decimal_to_dms(latitude, is_latitude=True)
    lon_deg, lon_min, lon_dir = APRSParser.decimal_to_dms(longitude, is_latitude=False)

    pos_str = f"{lat_deg:02d}{lat_min:05.2f}{lat_dir}{symbol_table}"
    pos_str += f"{lon_deg:03d}{lon_min:05.2f}{lon_dir}{symbol_code}"

    if comment:
        pos_str += comment

    return pos_str


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great circle distance between two points using haversine formula.

    Args:
        lat1: First point latitude
        lon1: First point longitude
        lat2: Second point latitude
        lon2: Second point longitude

    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate initial bearing from point 1 to point 2.

    Args:
        lat1: First point latitude
        lon1: First point longitude
        lat2: Second point latitude
        lon2: Second point longitude

    Returns:
        Bearing in degrees (0-360)
    """
    from math import radians, degrees, sin, cos, atan2

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1

    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    bearing = degrees(atan2(y, x))
    return (bearing + 360) % 360
