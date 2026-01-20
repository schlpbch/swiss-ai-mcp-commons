"""Tests for validation utilities and exceptions."""

import pytest
from datetime import date, timedelta
from swiss_ai_mcp_commons import (
    ValidationError,
    ConfigurationError,
    RateLimitError,
    TimeoutError,
    validate_date_range,
    validate_currency_code,
    validate_swiss_canton,
)


class TestStandardMcpException:
    """Test StandardMcpException."""

    def test_exception_to_dict(self):
        """Test exception serialization."""
        from swiss_ai_mcp_commons import StandardMcpException
        exc = StandardMcpException("Test error", code=-32001)
        exc_dict = exc.to_dict()
        assert exc_dict["code"] == -32001
        assert exc_dict["message"] == "Test error"

    def test_exception_with_details(self):
        """Test exception with additional details."""
        from swiss_ai_mcp_commons import StandardMcpException
        exc = StandardMcpException(
            "Test error",
            details={"field": "email", "value": "invalid"}
        )
        exc_dict = exc.to_dict()
        assert exc_dict["data"]["field"] == "email"

    def test_exception_string_representation(self):
        """Test exception string format."""
        from swiss_ai_mcp_commons import StandardMcpException
        exc = StandardMcpException("Test", code=-32600)
        assert "[-32600]" in str(exc)
        assert "Test" in str(exc)


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_basic(self):
        """Test basic validation error."""
        exc = ValidationError("Invalid value")
        assert exc.code == exc.VALIDATION_ERROR
        assert exc.message == "Invalid value"

    def test_validation_error_with_field(self):
        """Test validation error with field name."""
        exc = ValidationError(
            "Invalid date",
            field="start_date",
            value="2024-13-01"
        )
        assert exc.details["field"] == "start_date"
        assert "2024-13-01" in exc.details["value"]

    def test_validation_error_chain(self):
        """Test validation error with original exception."""
        original = ValueError("Original error")
        exc = ValidationError("Wrapped error", cause=original)
        assert exc.cause == original


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_basic(self):
        """Test basic configuration error."""
        exc = ConfigurationError("Missing required config")
        assert exc.code == exc.CONFIGURATION_ERROR

    def test_configuration_error_with_key(self):
        """Test configuration error with config key."""
        exc = ConfigurationError(
            "Missing API key",
            config_key="AMADEUS_API_KEY"
        )
        assert exc.details["config_key"] == "AMADEUS_API_KEY"


