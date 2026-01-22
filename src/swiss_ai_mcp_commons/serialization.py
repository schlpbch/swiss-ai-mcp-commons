"""JSON serialization mixin for API clients."""

import json
import gzip
import base64
from typing import Any, Dict


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
