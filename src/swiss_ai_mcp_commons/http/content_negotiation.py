"""HTTP content negotiation utilities for API clients and servers."""

from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ContentType(str, Enum):
    """Common content types for API responses."""

    JSON = "application/json"
    JSON_UTF8 = "application/json; charset=utf-8"
    GZIP = "application/gzip"
    OCTET_STREAM = "application/octet-stream"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"


class Encoding(str, Enum):
    """Common content encodings."""

    IDENTITY = "identity"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "br"


@dataclass
class MediaType:
    """Parsed media type with quality value."""

    type: str
    subtype: str
    quality: float = 1.0
    params: dict[str, str] | None = None

    @property
    def full_type(self) -> str:
        """Get full media type (type/subtype)."""
        return f"{self.type}/{self.subtype}"

    def matches(self, content_type: str) -> bool:
        """Check if this media type matches a content type.

        Args:
            content_type: Content type to match (e.g., 'application/json')

        Returns:
            True if matches, False otherwise
        """
        if self.type == "*" and self.subtype == "*":
            return True
        if self.subtype == "*":
            return content_type.startswith(f"{self.type}/")
        return content_type == self.full_type

    def __str__(self) -> str:
        """String representation of media type."""
        result = self.full_type
        if self.params:
            params_str = "; ".join(f"{k}={v}" for k, v in self.params.items())
            result = f"{result}; {params_str}"
        if self.quality != 1.0:
            result = f"{result}; q={self.quality}"
        return result


@dataclass
class EncodingPreference:
    """Content encoding with quality value."""

    encoding: str
    quality: float = 1.0

    def matches(self, encoding: str) -> bool:
        """Check if this preference matches an encoding.

        Args:
            encoding: Encoding to match (e.g., 'gzip')

        Returns:
            True if matches, False otherwise
        """
        return self.encoding == "*" or self.encoding == encoding

    def __str__(self) -> str:
        """String representation of encoding preference."""
        if self.quality != 1.0:
            return f"{self.encoding}; q={self.quality}"
        return self.encoding


def parse_media_type(media_type_str: str) -> MediaType:
    """Parse a media type string with optional quality value.

    Args:
        media_type_str: Media type string (e.g., 'application/json; q=0.8')

    Returns:
        Parsed MediaType object

    Examples:
        >>> parse_media_type('application/json')
        MediaType(type='application', subtype='json', quality=1.0)
        >>> parse_media_type('text/*; q=0.5')
        MediaType(type='text', subtype='*', quality=0.5)
    """
    parts = [p.strip() for p in media_type_str.split(";")]
    main_type = parts[0]

    # Parse type/subtype
    if "/" in main_type:
        type_parts = main_type.split("/", 1)
        media_type = type_parts[0].strip()
        media_subtype = type_parts[1].strip()
    else:
        media_type = main_type
        media_subtype = "*"

    # Parse parameters and quality
    quality = 1.0
    params: dict[str, str] = {}

    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "q":
                try:
                    quality = float(value)
                    quality = max(0.0, min(1.0, quality))  # Clamp to [0, 1]
                except ValueError:
                    quality = 1.0
            else:
                params[key] = value

    return MediaType(
        type=media_type,
        subtype=media_subtype,
        quality=quality,
        params=params if params else None,
    )


def parse_accept_header(accept_header: str) -> List[MediaType]:
    """Parse Accept header value into list of media types.

    Args:
        accept_header: Accept header value (e.g., 'application/json, text/html; q=0.9')

    Returns:
        List of MediaType objects sorted by quality (highest first)

    Examples:
        >>> parse_accept_header('application/json, text/html; q=0.9')
        [MediaType(type='application', subtype='json', quality=1.0),
         MediaType(type='text', subtype='html', quality=0.9)]
    """
    if not accept_header:
        return []

    media_types = [parse_media_type(mt.strip()) for mt in accept_header.split(",")]
    # Sort by quality (highest first), then by specificity
    return sorted(
        media_types,
        key=lambda mt: (mt.quality, mt.type != "*", mt.subtype != "*"),
        reverse=True,
    )


