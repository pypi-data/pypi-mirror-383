# Boston Harbor Ferries Architecture

## Current Implementation

```
┌──────────────────────────────────────────────────────────────┐
│                    CLI Application                            │
│              (boston_harbor_ferries/cli.py)                   │
│                                                               │
│  Commands:                                                    │
│  - track <mmsi>    : Track specific ferry                     │
│  - track-all       : Track all ferries                        │
│  - list-vessels    : Show known ferries                       │
│  - test-api        : Verify configuration                     │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   Hand-Written Client                         │
│              (boston_harbor_ferries/client.py)                │
│                                                               │
│  - APRSClient: HTTP client with rate limiting                 │
│  - FerryPosition: Position data model                         │
│  - In-memory caching with TTL                                 │
│  - User-Agent header management                               │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                  Pydantic Schemas                             │
│              (boston_harbor_ferries/schemas.py)               │
│                                                               │
│  - LocationRequest/Response                                   │
│  - WeatherRequest/Response                                    │
│  - MessageRequest/Response                                    │
│  - Field validators for type coercion                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    APRS.fi HTTP API                           │
│              https://api.aprs.fi/api                          │
└──────────────────────────────────────────────────────────────┘
```

## Proposed: Code-Generated Client

```
┌──────────────────────────────────────────────────────────────┐
│                    CLI Application                            │
│              (boston_harbor_ferries/cli.py)                   │
│                      [NO CHANGES]                             │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   Adapter Layer (New)                         │
│         (boston_harbor_ferries/adapters/aprs_fi.py)           │
│                                                               │
│  Purpose: Bridge between our domain models and generated      │
│           client                                              │
│                                                               │
│  class APRSFiAdapter:                                         │
│      def __init__(self, api_client: GeneratedClient):        │
│          self.client = api_client                             │
│                                                               │
│      def get_vessel_position(mmsi) -> FerryPosition:          │
│          response = self.client.query_location(name=mmsi)     │
│          return self._convert_to_ferry_position(response)     │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│              Generated Client Library                         │
│           (generated/aprs-fi-client/)                         │
│                                                               │
│  Generated from: specs/aprs-fi-api.yaml                       │
│                                                               │
│  Provides:                                                    │
│  - ApiClient: Base HTTP client                                │
│  - Configuration: API key, headers                            │
│  - DefaultApi: API methods (query_location, query_weather)    │
│  - Models: Auto-generated from OpenAPI schemas                │
│  - Validation: Built-in type checking                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    APRS.fi HTTP API                           │
│              https://api.aprs.fi/api                          │
└──────────────────────────────────────────────────────────────┘
```

## Benefits of Code Generation

### 1. **Correctness**
- OpenAPI spec is the single source of truth
- Generated code matches API exactly
- Type safety from spec to code

### 2. **Maintainability**
- API changes → update spec → regenerate
- No manual schema updates
- Consistent error handling

### 3. **Documentation**
- Spec serves as API documentation
- Can generate API docs (ReDoc, Swagger UI)
- Examples embedded in spec

### 4. **Multi-Language Support**
- Same spec → generate clients in any language
- TypeScript for web frontend
- Go for high-performance services
- Rust for embedded systems

## Migration Path

### Phase 1: Generate Alongside (Current)
```
boston_harbor_ferries/
├── client.py              # Hand-written (current)
├── schemas.py             # Hand-written (current)
└── adapters/
    └── aprs_fi.py        # New: uses generated client
```

### Phase 2: Test Generated Client
```bash
# Generate client
gmake codegen

# Test alongside existing
python -c "
from boston_harbor_ferries.adapters.aprs_fi import APRSFiAdapter
adapter = APRSFiAdapter()
pos = adapter.get_vessel_position('368157410')
print(pos)
"
```

### Phase 3: Full Migration (Future)
```
boston_harbor_ferries/
├── cli.py                 # Updated to use adapter
├── adapters/
│   └── aprs_fi.py        # Uses generated client
├── models.py              # Domain models (FerryPosition, etc)
└── [generated removed]    # Old client.py, schemas.py removed
```

## Ham::APRS::IS Python Port

For real-time APRS-IS connections (alternative architecture):

