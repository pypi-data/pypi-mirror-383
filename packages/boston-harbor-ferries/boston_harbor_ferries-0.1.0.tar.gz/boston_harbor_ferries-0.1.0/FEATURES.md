# Boston Harbor Ferries - Feature Summary

## Overview

Complete APRS-based ferry tracking system for Boston Harbor commuter ferries with:
- ✅ Fully typed Pydantic schemas for all API interactions
- ✅ Python port of Ham::APRS::FAP packet parser
- ✅ Rate limiting and intelligent caching
- ✅ Rich CLI with beautiful terminal output
- ✅ MCP server for AI assistant integration
- ✅ uvx-compatible (run without installation)

## Architecture

```
boston_harbor_ferries/
├── schemas.py           # Pydantic models for API request/response
├── aprs_parser.py       # APRS packet parser (Ham::APRS::FAP port)
├── client.py            # HTTP client with caching & rate limiting
├── vessels.py           # Ferry database (4 vessels, 2 routes)
├── config.py            # Settings from environment
├── cli.py               # Click-based CLI with Rich output
├── mcp_server.py        # MCP server for Claude Code
└── __init__.py          # Public API exports
```

## Typed Schemas

All API interactions use Pydantic models:

### Request Models
- `LocationRequest` - Query vessel positions
- `WeatherRequest` - Query weather data
- `MessageRequest` - Query APRS messages

### Response Models
- `LocationResponse` with `LocationEntry[]`
- `WeatherResponse` with `WeatherEntry[]`
- `MessageResponse` with `MessageEntry[]`

### Benefits
- IDE autocomplete for all fields
- Runtime validation with Pydantic
- Type checking with mypy
- Automatic parsing (strings → floats, timestamps → datetime)
- Helper properties (e.g., `speed_knots`, `temperature_c`)

## APRS Parser

Python implementation of Ham::APRS::FAP functionality:

```python
from boston_harbor_ferries import APRSParser, APRSPosition

parser = APRSParser()
position = parser.parse_packet("N0CALL>APRS:!4903.50N/07201.75W-Test")

# Parsed fields
print(f"Lat/Lon: {position.latitude}, {position.longitude}")
print(f"Speed: {position.speed} km/h")
print(f"Course: {position.course}°")
```

Features:
- Parse APRS position packets (uncompressed format)
- Parse status messages
- DMS ↔ Decimal degree conversion
- Distance calculation (Haversine)
- Bearing calculation

## API Client

Three query methods with typed responses:

```python
from boston_harbor_ferries import APRSClient

with APRSClient() as client:
    # Location queries
    loc_response = client.query_location("368157410")

    # Weather queries
    wx_response = client.query_weather("OH2TI")

    # Message queries
    msg_response = client.query_messages("OH2TI")
```

Features:
- Automatic rate limiting (10 req/min default)
- Disk-based caching (2 min TTL default)
- Batch queries (up to 20 stations)
- Proper User-Agent header
- Error handling with typed responses

## CLI Commands

```bash
# Vessel management
harbor-ferry list-vessels        # List all 4 ferries
harbor-ferry routes              # Show route information

# Tracking
harbor-ferry track 368157410     # Track specific ferry
harbor-ferry track-all           # Track all ferries
harbor-ferry track --no-cache    # Force fresh API data

# Cache management
harbor-ferry cache-info          # Show cache stats
harbor-ferry clear-cache         # Clear cached data
```

## MCP Server

Five tools for AI assistants:

1. `list_ferries` - Get vessel database
2. `get_ferry_routes` - Get route information
3. `track_ferry` - Track by MMSI
4. `track_all_ferries` - Track all vessels
5. `clear_cache` - Clear cached data

Integration with Claude Code:

```json
{
  "mcpServers": {
    "boston-harbor-ferries": {
      "command": "uvx",
      "args": ["--from", "boston_harbor_ferries", "harbor-ferry-mcp"],
      "env": {"APRS_API_KEY": "your-key"}
    }
  }
}
```

## Tracked Vessels

### North Station Route (3 vessels)
- PHILLIS WHEATLEY (368227350)
- SAMUEL WHITTEMORE (368227370)
- COMMONWEALTH (368351390)

Route: LoveJoy Wharf → Fan Pier → Pier 10 (~30 min)

### East Boston Route (1 vessel)
- CRISPUS ATTUCKS (368157410)

Route: Lewis Mall Wharf ↔ Fan Pier (~10 min)

## API Compliance

Fully compliant with aprs.fi API terms:

- ✅ Credits aprs.fi in all output
- ✅ Links back to https://aprs.fi
- ✅ Free to use for all users
- ✅ Each user has own API key
- ✅ Rate limited (configurable)
- ✅ Intelligent caching
- ✅ User-Agent header with app info
- ✅ No background polling
- ✅ No data harvesting

## Python API

### High-level ferry tracking:

```python
from boston_harbor_ferries import APRSClient, VESSELS

with APRSClient() as client:
    # Track Crispus Attucks
    pos = client.get_vessel_position("368157410")
    print(f"{pos.vessel.name}: {pos.latitude}, {pos.longitude}")

    # Track all ferries
    for ferry in client.get_all_ferries():
        print(f"{ferry.vessel.name}: {ferry.age_seconds:.0f}s old")
```

### Low-level typed queries:

```python
from boston_harbor_ferries import APRSClient, LocationResponse

with APRSClient() as client:
    # Batch query multiple vessels
    response: LocationResponse = client.query_location(
        "368157410,368227350,368227370"
    )

    for entry in response.entries:
        print(f"{entry.name} @ {entry.speed_knots} knots")
```

## Utilities

Helper functions for APRS work:

```python
from boston_harbor_ferries import calculate_distance, calculate_bearing

# Distance between two points
dist_km = calculate_distance(42.3657, -71.0400, 42.3516, -71.0438)

# Bearing from point A to point B
bearing = calculate_bearing(42.3657, -71.0400, 42.3516, -71.0438)
```

## Configuration

Environment variables (or `.env` file):

```bash
APRS_API_KEY=your-api-key-from-aprs.fi
APRS_CACHE_TTL_SECONDS=120              # Default: 2 minutes
APRS_MAX_REQUESTS_PER_MINUTE=10         # Default: 10
APRS_CACHE_DIR=/tmp/ferry-cache         # Optional
```

## Development

```bash
# Install in dev mode
cd boston_harbor_ferries
pip install -e ".[dev]"

# Run tests (when implemented)
pytest

# Type checking
mypy boston_harbor_ferries

# Format code
black boston_harbor_ferries
```

## Future Enhancements

Possible additions:
- [ ] Async client with asyncio/httpx
- [ ] WebSocket support for real-time updates
- [ ] Historical position tracking
- [ ] Route prediction
- [ ] Arrival time estimation
- [ ] TUI dashboard with live updates
- [ ] Notification system (alerts)
- [ ] Integration with AIS data
- [ ] Vessel comparison tools
- [ ] Geographic visualization

## Credits

- **APRS.fi**: Hessu's excellent APRS infrastructure - https://aprs.fi
- **Ham::APRS::FAP**: Original Perl APRS parser - https://metacpan.org/dist/Ham-APRS-FAP
- **Seaport Ferry**: Boston Harbor ferry operator - https://seaportferry.com

## License

MIT