class TestRateLimitError:
    """Test RateLimitError exception."""

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry info."""
        exc = RateLimitError(
            "Too many requests",
            retry_after_seconds=60
        )
        assert exc.details["retry_after_seconds"] == 60


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_timeout_error_with_timeout_value(self):
        """Test timeout error with timeout value."""
        exc = TimeoutError(
            "Request timed out",
            timeout_seconds=30.0
        )
        assert exc.details["timeout_seconds"] == 30.0


class TestValidateDateRange:
    """Test date range validation."""

    def test_valid_date_range(self):
        """Test valid date range."""
        start = date(2024, 7, 15)
        end = date(2024, 7, 22)
        result_start, result_end = validate_date_range(start, end, allow_past=True)
        assert result_start == start
        assert result_end == end

    def test_past_date_not_allowed(self):
        """Test past date validation."""
        past = date(2020, 1, 1)
        today = date.today()
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range(past, today)
        assert "past" in str(exc_info.value).lower()

    def test_past_date_allowed(self):
        """Test past date allowed when specified."""
        past = date(2020, 1, 1)
        result_start, _ = validate_date_range(past, date(2020, 1, 31), allow_past=True)
        assert result_start == past

    def test_end_before_start(self):
        """Test end date must be after start."""
        start = date(2024, 7, 22)
        end = date(2024, 7, 15)
        with pytest.raises(ValidationError):
            validate_date_range(start, end, allow_past=True)

    def test_min_days_requirement(self):
        """Test minimum days requirement."""
        start = date(2024, 7, 15)
        end = date(2024, 7, 16)  # Only 2 days
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range(start, end, min_days=7, allow_past=True)
        assert "at least 7 days" in str(exc_info.value).lower()

    def test_max_days_requirement(self):
        """Test maximum days requirement."""
        start = date(2024, 7, 15)
        end = date(2025, 1, 15)  # 185 days
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range(start, end, max_days=180, allow_past=True)
        assert "cannot exceed" in str(exc_info.value).lower()


class TestValidateCurrencyCode:
    """Test currency code validation."""

    def test_valid_currency_codes(self):
        """Test valid currency codes."""
        codes = ['CHF', 'USD', 'EUR', 'GBP']
        for code in codes:
            result = validate_currency_code(code)
            assert result == code

    def test_lowercase_normalization(self):
        """Test lowercase currency code normalization."""
        result = validate_currency_code('chf')
        assert result == 'CHF'

    def test_invalid_currency_code(self):
        """Test invalid currency code."""
        with pytest.raises(ValidationError) as exc_info:
            validate_currency_code('XXX')
        assert "Invalid" in str(exc_info.value)

    def test_wrong_length_currency(self):
        """Test currency code wrong length."""
        with pytest.raises(ValidationError) as exc_info:
            validate_currency_code('CH')
        assert "3 characters" in str(exc_info.value)


class TestValidateSwissCanton:
    """Test Swiss canton validation."""

    def test_valid_cantons(self, swiss_cantons):
        """Test all valid Swiss cantons."""
        for canton in swiss_cantons:
            result = validate_swiss_canton(canton)
            assert result == canton

    def test_lowercase_normalization(self):
        """Test lowercase canton normalization."""
        result = validate_swiss_canton('be')
        assert result == 'BE'

    def test_invalid_canton(self):
        """Test invalid canton code."""
        with pytest.raises(ValidationError) as exc_info:
            validate_swiss_canton('XX')
        assert "Invalid" in str(exc_info.value)

    def test_wrong_length_canton(self):
        """Test canton code wrong length."""
        with pytest.raises(ValidationError) as exc_info:
            validate_swiss_canton('BER')
        assert "2 characters" in str(exc_info.value)


class TestValidateEmail:
    """Test email validation."""

    def test_valid_emails(self):
        """Test valid email addresses."""
        from swiss_ai_mcp_commons import validate_email
        emails = [
            'user@example.com',
            'test.name@domain.co.uk',
            'info@swiss-tourism.ch',
        ]
        for email in emails:
            result = validate_email(email)
            assert "@" in result

    def test_invalid_emails(self):
        """Test invalid email addresses."""
        from swiss_ai_mcp_commons import validate_email
        invalid = ['test', 'test@', '@example.com', 'test.example']
        for email in invalid:
            with pytest.raises(ValidationError):
                validate_email(email)

    def test_email_lowercase(self):
        """Test email normalization to lowercase."""
        from swiss_ai_mcp_commons import validate_email
        result = validate_email('USER@EXAMPLE.COM')
        assert result == 'user@example.com'


class TestValidatePhone:
    """Test phone number validation."""

    def test_valid_swiss_phone(self):
        """Test valid Swiss phone numbers."""
        from swiss_ai_mcp_commons import validate_phone
        phones = [
            '+41 44 123 4567',  # +41 format
            '044 123 4567',     # 0 format
        ]
        for phone in phones:
            result = validate_phone(phone, country='CH')
            assert result.isdigit()

    def test_invalid_swiss_phone(self):
        """Test invalid Swiss phone numbers."""
        from swiss_ai_mcp_commons import validate_phone
        with pytest.raises(ValidationError):
            validate_phone('123', country='CH')

    def test_swiss_phone_format_variety(self):
        """Test various Swiss phone formats."""
        from swiss_ai_mcp_commons import validate_phone
        # All should normalize to digits only
        result = validate_phone('+41-44-123-4567', country='CH')
        assert len(result) == 11  # +41 + 9 digits


class TestValidatePrice:
    """Test price validation."""

    def test_valid_price(self):
        """Test valid price."""
        from swiss_ai_mcp_commons import validate_price
        result = validate_price(125.50)
        assert result == 125.50

    def test_price_rounding(self):
        """Test price rounding to 2 decimals."""
        from swiss_ai_mcp_commons import validate_price
        result = validate_price(125.555)
        assert result == 125.56

    def test_negative_price(self):
        """Test negative price rejection."""
        from swiss_ai_mcp_commons import validate_price
        with pytest.raises(ValidationError):
            validate_price(-10)

    def test_price_range(self):
        """Test price range validation."""
        from swiss_ai_mcp_commons import validate_price
        with pytest.raises(ValidationError):
            validate_price(2000000, max_price=1000000)
