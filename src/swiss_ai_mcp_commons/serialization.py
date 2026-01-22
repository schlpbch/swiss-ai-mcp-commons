"""JSON serialization mixin for API clients."""

import json
import gzip
import base64
from typing import Any, Dict, Tuple, Optional

from .http.content_negotiation import (
    ContentType,
    Encoding,
    select_encoding,
    build_content_type_header,
    should_compress,
)


class JsonSerializableMixin:
    """Mixin providing JSON serialization with optional gzip compression.

    Classes using this mixin must implement a `to_dict()` method that returns
    a dictionary representation of their state.
    """

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance state to dictionary for JSON serialization.

        This method must be implemented by classes using the mixin.

        Returns:
            Dictionary representation of instance state

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement to_dict() method"
        )

    def to_json(self, compress: bool = False, **kwargs) -> str:
        """Convert instance state to compact JSON string with optional gzip compression.

        Args:
            compress: If True, gzip compress and base64 encode the JSON
            **kwargs: Additional arguments for json.dumps (e.g., indent=2 for pretty print)

        Returns:
            JSON string representation of instance state, optionally gzip compressed and base64 encoded
        """
        json_str = json.dumps(self.to_dict(), **kwargs)
        if compress:
            compressed = gzip.compress(json_str.encode('utf-8'))
            return base64.b64encode(compressed).decode('ascii')
        return json_str

    def to_json_gzipped(self, as_base64: bool = True, **kwargs) -> str | bytes:
        """Convert instance state to gzip-compressed JSON.

        Args:
            as_base64: If True, return base64-encoded string; if False, return raw bytes
            **kwargs: Additional arguments for json.dumps (e.g., indent=2 for pretty print)

        Returns:
            Gzip-compressed JSON as base64 string or raw bytes
        """
        json_str = json.dumps(self.to_dict(), **kwargs)
        compressed = gzip.compress(json_str.encode('utf-8'))
        if as_base64:
            return base64.b64encode(compressed).decode('ascii')
        return compressed

    def serialize_with_negotiation(
        self,
        accept_encoding: Optional[str] = None,
        min_compress_size: int = 1024,
        charset: str = "utf-8",
        **kwargs
    ) -> Tuple[str | bytes, Dict[str, str]]:
        """Serialize instance with content negotiation support.

        This method serializes the instance to JSON and optionally compresses it based
        on the Accept-Encoding header and content size.

        Args:
            accept_encoding: Accept-Encoding header value (e.g., 'gzip, deflate')
            min_compress_size: Minimum size in bytes to trigger compression (default: 1024)
            charset: Character encoding for JSON (default: 'utf-8')
            **kwargs: Additional arguments for json.dumps (e.g., indent=2)

        Returns:
            Tuple of (serialized_content, response_headers) where:
            - serialized_content: JSON string or gzip-compressed bytes
            - response_headers: Dict with 'Content-Type' and optionally 'Content-Encoding'

        Examples:
            >>> client = SomeClient()
            >>> content, headers = client.serialize_with_negotiation(
            ...     accept_encoding='gzip',
            ...     indent=2
            ... )
            >>> print(headers['Content-Type'])
            'application/json; charset=utf-8'
            >>> print(headers.get('Content-Encoding'))
            'gzip'
        """
        # Serialize to JSON
        json_str = json.dumps(self.to_dict(), **kwargs)
        json_bytes = json_str.encode(charset)
        content_size = len(json_bytes)

        # Initialize response headers
        headers: Dict[str, str] = {
            "Content-Type": build_content_type_header(ContentType.JSON.value, charset)
        }

        # Determine if compression should be applied
        if accept_encoding and should_compress(
            accept_encoding, min_size_bytes=min_compress_size, content_size=content_size
        ):
            # Select best encoding
            encoding = select_encoding(
                accept_encoding, [Encoding.GZIP.value, Encoding.IDENTITY.value]
            )

            if encoding == Encoding.GZIP.value:
                # Compress and return bytes
                compressed = gzip.compress(json_bytes)
                headers["Content-Encoding"] = Encoding.GZIP.value
                headers["Content-Length"] = str(len(compressed))
                return compressed, headers

        # Return uncompressed JSON
        headers["Content-Length"] = str(content_size)
        return json_str, headers
