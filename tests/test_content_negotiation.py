"""Tests for HTTP content negotiation utilities."""

import pytest
from swiss_ai_mcp_commons.http.content_negotiation import (
    ContentType,
    Encoding,
    MediaType,
    EncodingPreference,
    parse_media_type,
    parse_accept_header,
    parse_encoding_preference,
    parse_accept_encoding_header,
    select_content_type,
    select_encoding,
    build_content_type_header,
    should_compress,
)


class TestMediaType:
    """Tests for MediaType class."""

    def test_full_type(self):
        """Test full_type property."""
        mt = MediaType(type="application", subtype="json")
        assert mt.full_type == "application/json"

    def test_matches_exact(self):
        """Test exact match."""
        mt = MediaType(type="application", subtype="json")
        assert mt.matches("application/json")
        assert not mt.matches("text/html")

    def test_matches_wildcard_subtype(self):
        """Test wildcard subtype match."""
        mt = MediaType(type="text", subtype="*")
        assert mt.matches("text/html")
        assert mt.matches("text/plain")
        assert not mt.matches("application/json")

    def test_matches_wildcard_all(self):
        """Test wildcard all match."""
        mt = MediaType(type="*", subtype="*")
        assert mt.matches("application/json")
        assert mt.matches("text/html")
        assert mt.matches("image/png")

    def test_str_simple(self):
        """Test string representation without params."""
        mt = MediaType(type="application", subtype="json")
        assert str(mt) == "application/json"

    def test_str_with_quality(self):
        """Test string representation with quality."""
        mt = MediaType(type="text", subtype="html", quality=0.8)
        assert str(mt) == "text/html; q=0.8"

    def test_str_with_params(self):
        """Test string representation with parameters."""
        mt = MediaType(type="application", subtype="json", params={"charset": "utf-8"})
        assert "application/json" in str(mt)
        assert "charset=utf-8" in str(mt)


class TestEncodingPreference:
    """Tests for EncodingPreference class."""

    def test_matches_exact(self):
        """Test exact encoding match."""
        pref = EncodingPreference(encoding="gzip")
        assert pref.matches("gzip")
        assert not pref.matches("deflate")

    def test_matches_wildcard(self):
        """Test wildcard encoding match."""
        pref = EncodingPreference(encoding="*")
        assert pref.matches("gzip")
        assert pref.matches("deflate")
        assert pref.matches("br")

    def test_str_simple(self):
        """Test string representation without quality."""
        pref = EncodingPreference(encoding="gzip")
        assert str(pref) == "gzip"

    def test_str_with_quality(self):
        """Test string representation with quality."""
        pref = EncodingPreference(encoding="deflate", quality=0.7)
        assert str(pref) == "deflate; q=0.7"


class TestParseMediaType:
    """Tests for parse_media_type function."""

    def test_parse_simple(self):
        """Test parsing simple media type."""
        mt = parse_media_type("application/json")
        assert mt.type == "application"
        assert mt.subtype == "json"
        assert mt.quality == 1.0

    def test_parse_with_quality(self):
        """Test parsing media type with quality value."""
        mt = parse_media_type("text/html; q=0.8")
        assert mt.type == "text"
        assert mt.subtype == "html"
        assert mt.quality == 0.8

    def test_parse_with_params(self):
        """Test parsing media type with parameters."""
        mt = parse_media_type("application/json; charset=utf-8")
        assert mt.type == "application"
        assert mt.subtype == "json"
        assert mt.params == {"charset": "utf-8"}

    def test_parse_with_params_and_quality(self):
        """Test parsing media type with both params and quality."""
        mt = parse_media_type("text/html; charset=utf-8; q=0.9")
        assert mt.type == "text"
        assert mt.subtype == "html"
        assert mt.quality == 0.9
        assert mt.params == {"charset": "utf-8"}

    def test_parse_wildcard(self):
        """Test parsing wildcard media types."""
        mt1 = parse_media_type("text/*")
        assert mt1.type == "text"
        assert mt1.subtype == "*"

        mt2 = parse_media_type("*/*")
        assert mt2.type == "*"
        assert mt2.subtype == "*"

    def test_parse_quality_clamping(self):
        """Test that quality values are clamped to [0, 1]."""
        mt1 = parse_media_type("text/html; q=1.5")
        assert mt1.quality == 1.0

        mt2 = parse_media_type("text/html; q=-0.5")
        assert mt2.quality == 0.0


