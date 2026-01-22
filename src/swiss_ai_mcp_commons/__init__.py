"""Swiss AI MCP Commons - Shared infrastructure for Swiss MCPs.

Provides:
- Standardized data models (Location, Weather, Pricing, etc.)
- HTTP client with caching and retries
- Structured logging configuration
- Validation utilities
- Standard exception hierarchy
"""

from .models import (
    Location,
    Coordinates,
    Region,
    Weather,
    Temperature,
    SnowConditions,
    AirQuality,
    Price,
    FareOption,
    PricingInfo,
    TimeRange,
    DateRange,
)

from .http import CachedHttpClient

from .logging import configure_logging, get_logger

from .validation import (
    StandardMcpException,
    ValidationError,
    ApiError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    validate_date_range,
    validate_currency_code,
    validate_swiss_canton,
    validate_email,
    validate_phone,
    validate_price,
)

__version__ = "1.1.0"
__author__ = "Claude"
__license__ = "MIT"

__all__ = [
    # Models
    "Location",
    "Coordinates",
    "Region",
    "Weather",
    "Temperature",
    "SnowConditions",
    "AirQuality",
    "Price",
    "FareOption",
    "PricingInfo",
    "TimeRange",
    "DateRange",
    # HTTP
    "CachedHttpClient",
    # Logging
    "configure_logging",
    "get_logger",
    # Validation
    "StandardMcpException",
    "ValidationError",
    "ApiError",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "validate_date_range",
    "validate_currency_code",
    "validate_swiss_canton",
    "validate_email",
    "validate_phone",
    "validate_price",
]
