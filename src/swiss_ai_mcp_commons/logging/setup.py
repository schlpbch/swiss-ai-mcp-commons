"""Structured logging configuration using structlog."""

import structlog
import logging
import json
from typing import Any
import sys


def configure_logging(
    app_name: str = "swiss-ai-mcp",
    version: str = "1.0.0",
    json_output: bool = True,
    log_level: str = "INFO",
) -> None:
    """Configure structured logging with structlog.

    Args:
        app_name: Application name for logging context
        version: Application version for logging context
        json_output: Whether to output JSON formatted logs
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard logging first
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Structlog configuration
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        # Add context from context vars
        structlog.contextvars.merge_contextvars,
        # Add request ID if available
        structlog.stdlib.add_log_level,
        # Add timestamp
        timestamper,
        # Add app context
        structlog.processors.CallsiteParameterAdder(),
    ]

    if json_output:
        # JSON output for production
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Human-readable output for development
        structlog.configure(
            processors=shared_processors + [
                structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Add application context
    logger = structlog.get_logger()
    logger.info(
        "logging_initialized",
        app=app_name,
        version=version,
        json_output=json_output,
        log_level=log_level,
    )


class JsonFormatter(logging.Formatter):
    """JSON formatter for standard logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_logger(name: str) -> structlog.typing.FilteringBoundLogger:
    """Get a named logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)
