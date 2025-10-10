# Setup Guide

## Quick Start

### 1. Get API Key

Visit https://aprs.fi and create a free account. Your API key will be in your account settings.

### 2. Set Environment Variable

```bash
export APRS_API_KEY="your-key-from-aprs.fi"
```

### 3. Run with uvx (no installation)

```bash
# From the parent directory (pi-setup)
uvx --from ./boston_harbor_ferries harbor-ferry list-vessels
```

Or from within the package directory:

```bash
cd boston_harbor_ferries
uvx --from . harbor-ferry list-vessels
```

## Testing the Installation

```bash
# List all ferries (no API call needed)
uvx --from ./boston_harbor_ferries harbor-ferry list-vessels

# Show routes (no API call needed)
uvx --from ./boston_harbor_ferries harbor-ferry routes

# Track Crispus Attucks (makes API call)
uvx --from ./boston_harbor_ferries harbor-ferry track 368157410

# Track all ferries (makes API calls)
uvx --from ./boston_harbor_ferries harbor-ferry track-all
```

## Using as MCP Server with Claude Code

### Option 1: Using uvx (recommended)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "boston-harbor-ferries": {
      "command": "uvx",
      "args": [
        "--from",
        "/home/jwalsh/ghq/github.com/aygp-dr/pi-setup/boston_harbor_ferries",
        "harbor-ferry-mcp"
      ],
      "env": {
        "APRS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Option 2: Install locally

```bash
cd boston_harbor_ferries
pip install -e .

# Then use in Claude Desktop config:
{
  "mcpServers": {
    "boston-harbor-ferries": {
      "command": "harbor-ferry-mcp",
      "env": {
        "APRS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Development Setup

```bash
cd boston_harbor_ferries

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv/bin/activate.fish` for fish shell

# Install in editable mode
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env and add your API key

# Test CLI
harbor-ferry list-vessels
harbor-ferry track 368157410

# Test MCP server
harbor-ferry-mcp
```

## Troubleshooting

### "No API key found"

Make sure you've set the `APRS_API_KEY` environment variable:

```bash
export APRS_API_KEY="your-key"
```

Or create a `.env` file in the `boston_harbor_ferries` directory.

### "Unknown vessel MMSI"

Check that you're using a valid MMSI for one of the known ferries:

- 368157410 - CRISPUS ATTUCKS
- 368227350 - PHILLIS WHEATLEY
- 368227370 - SAMUEL WHITTEMORE
- 368351390 - COMMONWEALTH

### "No position data found"

The ferry may not be currently transmitting APRS data. This is normal when:
- Ferry is not in service
- Ferry is outside operating hours (weekdays only, commute hours)
- Ferry's APRS transponder is offline

Try again during weekday commute hours (6:30-9:00 AM or 4:00-7:00 PM ET).

### Rate Limiting

If you see rate limit errors, the cache will prevent excessive requests. Default settings:
- Cache TTL: 2 minutes
- Max requests: 10 per minute

You can clear the cache with:

```bash
harbor-ferry clear-cache
```

## API Terms Compliance

This tool is designed to comply with aprs.fi API terms:

- Each user must have their own API key
- Requests are rate-limited (default 10/min)
- Responses are cached (default 2 min TTL)
- All output credits aprs.fi as the data source
- User-Agent header identifies the application
- No background polling or archival collection
- Free to use for all users

Please respect these terms when using the tool.
