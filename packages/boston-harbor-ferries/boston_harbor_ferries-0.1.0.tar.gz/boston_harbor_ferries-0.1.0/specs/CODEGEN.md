# Code Generation Quick Start

## TL;DR

We have OpenAPI specs that can generate the APRS.fi client instead of hand-writing it.

```bash
# Validate spec
gmake codegen-validate

# Generate Python client
gmake codegen

# Clean generated code
gmake codegen-clean
```

## What's in `specs/`

```
specs/
├── aprs-fi-api.yaml      # OpenAPI 3.1 spec for APRS.fi API
├── codegen-config.yaml   # Generator configuration
├── architecture.md       # Detailed architecture docs
└── README.md            # Full documentation
```

## Current Setup (No Changes Needed)

```python
# Current implementation (hand-written)
from boston_harbor_ferries import APRSClient

with APRSClient() as client:
    pos = client.get_vessel_position("368157410")
    print(f"{pos.vessel.name} at {pos.latitude}, {pos.longitude}")
```

This works perfectly! ✅

## Future: Code-Generated Client

```python
# Generated from specs/aprs-fi-api.yaml
from aprs_fi_client import ApiClient, DefaultApi, Configuration

config = Configuration()
config.api_key['apikey'] = 'your-key'

with ApiClient(config) as api_client:
    api = DefaultApi(api_client)
    response = api.query_location(name="368157410")

    for entry in response.entries:
        print(f"{entry.name} at {entry.lat}, {entry.lng}")
```

## Why Use Code Generation?

### Pros
1. **Single Source of Truth**: OpenAPI spec defines the API
2. **Type Safety**: Generated code has full type hints
3. **Auto-Update**: API changes → update spec → regenerate
4. **Multi-Language**: Same spec → Python, TypeScript, Go, etc.
5. **Validation**: Spec ensures correctness

### Cons
1. **More Complex**: Extra build step
2. **Less Control**: Generated code may not be ideal
3. **Dependencies**: Need codegen tools

## When to Use Code Generation?

✅ **Use codegen when:**
- API is large/complex
- Need multiple language clients
- API changes frequently
- Team has multiple developers
- Want guaranteed type safety

❌ **Skip codegen when:**
- Simple API (like ours currently)
- Rapid prototyping
- Single language only
- Stable API
- Small project

## Our Recommendation

**Current (hand-written)**: Keep for now - it's simple and works!

**Future (code-gen)**: Consider when:
1. Adding more APRS.fi endpoints
2. Supporting other languages (TypeScript frontend?)
3. Team grows beyond 1-2 developers
4. API becomes more complex

## Alternative: APRS-IS Direct Connection

See `architecture.md` for Python port of Ham::APRS::IS:

```python
# Future: Real-time streaming
from aprs_is import APRSISClient

with APRSISClient("rotate.aprs2.net:14580", "N0CALL") as client:
    client.set_filter("r/42.35/-71.05/5")  # 5km radius
    for packet in client.stream():
        print(f"{packet.source}: {packet.lat}, {packet.lon}")
```

**Benefits:**
- Real-time (not polling)
- No API key needed
- Lower latency
- Direct from source

**Tradeoffs:**
- More complex (TCP, parsing)
- Must handle reconnection
- No caching/validation

## Tools

### OpenAPI Python Client (Recommended)
```bash
pip install openapi-python-client
gmake codegen
```

### OpenAPI Generator (Alternative)
```bash
npm install -g @openapitools/openapi-generator-cli
openapi-generator-cli generate \
  -i specs/aprs-fi-api.yaml \
  -g python \
  -o generated/aprs-fi-client
```

### Datamodel Code Generator (Models Only)
```bash
pip install datamodel-code-generator
datamodel-codegen \
  --input specs/aprs-fi-api.yaml \
  --input-file-type openapi \
  --output generated/models.py
```

## Verification

Test that CRISPUS ATTUCKS still works:

```bash
uv run python -m boston_harbor_ferries.cli track 368157410
```

Should show real-time ferry position! 🚢

## Next Steps

1. Review `specs/aprs-fi-api.yaml` - the OpenAPI spec
2. Read `specs/architecture.md` - full architecture
3. Try `gmake codegen-validate` - validate spec
4. Decide: stick with hand-written or try codegen?

## Questions?

- OpenAPI: https://swagger.io/specification/
- APRS.fi API: https://aprs.fi/page/api
- Ham::APRS::IS: https://metacpan.org/pod/Ham::APRS::IS
- APRS-IS Protocol: http://www.aprs-is.net/
