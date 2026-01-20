# Swiss AI MCP Commons

Shared infrastructure and data models for Swiss AI Model Context Protocol (MCP) servers.

**Version:** 1.0.0
**License:** MIT
**Status:** Production Ready

## Overview

`swiss-ai-mcp-commons` is a Python package providing standardized components for Swiss travel and tourism MCPs:

- **Data Models**: Standardized Pydantic models for locations, weather, pricing, and time
- **HTTP Client**: Async HTTP client with caching, retries, and structured logging
- **Validation**: Input validation utilities for dates, currencies, Swiss regions, and more
- **Error Handling**: Standard exception hierarchy with JSON-RPC error codes
- **Logging**: Structured logging configuration with JSON output support

## Features

### Standardized Data Models

```python
from swiss_ai_mcp_commons import Location, Coordinates, Weather, Price

# Geographic location
location = Location(
    name="Bern",
    coordinates=Coordinates(latitude=46.947, longitude=7.447),
    region=Region(canton="BE"),
)

# Weather data
weather = Weather(
    timestamp=datetime.now(),
    description="Sunny",
    temperature=Temperature(value=15.2, min=8.5, max=19.3),
    humidity_percent=65,
)

# Pricing information
price = Price(amount=125.50, currency="CHF")
```

### HTTP Client with Caching

```python
from swiss_ai_mcp_commons import CachedHttpClient

async with CachedHttpClient(
    base_url="https://api.example.com",
    cache_ttl_seconds=120,
) as client:
    # Automatically cached for 120 seconds
    data = await client.get("/v1/endpoint", params={"key": "value"})

    # Retries with exponential backoff on server errors
    data = await client.post("/v1/create", json={"data": "value"})
```

### Input Validation

```python
from swiss_ai_mcp_commons import (
    validate_date_range,
    validate_currency_code,
    validate_swiss_canton,
)

# Date range validation
start = date(2024, 7, 15)
end = date(2024, 7, 22)
validate_date_range(start, end, min_days=1, max_days=365)

# Currency code validation
currency = validate_currency_code("CHF")  # "CHF"

# Swiss canton validation
canton = validate_swiss_canton("be")  # "BE"
```

### Structured Logging

```python
from swiss_ai_mcp_commons import configure_logging, get_logger

# Configure logging
configure_logging(
    app_name="my-app",
    version="1.0.0",
    json_output=True,
)

# Get logger
logger = get_logger(__name__)
logger.info("event_name", key="value", number=42)
# Output: {"timestamp": "2024-01-20T14:30:00Z", "level": "info", "event": "event_name", "key": "value", "number": 42}
```

### Error Handling

```python
from swiss_ai_mcp_commons import (
    StandardMcpException,
    ValidationError,
    ApiError,
    ConfigurationError,
)

# Validation error
try:
    validate_date_range(invalid_start, invalid_end)
except ValidationError as e:
    error_dict = e.to_dict()  # {"code": -32001, "message": "...", "data": {...}}

# API error
try:
    await client.get("/endpoint")
except ApiError as e:
    print(f"API {e.details['api']} failed: {e.message}")

# Configuration error
if not os.environ.get("API_KEY"):
    raise ConfigurationError(
        "Missing required API key",
        config_key="API_KEY"
    )
```

## Installation

### From PyPI (when published)

```bash
pip install swiss-ai-mcp-commons
```

### From local development

```bash
# Clone repository
git clone https://github.com/your-org/swiss-ai-mcp-commons.git
cd swiss-ai-mcp-commons

# Install with development dependencies
pip install -e ".[dev]"

# Or using uv
uv sync
```

## Usage in MCPs

### Example: Weather MCP

```python
from fastmcp import FastMCP
from swiss_ai_mcp_commons import (
    configure_logging,
    CachedHttpClient,
    Weather,
    Location,
)

configure_logging(app_name="open-meteo-mcp", version="2.1.0")
mcp = FastMCP("Open-Meteo Weather")

@mcp.tool()
async def get_weather(location: Location) -> Weather:
    """Get current weather for a location."""
    async with CachedHttpClient(base_url="https://api.open-meteo.com") as client:
        data = await client.get(
            "/v1/forecast",
            params={
                "latitude": location.coordinates.latitude,
                "longitude": location.coordinates.longitude,
            }
        )
        return Weather(
            timestamp=datetime.now(),
            description=data["current"]["weather"],
            temperature=Temperature(value=data["current"]["temperature"]),
        )
```

### Example: Journey MCP

