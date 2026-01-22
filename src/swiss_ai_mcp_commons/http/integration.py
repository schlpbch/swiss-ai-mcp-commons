"""HTTP framework integration helpers for content negotiation.

This module provides utilities for integrating content negotiation
with popular Python web frameworks like FastAPI, Starlette, and Flask.
"""

from typing import Any, Dict, Optional
try:
    from starlette.responses import Response
    HAS_STARLETTE = True
except ImportError:
    HAS_STARLETTE = False


def create_negotiated_response(
    content: str | bytes,
    headers: Dict[str, str],
    status_code: int = 200,
) -> Any:
    """Create an HTTP response with content negotiation headers.

    Works with Starlette/FastAPI Response objects.

    Args:
        content: Response content (JSON string or gzip bytes)
        headers: Headers dict with Content-Type, Content-Encoding, Content-Length
        status_code: HTTP status code (default: 200)

    Returns:
        Starlette Response object if available, otherwise dict

    Examples:
        >>> from swiss_ai_mcp_commons.serialization import JsonSerializableMixin
        >>> class MyClient(JsonSerializableMixin):
        ...     def to_dict(self):
        ...         return {"status": "ok"}
        >>>
        >>> client = MyClient()
        >>> content, headers = client.serialize_with_negotiation(
        ...     accept_encoding="gzip"
        ... )
        >>> response = create_negotiated_response(content, headers)
    """
    if HAS_STARLETTE:
        return Response(
            content=content if isinstance(content, bytes) else content.encode('utf-8'),
            status_code=status_code,
            headers=headers,
            media_type=headers.get("Content-Type", "application/json"),
        )
    else:
        # Fallback for non-Starlette environments
        return {
            "content": content,
            "status_code": status_code,
            "headers": headers,
        }


# FastAPI-specific helper
def fastapi_negotiated_response(
    serializable: Any,
    accept_encoding: Optional[str] = None,
    min_compress_size: int = 1024,
    status_code: int = 200,
) -> Any:
    """Create FastAPI response with automatic content negotiation.

    Args:
        serializable: Object with serialize_with_negotiation() method
        accept_encoding: Accept-Encoding header from request
        min_compress_size: Minimum size for compression (default: 1024 bytes)
        status_code: HTTP status code (default: 200)

    Returns:
        FastAPI Response with negotiated content and headers

    Examples:
        FastAPI endpoint example:
        ```python
        from fastapi import FastAPI, Header
        from swiss_ai_mcp_commons.http.integration import fastapi_negotiated_response

        app = FastAPI()

        @app.get("/api/client")
        async def get_client(
            accept_encoding: Optional[str] = Header(None)
        ):
            client = MyClient()
            return fastapi_negotiated_response(
                client,
                accept_encoding=accept_encoding
            )
        ```
    """
    if not hasattr(serializable, 'serialize_with_negotiation'):
        raise ValueError(
            f"{type(serializable).__name__} must have serialize_with_negotiation() method"
        )

    content, headers = serializable.serialize_with_negotiation(
        accept_encoding=accept_encoding,
        min_compress_size=min_compress_size,
    )

    return create_negotiated_response(content, headers, status_code)


# Flask-specific helper (if Flask is available)
try:
    from flask import make_response
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


def flask_negotiated_response(
    serializable: Any,
    accept_encoding: Optional[str] = None,
    min_compress_size: int = 1024,
    status_code: int = 200,
) -> Any:
    """Create Flask response with automatic content negotiation.

    Args:
        serializable: Object with serialize_with_negotiation() method
        accept_encoding: Accept-Encoding header from request
        min_compress_size: Minimum size for compression (default: 1024 bytes)
        status_code: HTTP status code (default: 200)

    Returns:
        Flask Response with negotiated content and headers

    Examples:
        Flask endpoint example:
        ```python
        from flask import Flask, request
        from swiss_ai_mcp_commons.http.integration import flask_negotiated_response

        app = Flask(__name__)

        @app.route('/api/client')
        def get_client():
            client = MyClient()
            return flask_negotiated_response(
                client,
                accept_encoding=request.headers.get('Accept-Encoding')
            )
        ```
    """
    if not HAS_FLASK:
        raise ImportError("Flask is not installed")

    if not hasattr(serializable, 'serialize_with_negotiation'):
        raise ValueError(
            f"{type(serializable).__name__} must have serialize_with_negotiation() method"
        )

    content, headers = serializable.serialize_with_negotiation(
        accept_encoding=accept_encoding,
        min_compress_size=min_compress_size,
    )

    response = make_response(content, status_code)
    for key, value in headers.items():
        response.headers[key] = value

    return response
