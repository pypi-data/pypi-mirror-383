"""Boston Harbor commuter ferry tracker using APRS.fi API."""

__version__ = "0.1.0"

from .vessels import VESSELS, Vessel, Route
from .client import APRSClient, FerryPosition
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
from .aprs_parser import APRSParser, APRSPosition, calculate_distance, calculate_bearing

__all__ = [
    # Vessel database
    "VESSELS",
    "Vessel",
    "Route",
    # Client
    "APRSClient",
    "FerryPosition",
    # Schemas
    "LocationRequest",
    "LocationResponse",
    "LocationEntry",
    "WeatherRequest",
    "WeatherResponse",
    "WeatherEntry",
    "MessageRequest",
    "MessageResponse",
    # Parser
    "APRSParser",
    "APRSPosition",
    "calculate_distance",
    "calculate_bearing",
]
