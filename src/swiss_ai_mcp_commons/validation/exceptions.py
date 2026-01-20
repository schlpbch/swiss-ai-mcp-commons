"""Standard exception hierarchy for MCPs."""

from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class StandardMcpException(Exception):
    """Base exception for all MCP errors with JSON-RPC error codes."""

    # JSON-RPC 2.0 error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32099
    SERVER_ERROR_END = -32000

    # Custom error codes (reserved range)
    VALIDATION_ERROR = -32001
    AUTHENTICATION_ERROR = -32002
    AUTHORIZATION_ERROR = -32003
    NOT_FOUND_ERROR = -32004
    CONFLICT_ERROR = -32005
    EXTERNAL_API_ERROR = -32006
    RATE_LIMIT_ERROR = -32007
    TIMEOUT_ERROR = -32008
    CONFIGURATION_ERROR = -32009

    def __init__(
        self,
        message: str,
        code: int = INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize StandardMcpException.

        Args:
            message: Human-readable error message
            code: JSON-RPC error code
            details: Additional error details
            cause: Original exception that caused this
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.cause = cause

        logger.error(
            "mcp_exception",
            message=message,
            code=code,
            details=self.details,
            cause=str(cause) if cause else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to JSON-RPC error object."""
        error_obj = {
            "code": self.code,
            "message": self.message,
        }

        if self.details:
            error_obj["data"] = self.details

        return error_obj

    def __str__(self) -> str:
        """String representation."""
        return f"[{self.code}] {self.message}"


class ValidationError(StandardMcpException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize ValidationError.

        Args:
            message: Error message
            field: Field name that failed validation
            value: Invalid value
            cause: Original exception
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(
            message,
            code=self.VALIDATION_ERROR,
            details=details,
            cause=cause,
        )


class ApiError(StandardMcpException):
    """Raised when external API call fails."""

    def __init__(
        self,
        message: str,
        api_name: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize ApiError.

        Args:
            message: Error message
            api_name: Name of the API that failed
            status_code: HTTP status code
            response_body: Response body from API
            cause: Original exception
        """
        details = {"api": api_name}
        if status_code:
            details["status_code"] = status_code
        if response_body:
            details["response"] = response_body[:500]  # Truncate long responses

        super().__init__(
            message,
            code=self.EXTERNAL_API_ERROR,
            details=details,
            cause=cause,
        )


class ConfigurationError(StandardMcpException):
    """Raised when configuration is invalid."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize ConfigurationError.

        Args:
            message: Error message
            config_key: Configuration key that's missing/invalid
            cause: Original exception
        """
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message,
            code=self.CONFIGURATION_ERROR,
            details=details,
            cause=cause,
        )


class AuthenticationError(StandardMcpException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        cause: Optional[Exception] = None,
    ):
        """Initialize AuthenticationError."""
        super().__init__(
            message,
            code=self.AUTHENTICATION_ERROR,
            cause=cause,
        )


class RateLimitError(StandardMcpException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        retry_after_seconds: Optional[int] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize RateLimitError.

        Args:
            message: Error message
            retry_after_seconds: Seconds to wait before retry
            cause: Original exception
        """
        details = {}
        if retry_after_seconds:
            details["retry_after_seconds"] = retry_after_seconds

        super().__init__(
            message,
            code=self.RATE_LIMIT_ERROR,
            details=details,
            cause=cause,
        )


class TimeoutError(StandardMcpException):
    """Raised when operation times out."""

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize TimeoutError.

        Args:
            message: Error message
            timeout_seconds: Timeout value
            cause: Original exception
        """
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds

        super().__init__(
            message,
            code=self.TIMEOUT_ERROR,
            details=details,
            cause=cause,
        )
