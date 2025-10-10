# API Schemas and APRS Parser

This document describes the typed schemas and APRS parsing functionality.

## Pydantic Schemas

All API requests and responses use Pydantic models for type safety and validation.

### Location Queries

```python
from boston_harbor_ferries import APRSClient, LocationResponse

with APRSClient() as client:
    # Query single station
    response: LocationResponse = client.query_location("368157410")

    # Query multiple stations (batch query)
    response: LocationResponse = client.query_location("368157410,368227350")

    # Access typed entries
    for entry in response.entries:
        print(f"{entry.name}: {entry.latitude}, {entry.longitude}")
        print(f"Speed: {entry.speed_knots} knots")
        print(f"Timestamp: {entry.timestamp}")
```

### Weather Queries

```python
from boston_harbor_ferries import WeatherResponse

with APRSClient() as client:
    response: WeatherResponse = client.query_weather("OH2TI")

    for entry in response.entries:
        print(f"Temperature: {entry.temperature_c}°C")
        print(f"Pressure: {entry.pressure} mbar")
        print(f"Wind: {entry.wind_speed} m/s from {entry.wind_direction}°")
```

### Message Queries

```python
from boston_harbor_ferries import MessageResponse

with APRSClient() as client:
    response: MessageResponse = client.query_messages("OH2TI")

    for msg in response.entries:
        print(f"From {msg.srccall}: {msg.message}")
        print(f"Received: {msg.timestamp}")
```

## APRS Parser (Ham::APRS::FAP Port)

Python implementation of APRS packet parsing based on the Perl Ham::APRS::FAP library.

### Parse APRS Packets

```python
from boston_harbor_ferries import APRSParser, APRSPosition

parser = APRSParser()

# Parse position report
packet = "N0CALL>APRS,WIDE1-1:!4903.50N/07201.75W-Test comment"
position: APRSPosition = parser.parse_packet(packet)

if position:
    print(f"Source: {position.source}")
    print(f"Position: {position.latitude}, {position.longitude}")
    print(f"Symbol: {position.symbol_table}{position.symbol_code}")
    print(f"Comment: {position.comment}")
```

### Coordinate Conversion

```python
from boston_harbor_ferries.aprs_parser import APRSParser

# Convert DMS to decimal
lat_decimal = APRSParser.dms_to_decimal(42, 21.95, "N")
# Result: 42.36583

# Convert decimal to DMS
degrees, minutes, direction = APRSParser.decimal_to_dms(42.36583, is_latitude=True)
# Result: (42, 21.95, "N")
```

### Distance and Bearing Calculations

```python
from boston_harbor_ferries import calculate_distance, calculate_bearing

# Calculate distance between two points (Haversine formula)
distance_km = calculate_distance(
    lat1=42.3657, lon1=-71.0400,  # Lewis Mall Wharf
    lat2=42.3516, lon2=-71.0438,  # Fan Pier
)
# Result: ~1.7 km

# Calculate bearing from point 1 to point 2
bearing = calculate_bearing(
    lat1=42.3657, lon1=-71.0400,
    lat2=42.3516, lon2=-71.0438,
)
# Result: ~185° (roughly south)
```

## Schema Examples

### LocationEntry Fields

```python
class LocationEntry(BaseModel):
    # Required
    name: str                    # Station name
    type: str                    # a=AIS, l=APRS, i=item, o=object, w=weather
    time: int                    # Unix timestamp (first report)
    lasttime: int                # Unix timestamp (last report)
    lat: str                     # Latitude (decimal degrees)
    lng: str                     # Longitude (decimal degrees)

    # Optional common
    course: Optional[int]        # Course in degrees
    speed: Optional[str]         # Speed in km/h
    altitude: Optional[str]      # Altitude in meters
    symbol: Optional[str]        # APRS symbol code
    comment: Optional[str]       # Comment text

    # Optional AIS
    mmsi: Optional[str]          # AIS MMSI number
    heading: Optional[int]       # Heading in degrees
    length: Optional[int]        # Vessel length (m)
    width: Optional[int]         # Vessel width (m)

    # Computed properties
    @property
    def latitude(self) -> float
    @property
    def longitude(self) -> float
    @property
    def speed_knots(self) -> Optional[float]
    @property
    def timestamp(self) -> datetime
```

### WeatherEntry Fields

```python
class WeatherEntry(BaseModel):
    name: str                       # Station name
    time: int                       # Unix timestamp
    temp: Optional[str]             # Temperature (°C)
    pressure: Optional[str]         # Pressure (mbar)
    humidity: Optional[str]         # Humidity (%)
    wind_direction: Optional[str]   # Wind direction (°)
    wind_speed: Optional[str]       # Wind speed (m/s)
    wind_gust: Optional[str]        # Wind gust (m/s)
    rain_1h: Optional[str]          # Rain 1h (mm)
    rain_24h: Optional[str]         # Rain 24h (mm)
    rain_mn: Optional[str]          # Rain since midnight (mm)
    luminosity: Optional[str]       # Luminosity (W/m²)

    @property
    def temperature_c(self) -> Optional[float]
    @property
    def timestamp(self) -> datetime
```

### MessageEntry Fields

```python
class MessageEntry(BaseModel):
    messageid: str      # Incrementing message ID
    time: int           # Unix timestamp
    srccall: str        # Source callsign
    dst: str            # Destination
    message: str        # Message content

    @property
    def timestamp(self) -> datetime
```

## Type Safety Benefits

1. **Autocomplete**: IDEs provide autocomplete for all fields
2. **Validation**: Pydantic validates data at runtime
3. **Type Checking**: mypy and other tools can verify types
4. **Documentation**: Field descriptions serve as inline docs
5. **Parsing**: Automatic parsing of numeric strings to floats
6. **Conversion**: Helper properties convert between units

## Error Handling

All query methods return typed responses even on error:

```python
response = client.query_location("INVALID")

if response.result == "fail":
    print(f"Error: {response.description}")
else:
    # Safe to access entries
    for entry in response.entries:
        print(entry.name)
```

## Credit

- APRS.fi API documentation: https://aprs.fi/page/api
- Ham::APRS::FAP (Perl): https://metacpan.org/dist/Ham-APRS-FAP
- APRS Protocol Specification: http://www.aprs.org/doc/APRS101.PDF