```
┌──────────────────────────────────────────────────────────────┐
│                    CLI Application                            │
│  New commands:                                                │
│  - stream [--filter FILTER]  : Real-time stream               │
│  - listen [--area LAT,LON,R] : Geographic filter              │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                Python APRS-IS Client                          │
│           (aprs_is/client.py - to be implemented)             │
│                                                               │
│  Based on Ham::APRS::IS concepts:                             │
│  - TCP connection to APRS-IS servers                          │
│  - Authentication (callsign + passcode)                       │
│  - Server-side filtering                                      │
│  - Packet parsing                                             │
│  - Automatic reconnection                                     │
│                                                               │
│  class APRSISClient:                                          │
│      def connect(server, callsign, filter): ...               │
│      def stream_packets(): ...  # Generator                   │
│      def parse_packet(line): ...                              │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                  APRS Packet Parser                           │
│           (aprs_is/parser.py - to be implemented)             │
│                                                               │
│  Parse APRS packet formats:                                   │
│  - Position packets                                           │
│  - AIS position reports (our use case)                        │
│  - Weather packets                                            │
│  - Messages                                                   │
│  - Telemetry                                                  │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                  APRS-IS Network (TCP)                        │
│              rotate.aprs2.net:14580                           │
│                                                               │
│  Features:                                                    │
│  - Full-feed APRS data                                        │
│  - Server-side filtering                                      │
│  - No API key needed (callsign + passcode)                    │
│  - Real-time updates                                          │
└──────────────────────────────────────────────────────────────┘
```

### APRS-IS Filter Examples

```python
# Geographic area (5km radius around Boston Harbor)
filter = "r/42.35/-71.05/5"

# Specific callsigns/MMSI
filter = "b/WDL7133"  # CRISPUS ATTUCKS

# Multiple filters (OR)
filter = "r/42.35/-71.05/5 b/WDL7133 b/WDL7138"

# Type filter (only AIS)
filter = "t/a"  # AIS only
```

## Comparison

| Feature | APRS.fi HTTP | APRS-IS Direct |
|---------|--------------|----------------|
| **Latency** | ~30s (polling) | <1s (streaming) |
| **Auth** | API key required | Callsign + passcode |
| **Connection** | Stateless HTTP | Persistent TCP |
| **Caching** | Built-in at aprs.fi | Must implement |
| **Rate Limit** | 10 req/min | No limit (streaming) |
| **Data Quality** | Validated/cleaned | Raw packets |
| **Complexity** | Low | Medium |
| **Dependencies** | httpx, pydantic | socket, async |
| **Best For** | Dashboards, polling | Real-time, monitoring |

## Recommended Stack

### Current: HTTP API (Good for MVP)
```python
# Simple, works now
from boston_harbor_ferries import APRSClient

with APRSClient() as client:
    pos = client.get_vessel_position("368157410")
```

### Future: Code-Generated (Better Maintainability)
```python
# Generated from spec
from aprs_fi_client import ApiClient, DefaultApi

with ApiClient(config) as client:
    api = DefaultApi(client)
    response = api.query_location(name="368157410")
```

### Advanced: APRS-IS Streaming (Real-Time)
```python
# Direct APRS-IS connection
from aprs_is import APRSISClient

with APRSISClient("rotate.aprs2.net:14580", "N0CALL") as client:
    client.set_filter("r/42.35/-71.05/5")
    for packet in client.stream():
        if packet.source_mmsi == "368157410":
            print(f"Ferry at: {packet.lat}, {packet.lon}")
```

## Directory Structure (Proposed)

```
boston-harbor-ferries/
├── boston_harbor_ferries/      # Main package
│   ├── cli.py                  # CLI commands
│   ├── models.py               # Domain models (FerryPosition, Vessel)
│   ├── vessels.py              # Ferry database
│   ├── config.py               # Settings
│   └── adapters/               # Adapter pattern
│       ├── aprs_fi.py         # APRS.fi HTTP adapter
│       └── aprs_is.py         # APRS-IS stream adapter (future)
│
├── specs/                      # API specifications
│   ├── aprs-fi-api.yaml       # OpenAPI spec
│   ├── codegen-config.yaml    # Generator config
│   ├── README.md              # Spec documentation
│   └── architecture.md        # This file
│
├── generated/                  # Code-generated clients
│   ├── aprs-fi-client/        # From OpenAPI spec
│   │   ├── aprs_fi_client/
│   │   ├── setup.py
│   │   └── README.md
│   └── .gitignore             # Don't commit generated code
│
├── aprs_is/                    # Python APRS-IS library (future)
│   ├── client.py              # APRS-IS TCP client
│   ├── parser.py              # Packet parser
│   ├── filters.py             # Filter expressions
│   └── models.py              # Packet models
│
├── tests/
│   ├── test_adapters.py       # Adapter tests
│   ├── test_models.py         # Model tests
│   └── fixtures/              # Test data
│
├── Makefile                    # Build targets
└── README.md                   # User documentation
```

## Next Steps

1. ✅ Create OpenAPI spec (`specs/aprs-fi-api.yaml`)
2. ✅ Document architecture
3. ⬜ Add `gmake codegen` target
4. ⬜ Create adapter layer
5. ⬜ Test generated client alongside current
6. ⬜ Design APRS-IS Python library
7. ⬜ Implement streaming support