def parse_encoding_preference(encoding_str: str) -> EncodingPreference:
    """Parse an encoding preference string with optional quality value.

    Args:
        encoding_str: Encoding string (e.g., 'gzip; q=0.8')

    Returns:
        Parsed EncodingPreference object

    Examples:
        >>> parse_encoding_preference('gzip')
        EncodingPreference(encoding='gzip', quality=1.0)
        >>> parse_encoding_preference('br; q=0.5')
        EncodingPreference(encoding='br', quality=0.5)
    """
    parts = [p.strip() for p in encoding_str.split(";")]
    encoding = parts[0]
    quality = 1.0

    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            if key.strip() == "q":
                try:
                    quality = float(value.strip())
                    quality = max(0.0, min(1.0, quality))
                except ValueError:
                    quality = 1.0

    return EncodingPreference(encoding=encoding, quality=quality)


def parse_accept_encoding_header(accept_encoding: str) -> List[EncodingPreference]:
    """Parse Accept-Encoding header value into list of encoding preferences.

    Args:
        accept_encoding: Accept-Encoding header value (e.g., 'gzip, deflate; q=0.8')

    Returns:
        List of EncodingPreference objects sorted by quality (highest first)

    Examples:
        >>> parse_accept_encoding_header('gzip, deflate; q=0.8')
        [EncodingPreference(encoding='gzip', quality=1.0),
         EncodingPreference(encoding='deflate', quality=0.8)]
    """
    if not accept_encoding:
        return []

    encodings = [parse_encoding_preference(e.strip()) for e in accept_encoding.split(",")]
    return sorted(encodings, key=lambda e: e.quality, reverse=True)


def select_content_type(
    accept_header: str, available_types: List[str]
) -> Optional[str]:
    """Select the best content type based on Accept header and available types.

    Args:
        accept_header: Accept header value from client
        available_types: List of content types the server can provide

    Returns:
        Best matching content type, or None if no match

    Examples:
        >>> select_content_type('application/json, text/*', ['application/json', 'text/html'])
        'application/json'
        >>> select_content_type('text/html', ['application/json'])
        None
    """
    if not accept_header:
        return available_types[0] if available_types else None

    accepted = parse_accept_header(accept_header)

    for media_type in accepted:
        for available in available_types:
            if media_type.matches(available):
                return available

    return None


def select_encoding(
    accept_encoding: str, available_encodings: List[str]
) -> Optional[str]:
    """Select the best encoding based on Accept-Encoding header.

    Args:
        accept_encoding: Accept-Encoding header value from client
        available_encodings: List of encodings the server supports

    Returns:
        Best matching encoding, or None if no match

    Examples:
        >>> select_encoding('gzip, deflate', ['gzip', 'identity'])
        'gzip'
        >>> select_encoding('br', ['gzip', 'identity'])
        'identity'  # Fallback to identity
    """
    if not accept_encoding:
        return "identity"

    preferences = parse_accept_encoding_header(accept_encoding)

    for pref in preferences:
        for available in available_encodings:
            if pref.matches(available):
                return available

    # Fallback to identity if available
    return "identity" if "identity" in available_encodings else None


def build_content_type_header(
    content_type: str, charset: Optional[str] = None
) -> str:
    """Build a complete Content-Type header value.

    Args:
        content_type: Base content type (e.g., 'application/json')
        charset: Optional charset (e.g., 'utf-8')

    Returns:
        Complete Content-Type header value

    Examples:
        >>> build_content_type_header('application/json', 'utf-8')
        'application/json; charset=utf-8'
    """
    if charset:
        return f"{content_type}; charset={charset}"
    return content_type


def should_compress(
    accept_encoding: str, min_size_bytes: int = 1024, content_size: int = 0
) -> bool:
    """Determine if response should be compressed based on Accept-Encoding.

    Args:
        accept_encoding: Accept-Encoding header value from client
        min_size_bytes: Minimum content size to compress (default: 1024 bytes)
        content_size: Size of content to potentially compress

    Returns:
        True if content should be compressed, False otherwise

    Examples:
        >>> should_compress('gzip, deflate', content_size=2048)
        True
        >>> should_compress('gzip', content_size=512)
        False  # Too small
    """
    if content_size < min_size_bytes:
        return False

    if not accept_encoding:
        return False

    # Check if client accepts gzip or other compression
    encodings = parse_accept_encoding_header(accept_encoding)
    for enc in encodings:
        if enc.encoding in ["gzip", "deflate", "br"] and enc.quality > 0:
            return True

    return False