```python
from swiss_ai_mcp_commons import (
    validate_date_range,
    DateRange,
    StandardMcpException,
)

@mcp.tool()
def plan_journey(start_date: str, end_date: str) -> dict:
    """Plan a journey with date validation."""
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        validate_date_range(start, end, min_days=1, max_days=365)

        date_range = DateRange(start_date=start, end_date=end)
        # ... rest of journey planning logic
        return {"duration_days": date_range.days}
    except ValidationError as e:
        raise StandardMcpException(e.message, code=e.code)
```

## Data Models

### Location Models

- **Coordinates**: Geographic coordinates with validation (-90 to 90 latitude, -180 to 180 longitude)
- **Region**: Swiss canton and district information
- **Location**: Complete location with coordinates, region, and metadata

### Weather Models

- **Temperature**: Temperature with min/max and apparent temperature
- **SnowConditions**: Snow depth, fresh snow, avalanche risk, quality
- **AirQuality**: Air Quality Index with pollutant levels and pollen data
- **Weather**: Comprehensive weather with all above plus wind, humidity, precipitation

### Pricing Models

- **Price**: Single price with currency
- **FareOption**: Fare class, restrictions, baggage, discounts
- **PricingInfo**: Standard vs discounted pricing with fare options

### Time Models

- **TimeRange**: Time range with validation
- **DateRange**: Date range with properties (days, is_past, is_future, is_current)

## Validation Utilities

- `validate_date_range()`: Date range validation with min/max days
- `validate_currency_code()`: ISO 4217 currency code validation
- `validate_swiss_canton()`: Swiss canton code validation (2-letter codes)
- `validate_email()`: Email address validation
- `validate_phone()`: Phone number validation (Swiss format)
- `validate_price()`: Price amount validation with min/max range

## Exception Hierarchy

All exceptions inherit from `StandardMcpException` with JSON-RPC error codes:

- **ValidationError** (-32001): Input validation failed
- **ApiError** (-32006): External API call failed
- **ConfigurationError** (-32009): Configuration issue
- **AuthenticationError** (-32002): Authentication failed
- **RateLimitError** (-32007): Rate limit exceeded
- **TimeoutError** (-32008): Operation timed out

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=swiss_ai_mcp_commons

# Run specific test file
uv run pytest tests/test_models.py

# Run with verbose output
uv run pytest -v
```

## Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# All checks
uv run black src/ tests/ && uv run ruff check src/ tests/ && uv run mypy src/
```

## Architecture

### Project Structure

```
swiss-ai-mcp-commons/
├── src/swiss_ai_mcp_commons/
│   ├── __init__.py           # Main package exports
│   ├── models/               # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── location.py       # Location, Coordinates, Region
│   │   ├── weather.py        # Weather, Temperature, Snow, AirQuality
│   │   ├── pricing.py        # Price, FareOption, PricingInfo
│   │   └── time.py           # TimeRange, DateRange
│   ├── http/                 # HTTP client
│   │   ├── __init__.py
│   │   └── client.py         # CachedHttpClient with retries
│   ├── logging/              # Structured logging
│   │   ├── __init__.py
│   │   └── setup.py          # Logging configuration
│   └── validation/           # Validation & exceptions
│       ├── __init__.py
│       ├── validators.py     # Input validators
│       └── exceptions.py     # Exception hierarchy
├── tests/                    # Test suite
│   ├── conftest.py          # Shared fixtures
│   ├── test_models.py       # Model tests
│   └── test_validation.py   # Validator & exception tests
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

### Design Principles

1. **Standardization**: Common models used across all MCPs reduce duplication
2. **Validation First**: Input validation happens at model boundaries
3. **Error Clarity**: JSON-RPC error codes enable clear error handling
4. **Async Native**: HTTP client uses async/await for scalability
5. **Observable**: Structured logging enables production debugging
6. **Type Safe**: Full Pydantic validation with type hints

## Performance

- **Caching**: HTTP responses cached for 120 seconds (configurable)
- **Retries**: Automatic exponential backoff for transient errors
- **Async**: Non-blocking I/O for concurrent requests
- **Minimal Dependencies**: Only Pydantic, httpx, structlog

## Contributing

Guidelines for contributing to swiss-ai-mcp-commons:

1. Maintain backward compatibility (semver)
2. Add tests for new features
3. Keep models focused and composable
4. Document complex validators
5. Use consistent naming (snake_case for functions, PascalCase for classes)

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Report bugs](https://github.com/your-org/swiss-ai-mcp-commons/issues)
- Documentation: [Full docs](https://github.com/your-org/swiss-ai-mcp-commons/wiki)

---

**Built with ❤️ for the Swiss AI MCP ecosystem**
