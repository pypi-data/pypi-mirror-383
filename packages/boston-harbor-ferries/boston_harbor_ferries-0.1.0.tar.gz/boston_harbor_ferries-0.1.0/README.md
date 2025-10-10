# Boston Harbor Ferries

[![PyPI version](https://img.shields.io/pypi/v/boston-harbor-ferries.svg)](https://pypi.org/project/boston-harbor-ferries/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![APRS.fi](https://img.shields.io/badge/data-APRS.fi-green.svg)](https://aprs.fi)

APRS-based Boston Harbor commuter ferry tracker with MCP server support.

Tightly scoped to track Seaport Ferry vessels operating in Boston Harbor.

**Data provided by [aprs.fi](https://aprs.fi)** - https://aprs.fi

## Features

- Track all 4 Seaport Ferry vessels in real-time
- Built-in rate limiting and caching (respects aprs.fi API terms)
- Rich CLI with beautiful terminal output
- MCP server for integration with Claude Code and other AI assistants
- Run with `uvx` (no installation required)

## Tracked Vessels

### Seaport Ferry - North Station Route
- **PHILLIS WHEATLEY** (MMSI: 368227350)
- **SAMUEL WHITTEMORE** (MMSI: 368227370)
- **COMMONWEALTH** (MMSI: 368351390)

Route: LoveJoy Wharf (North Station) ↔ Fan Pier (Seaport) ↔ Pier 10
Travel time: ~30 minutes

### Seaport Ferry - East Boston Route
- **CRISPUS ATTUCKS** (MMSI: 368157410)

Route: Lewis Mall Wharf (East Boston) ↔ Fan Pier (Seaport)
Travel time: ~10 minutes

## Installation

### Run with uvx (recommended)

```bash
# Set your API key
export APRS_API_KEY="your-key-from-aprs.fi"

# Run commands directly
uvx --from . harbor-ferry list-vessels
uvx --from . harbor-ferry track 368157410
uvx --from . harbor-ferry track-all
```

### Install in development mode

```bash
cd boston_harbor_ferries
pip install -e .
```

## Configuration

Get your free API key from https://aprs.fi (requires registration).

Set the API key via environment variable:

```bash
export APRS_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```bash
APRS_API_KEY=your-api-key-here
APRS_CACHE_TTL_SECONDS=120
APRS_MAX_REQUESTS_PER_MINUTE=10
```

## CLI Usage

```bash
# List all known ferries
harbor-ferry list-vessels

# Show routes and schedules
harbor-ferry routes

# Track a specific ferry
harbor-ferry track 368157410

# Track all ferries
harbor-ferry track-all

# Force fresh data (bypass cache)
harbor-ferry track 368157410 --no-cache

# Cache management
harbor-ferry cache-info
harbor-ferry clear-cache
```

## MCP Server Usage

The MCP server allows AI assistants like Claude Code to track ferries.

### Start the MCP server:

```bash
harbor-ferry-mcp
```

### Available MCP Tools:

- `list_ferries` - List all known Boston Harbor ferries
- `get_ferry_routes` - Get route information
- `track_ferry` - Track specific ferry by MMSI
- `track_all_ferries` - Get all ferry positions
- `clear_cache` - Clear cached data

### Claude Desktop Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "boston-harbor-ferries": {
      "command": "uvx",
      "args": ["--from", "/path/to/boston_harbor_ferries", "harbor-ferry-mcp"],
      "env": {
        "APRS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Python API

```python
from boston_harbor_ferries import APRSClient, VESSELS

# Initialize client (loads API key from env)
with APRSClient() as client:
    # Track specific ferry
    position = client.get_vessel_position("368157410")
    if position:
        print(f"{position.vessel.name} at {position.latitude}, {position.longitude}")

    # Track all ferries
    positions = client.get_all_ferries()
    for pos in positions:
        print(f"{pos.vessel.name}: {pos.age_seconds:.0f}s old")
```

## API Terms Compliance

This tool complies with aprs.fi API terms of service:

- ✅ Credits aprs.fi as data source in all output
- ✅ Provides link back to aprs.fi
- ✅ Free to use for all users
- ✅ Includes User-Agent header with app name/version
- ✅ Each user uses their own API key
- ✅ Built-in rate limiting (10 req/min default)
- ✅ Intelligent caching (2 min TTL default)
- ✅ Only queries when actively needed (no background polling)

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy boston_harbor_ferries
```

## License

MIT

## Acknowledgments

Data provided by [aprs.fi](https://aprs.fi) - Hessu's excellent APRS infrastructure service.

Ferry service operated by [Seaport Ferry](https://seaportferry.com).