class TestParseAcceptHeader:
    """Tests for parse_accept_header function."""

    def test_parse_single(self):
        """Test parsing single media type."""
        media_types = parse_accept_header("application/json")
        assert len(media_types) == 1
        assert media_types[0].full_type == "application/json"

    def test_parse_multiple(self):
        """Test parsing multiple media types."""
        media_types = parse_accept_header("application/json, text/html")
        assert len(media_types) == 2
        assert media_types[0].full_type == "application/json"
        assert media_types[1].full_type == "text/html"

    def test_parse_with_quality_sorting(self):
        """Test that media types are sorted by quality."""
        media_types = parse_accept_header("text/html; q=0.8, application/json")
        assert len(media_types) == 2
        # Higher quality first
        assert media_types[0].full_type == "application/json"
        assert media_types[0].quality == 1.0
        assert media_types[1].full_type == "text/html"
        assert media_types[1].quality == 0.8

    def test_parse_complex(self):
        """Test parsing complex Accept header."""
        header = "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8"
        media_types = parse_accept_header(header)
        assert len(media_types) == 4
        # Check sorting by quality and specificity
        assert media_types[0].quality == 1.0  # text/html
        assert media_types[-1].full_type == "*/*"  # Lowest priority

    def test_parse_empty(self):
        """Test parsing empty Accept header."""
        media_types = parse_accept_header("")
        assert len(media_types) == 0


class TestParseEncodingPreference:
    """Tests for parse_encoding_preference function."""

    def test_parse_simple(self):
        """Test parsing simple encoding."""
        pref = parse_encoding_preference("gzip")
        assert pref.encoding == "gzip"
        assert pref.quality == 1.0

    def test_parse_with_quality(self):
        """Test parsing encoding with quality value."""
        pref = parse_encoding_preference("deflate; q=0.7")
        assert pref.encoding == "deflate"
        assert pref.quality == 0.7

    def test_parse_wildcard(self):
        """Test parsing wildcard encoding."""
        pref = parse_encoding_preference("*")
        assert pref.encoding == "*"


class TestParseAcceptEncodingHeader:
    """Tests for parse_accept_encoding_header function."""

    def test_parse_single(self):
        """Test parsing single encoding."""
        encodings = parse_accept_encoding_header("gzip")
        assert len(encodings) == 1
        assert encodings[0].encoding == "gzip"

    def test_parse_multiple(self):
        """Test parsing multiple encodings."""
        encodings = parse_accept_encoding_header("gzip, deflate, br")
        assert len(encodings) == 3
        assert encodings[0].encoding == "gzip"
        assert encodings[1].encoding == "deflate"
        assert encodings[2].encoding == "br"

    def test_parse_with_quality_sorting(self):
        """Test that encodings are sorted by quality."""
        encodings = parse_accept_encoding_header("gzip; q=0.8, deflate, br; q=0.5")
        assert len(encodings) == 3
        # Higher quality first
        assert encodings[0].encoding == "deflate"
        assert encodings[0].quality == 1.0
        assert encodings[1].encoding == "gzip"
        assert encodings[1].quality == 0.8
        assert encodings[2].encoding == "br"
        assert encodings[2].quality == 0.5

    def test_parse_empty(self):
        """Test parsing empty Accept-Encoding header."""
        encodings = parse_accept_encoding_header("")
        assert len(encodings) == 0


