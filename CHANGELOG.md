# Changelog

All notable changes to swiss-ai-mcp-commons will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-22

### Added

#### HTTP Content Negotiation
- **Content negotiation utilities** for HTTP APIs (`http/content_negotiation.py`)
  - `ContentType` and `Encoding` enums for standard HTTP types
  - `MediaType` class for parsing Accept headers with quality values
  - `EncodingPreference` class for Accept-Encoding negotiation
  - `parse_accept_header()` - Parse and sort media types by quality
  - `parse_accept_encoding_header()` - Parse encoding preferences
  - `select_content_type()` - Choose best content type for client
  - `select_encoding()` - Choose best encoding with fallback
  - `build_content_type_header()` - Build Content-Type with charset
  - `should_compress()` - Smart compression decision based on size

#### JSON Serialization Enhancements
- **`JsonSerializableMixin` refactoring**
  - Extracted to dedicated `serialization.py` module
  - Added `serialize_with_negotiation()` method for automatic compression
  - Supports Accept-Encoding header for gzip compression
  - Configurable compression threshold (default: 1024 bytes)
  - Returns tuple of (content, headers) with proper HTTP headers
  - Backward compatible with existing `to_json()` and `to_json_gzipped()`

#### HTTP Framework Integration
- **Framework integration helpers** (`http/integration.py`)
  - `create_negotiated_response()` - Generic response creator
  - `fastapi_negotiated_response()` - FastAPI endpoint helper
  - `flask_negotiated_response()` - Flask endpoint helper
  - Works with Starlette/FastAPI Response objects
  - Automatic content-type and encoding header management

#### Documentation
- **Comprehensive content negotiation guide** (`docs/CONTENT_NEGOTIATION.md`)
  - Quick start examples
  - FastAPI integration (3 different methods)
  - Flask and Starlette integration examples
  - Configuration options and best practices
  - Testing examples (curl, requests, pytest)
  - Performance considerations and compression ratios
  - Migration guide for existing endpoints
  - Troubleshooting section
  - Real-world examples from aareguru-mcp and open-meteo-mcp

#### String Representation Methods
- Added `__str__()` methods to all model classes for better debugging
- Added `__repr__()` methods to HTTP client classes
- All clients now provide `to_dict()` for JSON serialization

### Changed
- `CachedHttpClient` now inherits from `JsonSerializableMixin`
- Improved code organization with dedicated modules for serialization

### Performance
- **60-80% bandwidth reduction** for JSON responses with gzip compression
- Smart compression only applies when beneficial (>1KB by default)
- Automatic fallback to uncompressed for small responses
- Compatible with all major HTTP clients and frameworks

### Testing
- **71 new tests** for content negotiation (54 tests)
- **17 new tests** for serialization enhancements
- **144 total tests** passing with comprehensive coverage
- All tests include edge cases and error handling

## [1.0.0] - 2025-01-XX

### Added
- Initial release of swiss-ai-mcp-commons
- Standardized data models (Location, Weather, Pricing, Time)
- HTTP client with caching and retries (`CachedHttpClient`)
- Structured logging configuration
- Validation utilities for Swiss-specific data
- Standard exception hierarchy for MCP errors
- Comprehensive test suite

### Models
- `Location`, `Coordinates`, `Region` - Geographic data
- `Weather`, `Temperature`, `SnowConditions`, `AirQuality` - Weather data
- `Price`, `FareOption`, `PricingInfo` - Pricing information
- `TimeRange`, `DateRange` - Time-related data

### HTTP
- `CachedHttpClient` - Async HTTP client with caching and retry logic
- Configurable cache TTL and retry strategies
- Support for GET and POST requests

### Validation
- `validate_date_range()` - Date range validation
- `validate_currency_code()` - Currency code validation
- `validate_swiss_canton()` - Swiss canton code validation
- `validate_email()` - Email validation
- `validate_phone()` - Swiss phone number validation
- `validate_price()` - Price validation with range checks

### Exceptions
- `StandardMcpException` - Base exception class
- `ValidationError` - Data validation errors
- `ApiError` - External API errors
- `ConfigurationError` - Configuration errors
- `AuthenticationError` - Authentication failures
- `RateLimitError` - Rate limit exceeded
- `TimeoutError` - Request timeouts

[1.1.0]: https://github.com/schlpbch/swiss-ai-mcp-commons/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/schlpbch/swiss-ai-mcp-commons/releases/tag/v1.0.0
