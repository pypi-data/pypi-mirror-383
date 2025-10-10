"""Boston Harbor ferry vessel database."""

from typing import Literal
from pydantic import BaseModel


class Route(BaseModel):
    """Ferry route definition."""

    name: str
    stops: list[str]
    travel_time_minutes: int


class Vessel(BaseModel):
    """Ferry vessel information."""

    name: str
    mmsi: str
    route: str
    operator: Literal["Seaport Ferry", "MBTA"]
    capacity: int | None = None
    description: str | None = None


# Seaport Ferry routes
NORTH_STATION_ROUTE = Route(
    name="North Station Route",
    stops=["LoveJoy Wharf (North Station)", "Fan Pier (Seaport)", "Pier 10"],
    travel_time_minutes=30,
)

EAST_BOSTON_ROUTE = Route(
    name="East Boston Route",
    stops=["Lewis Mall Wharf (East Boston)", "Fan Pier (Seaport)"],
    travel_time_minutes=10,
)

# Known Boston Harbor commuter ferries
VESSELS: dict[str, Vessel] = {
    # Seaport Ferry - North Station Route
    "368227350": Vessel(
        name="PHILLIS WHEATLEY",
        mmsi="368227350",
        route="North Station Route",
        operator="Seaport Ferry",
        capacity=90,
        description="North Station to Fan Pier to Pier 10",
    ),
    "368227370": Vessel(
        name="SAMUEL WHITTEMORE",
        mmsi="368227370",
        route="North Station Route",
        operator="Seaport Ferry",
        capacity=90,
        description="North Station to Fan Pier to Pier 10",
    ),
    "368351390": Vessel(
        name="COMMONWEALTH",
        mmsi="368351390",
        route="North Station Route",
        operator="Seaport Ferry",
        capacity=90,
        description="North Station to Fan Pier to Pier 10",
    ),
    # Seaport Ferry - East Boston Route
    "368157410": Vessel(
        name="CRISPUS ATTUCKS",
        mmsi="368157410",
        route="East Boston Route",
        operator="Seaport Ferry",
        capacity=90,
        description="East Boston to Fan Pier",
    ),
}

# Key locations in Boston Harbor
LOCATIONS = {
    "lovejoy_wharf": {"lat": 42.3659, "lon": -71.0610, "name": "LoveJoy Wharf (North Station)"},
    "fan_pier": {"lat": 42.3516, "lon": -71.0438, "name": "Fan Pier (Seaport)"},
    "pier_10": {"lat": 42.3526, "lon": -71.0324, "name": "Pier 10"},
    "lewis_mall": {"lat": 42.3657, "lon": -71.0400, "name": "Lewis Mall Wharf (East Boston)"},
}

ROUTES = {
    "North Station Route": NORTH_STATION_ROUTE,
    "East Boston Route": EAST_BOSTON_ROUTE,
}