class TestSelectContentType:
    """Tests for select_content_type function."""

    def test_select_exact_match(self):
        """Test selecting exact match."""
        result = select_content_type(
            "application/json", ["application/json", "text/html"]
        )
        assert result == "application/json"

    def test_select_with_quality(self):
        """Test selecting based on quality values."""
        result = select_content_type(
            "text/html; q=0.8, application/json", ["application/json", "text/html"]
        )
        assert result == "application/json"

    def test_select_with_wildcard(self):
        """Test selecting with wildcard."""
        result = select_content_type("text/*", ["text/html", "application/json"])
        assert result == "text/html"

    def test_select_no_match(self):
        """Test when no content type matches."""
        result = select_content_type("application/xml", ["application/json", "text/html"])
        assert result is None

    def test_select_empty_accept(self):
        """Test with empty Accept header."""
        result = select_content_type("", ["application/json", "text/html"])
        assert result == "application/json"  # First available

    def test_select_empty_available(self):
        """Test with no available types."""
        result = select_content_type("application/json", [])
        assert result is None


class TestSelectEncoding:
    """Tests for select_encoding function."""

    def test_select_gzip(self):
        """Test selecting gzip encoding."""
        result = select_encoding("gzip, deflate", ["gzip", "identity"])
        assert result == "gzip"

    def test_select_with_quality(self):
        """Test selecting based on quality values."""
        result = select_encoding("gzip; q=0.5, deflate", ["gzip", "deflate", "identity"])
        assert result == "deflate"

    def test_select_fallback_identity(self):
        """Test fallback to identity when no match."""
        result = select_encoding("br", ["gzip", "identity"])
        assert result == "identity"

    def test_select_wildcard(self):
        """Test selecting with wildcard."""
        result = select_encoding("*", ["gzip", "deflate"])
        assert result == "gzip"

    def test_select_empty_accept_encoding(self):
        """Test with empty Accept-Encoding header."""
        result = select_encoding("", ["gzip", "identity"])
        assert result == "identity"

    def test_select_no_identity_available(self):
        """Test when identity is not available."""
        result = select_encoding("br", ["gzip", "deflate"])
        assert result is None


class TestBuildContentTypeHeader:
    """Tests for build_content_type_header function."""

    def test_build_without_charset(self):
        """Test building without charset."""
        result = build_content_type_header("application/json")
        assert result == "application/json"

    def test_build_with_charset(self):
        """Test building with charset."""
        result = build_content_type_header("application/json", "utf-8")
        assert result == "application/json; charset=utf-8"


class TestShouldCompress:
    """Tests for should_compress function."""

    def test_compress_large_content_with_gzip(self):
        """Test compression for large content with gzip support."""
        assert should_compress("gzip, deflate", content_size=2048)

    def test_no_compress_small_content(self):
        """Test no compression for small content."""
        assert not should_compress("gzip", content_size=512)

    def test_no_compress_without_accept_encoding(self):
        """Test no compression without Accept-Encoding header."""
        assert not should_compress("", content_size=2048)

    def test_compress_with_custom_min_size(self):
        """Test compression with custom minimum size."""
        assert should_compress("gzip", min_size_bytes=500, content_size=1000)
        assert not should_compress("gzip", min_size_bytes=2000, content_size=1000)

    def test_no_compress_with_zero_quality(self):
        """Test no compression when encoding has zero quality."""
        assert not should_compress("gzip; q=0", content_size=2048)

    def test_compress_with_brotli(self):
        """Test compression with Brotli encoding."""
        assert should_compress("br", content_size=2048)


class TestContentTypeEnum:
    """Tests for ContentType enum."""

    def test_json_content_type(self):
        """Test JSON content type."""
        assert ContentType.JSON == "application/json"

    def test_gzip_content_type(self):
        """Test gzip content type."""
        assert ContentType.GZIP == "application/gzip"


class TestEncodingEnum:
    """Tests for Encoding enum."""

    def test_identity_encoding(self):
        """Test identity encoding."""
        assert Encoding.IDENTITY == "identity"

    def test_gzip_encoding(self):
        """Test gzip encoding."""
        assert Encoding.GZIP == "gzip"

    def test_brotli_encoding(self):
        """Test Brotli encoding."""
        assert Encoding.BROTLI == "br"
