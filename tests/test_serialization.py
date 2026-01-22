"""Tests for JSON serialization mixin."""

import gzip
import base64
import pytest
from swiss_ai_mcp_commons.serialization import JsonSerializableMixin


class TestClient(JsonSerializableMixin):
    """Test client implementing JsonSerializableMixin."""

    def __init__(self, name: str, value: int):
        """Initialize test client."""
        self.name = name
        self.value = value

    def to_dict(self):
        """Convert to dictionary."""
        return {"name": self.name, "value": self.value}


class TestJsonSerializableMixin:
    """Tests for JsonSerializableMixin class."""

    def test_to_dict_not_implemented(self):
        """Test that to_dict raises NotImplementedError if not overridden."""

        class IncompleteClient(JsonSerializableMixin):
            pass

        client = IncompleteClient()
        with pytest.raises(NotImplementedError, match="must implement to_dict"):
            client.to_dict()

    def test_to_json_simple(self):
        """Test simple JSON serialization."""
        client = TestClient("test", 42)
        result = client.to_json()
        assert result == '{"name": "test", "value": 42}'

    def test_to_json_with_indent(self):
        """Test JSON serialization with indentation."""
        client = TestClient("test", 42)
        result = client.to_json(indent=2)
        assert '"name": "test"' in result
        assert '"value": 42' in result

    def test_to_json_compressed(self):
        """Test JSON serialization with compression."""
        client = TestClient("test", 42)
        result = client.to_json(compress=True)

        # Should be base64 encoded
        assert isinstance(result, str)

        # Decode and decompress
        decoded = base64.b64decode(result)
        decompressed = gzip.decompress(decoded).decode('utf-8')
        assert decompressed == '{"name": "test", "value": 42}'

    def test_to_json_gzipped_as_base64(self):
        """Test gzipped JSON as base64 string."""
        client = TestClient("test", 42)
        result = client.to_json_gzipped(as_base64=True)

        # Should be base64 string
        assert isinstance(result, str)

        # Decode and decompress
        decoded = base64.b64decode(result)
        decompressed = gzip.decompress(decoded).decode('utf-8')
        assert decompressed == '{"name": "test", "value": 42}'

    def test_to_json_gzipped_as_bytes(self):
        """Test gzipped JSON as raw bytes."""
        client = TestClient("test", 42)
        result = client.to_json_gzipped(as_base64=False)

        # Should be raw bytes
        assert isinstance(result, bytes)

        # Decompress
        decompressed = gzip.decompress(result).decode('utf-8')
        assert decompressed == '{"name": "test", "value": 42}'


class TestSerializeWithNegotiation:
    """Tests for serialize_with_negotiation method."""

    def test_serialize_without_compression(self):
        """Test serialization without compression."""
        client = TestClient("test", 42)
        content, headers = client.serialize_with_negotiation()

        # Should return uncompressed JSON
        assert content == '{"name": "test", "value": 42}'
        assert headers["Content-Type"] == "application/json; charset=utf-8"
        assert "Content-Encoding" not in headers
        assert headers["Content-Length"] == str(len(content))

    def test_serialize_small_content_no_compression(self):
        """Test that small content is not compressed."""
        client = TestClient("a", 1)
        content, headers = client.serialize_with_negotiation(
            accept_encoding="gzip", min_compress_size=1024
        )

        # Should return uncompressed JSON (too small)
        assert isinstance(content, str)
        assert "Content-Encoding" not in headers

    def test_serialize_large_content_with_gzip(self):
        """Test that large content is compressed when requested."""
        # Create client with data that will exceed min_compress_size
        client = TestClient("x" * 500, 123456)
        content, headers = client.serialize_with_negotiation(
            accept_encoding="gzip", min_compress_size=100
        )

        # Should return compressed bytes
        assert isinstance(content, bytes)
        assert headers["Content-Type"] == "application/json; charset=utf-8"
        assert headers["Content-Encoding"] == "gzip"
        assert "Content-Length" in headers

        # Verify decompression works
        decompressed = gzip.decompress(content).decode('utf-8')
        assert '"name": "' in decompressed
        assert '"value": 123456' in decompressed

    def test_serialize_without_accept_encoding(self):
        """Test serialization without Accept-Encoding header."""
        client = TestClient("test", 42)
        content, headers = client.serialize_with_negotiation(accept_encoding=None)

        # Should return uncompressed JSON
        assert isinstance(content, str)
        assert "Content-Encoding" not in headers

    def test_serialize_with_custom_charset(self):
        """Test serialization with custom charset."""
        client = TestClient("test", 42)
        content, headers = client.serialize_with_negotiation(charset="iso-8859-1")

        assert headers["Content-Type"] == "application/json; charset=iso-8859-1"

    def test_serialize_with_indent(self):
        """Test serialization with pretty printing."""
        client = TestClient("test", 42)
        content, headers = client.serialize_with_negotiation(indent=2)

        assert isinstance(content, str)
        assert "\n" in content  # Should have newlines from indentation
        assert '"name": "test"' in content

    def test_serialize_compression_threshold(self):
        """Test compression threshold behavior."""
        client = TestClient("x" * 200, 12345)

        # With high threshold, should not compress
        content1, headers1 = client.serialize_with_negotiation(
            accept_encoding="gzip", min_compress_size=10000
        )
        assert isinstance(content1, str)
        assert "Content-Encoding" not in headers1

        # With low threshold, should compress
        content2, headers2 = client.serialize_with_negotiation(
            accept_encoding="gzip", min_compress_size=100
        )
        assert isinstance(content2, bytes)
        assert headers2["Content-Encoding"] == "gzip"

    def test_serialize_deflate_fallback(self):
        """Test fallback to identity when unsupported encoding requested."""
        client = TestClient("x" * 500, 123)
        content, headers = client.serialize_with_negotiation(
            accept_encoding="deflate", min_compress_size=100
        )

        # Should fallback to uncompressed (identity)
        assert isinstance(content, str)
        assert "Content-Encoding" not in headers

    def test_serialize_multiple_encodings(self):
        """Test with multiple encodings in Accept-Encoding."""
        client = TestClient("x" * 500, 123)
        content, headers = client.serialize_with_negotiation(
            accept_encoding="gzip, deflate, br", min_compress_size=100
        )

        # Should select gzip
        assert isinstance(content, bytes)
        assert headers["Content-Encoding"] == "gzip"

    def test_serialize_quality_values(self):
        """Test with quality values in Accept-Encoding."""
        client = TestClient("x" * 500, 123)
        content, headers = client.serialize_with_negotiation(
            accept_encoding="gzip; q=1.0, identity; q=0.5", min_compress_size=100
        )

        # Should prefer gzip (higher quality)
        assert isinstance(content, bytes)
        assert headers["Content-Encoding"] == "gzip"

    def test_serialize_content_length_accuracy(self):
        """Test that Content-Length is accurate."""
        client = TestClient("test", 42)

        # Uncompressed
        content1, headers1 = client.serialize_with_negotiation()
        assert int(headers1["Content-Length"]) == len(content1.encode('utf-8'))

        # Compressed
        client2 = TestClient("x" * 500, 123)
        content2, headers2 = client2.serialize_with_negotiation(
            accept_encoding="gzip", min_compress_size=100
        )
        assert int(headers2["Content-Length"]) == len(content2)
