# API Specifications

This directory contains OpenAPI specifications for generating client libraries.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   Boston Harbor Ferries                      │
│                  (High-level Ferry Tracker)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│              Generated APRS.fi Client (Python)               │
│           (from specs/aprs-fi-api.yaml via openapi-generator)│
└─────────────────────────────────────────────────────────────┘
                            ↓ calls
┌─────────────────────────────────────────────────────────────┐
│                    APRS.fi HTTP API                          │
│              (https://api.aprs.fi/api)                       │
└─────────────────────────────────────────────────────────────┘
```

## Alternative: Direct APRS-IS Connection (Future)

For real-time streaming instead of polling:

```
┌─────────────────────────────────────────────────────────────┐
│                   Boston Harbor Ferries                      │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│              Python APRS-IS Client Library                   │
│         (Python port of Perl Ham::APRS::IS)                  │
│         - TCP connection to APRS-IS servers                  │
│         - Real-time packet streaming                         │
│         - Filter by geographic area or callsign             │
└─────────────────────────────────────────────────────────────┘
                            ↓ connects to
┌─────────────────────────────────────────────────────────────┐
│                  APRS-IS Network (TCP)                       │
│           (rotate.aprs2.net:14580)                          │
└─────────────────────────────────────────────────────────────┘
```

## Files

### `aprs-fi-api.yaml`
OpenAPI 3.1 specification for the APRS.fi HTTP API. Includes:
- Location/position queries (`/get?what=loc`)
- Weather queries (`/get?what=wx`)
- Message queries (`/get?what=msg`)
- Complete schema definitions with AIS fields
- Authentication (API key)
- Examples from real CRISPUS ATTUCKS data

## Code Generation

### Using OpenAPI Generator

Generate Python client from spec:

```bash
# Install openapi-generator-cli
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i specs/aprs-fi-api.yaml \
  -g python \
  -o generated/aprs-fi-client \
  --additional-properties=packageName=aprs_fi_client,projectName=aprs-fi-client

# Install generated client
cd generated/aprs-fi-client
pip install -e .
```

### Using datamodel-code-generator (Pydantic models only)

Generate just Pydantic models:

```bash
pip install datamodel-code-generator

datamodel-codegen \
  --input specs/aprs-fi-api.yaml \
  --input-file-type openapi \
  --output generated/models.py
```

### Using openapi-python-client

Simpler alternative for Python:

```bash
pip install openapi-python-client

openapi-python-client generate \
  --path specs/aprs-fi-api.yaml \
  --config codegen-config.yaml
```

## Usage After Generation

```python
from aprs_fi_client import ApiClient, Configuration
from aprs_fi_client.api import default_api

# Configure API key
config = Configuration()
config.api_key['apikey'] = 'your-api-key'

# Create client
with ApiClient(config) as api_client:
    api = default_api.DefaultApi(api_client)

    # Query vessel position
    response = api.query_location(
        name="368157410",  # CRISPUS ATTUCKS
        apikey="your-key"
    )

    if response.result == "ok":
        for entry in response.entries:
            print(f"{entry.name}: {entry.lat}, {entry.lng}")
```

## Ham::APRS::IS Python Port

For direct APRS-IS connections (alternative to HTTP API):

### Perl Original
```perl
use Ham::APRS::IS;
my $is = new Ham::APRS::IS(
    'rotate.aprs2.net:14580',
    'N0CALL',
    'filter' => 'r/42.35/-71.05/5'  # 5km radius around Boston
);
$is->connect('pass' => -1) || die;
while (my $line = $is->getline_noncomment()) {
    print "$line\n";
}
```

### Python Port (Proposed)
```python
from aprs_is import APRSISClient

# Connect to APRS-IS
client = APRSISClient(
    server='rotate.aprs2.net:14580',
    callsign='N0CALL',
    passcode=-1,  # Read-only
    filter='r/42.35/-71.05/5'  # 5km radius
)

with client.connect() as stream:
    for packet in stream:
        if packet.type == 'position':
            print(f"{packet.source}: {packet.lat}, {packet.lon}")
```

## Why Two Approaches?

### HTTP API (Current - aprs.fi)
**Pros:**
- Simple HTTP requests
- No persistent connection
- Cached/aggregated data
- Well-documented API
- Rate limiting built-in

**Cons:**
- Polling required (not real-time)
- Dependent on aprs.fi service
- API key required
- Limited to 10 req/min

### APRS-IS Direct (Future)
**Pros:**
- Real-time streaming
- No API key needed
- Direct from source
- Geographic filtering
- Lower latency

**Cons:**
- TCP connection management
- Need to parse APRS packets
- More complex error handling
- No caching/aggregation
- Must implement own rate limiting

## Recommendation

**Current Setup (HTTP API):**
- Best for polling use cases
- Good for web apps/dashboards
- Simpler development
- Good data quality (aprs.fi validates)

**Future APRS-IS:**
- When real-time needed
- For continuous monitoring
- When making custom tools
- Learning APRS protocol

## Testing

Validate spec:

```bash
# Using openapi-generator
openapi-generator-cli validate -i specs/aprs-fi-api.yaml

# Using Redocly
npx @redocly/cli lint specs/aprs-fi-api.yaml

# Using Swagger Editor
# Visit: https://editor.swagger.io
# Load: specs/aprs-fi-api.yaml
```

## References

- [APRS.fi API Documentation](https://aprs.fi/page/api)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Ham::APRS::IS (Perl)](https://metacpan.org/pod/Ham::APRS::IS)
- [APRS-IS Protocol](http://www.aprs-is.net/)
- [APRS Protocol Reference](http://www.aprs.org/doc/APRS101.PDF)
