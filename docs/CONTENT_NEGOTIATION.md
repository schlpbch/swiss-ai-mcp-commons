# HTTP Content Negotiation Guide

This guide explains how to use the HTTP content negotiation features in swiss-ai-mcp-commons across your MCP servers.

## Overview

The library provides comprehensive HTTP content negotiation support for:
- **Content-Type negotiation** - Select best response format based on client's Accept header
- **Content-Encoding negotiation** - Automatic gzip compression based on Accept-Encoding header
- **Smart compression** - Only compress when beneficial (configurable size threshold)
- **Framework integration** - Helper functions for FastAPI, Flask, and Starlette

## Quick Start

### Basic Usage with JsonSerializableMixin

Any client that inherits from `JsonSerializableMixin` automatically gets content negotiation support:

```python
from swiss_ai_mcp_commons.serialization import JsonSerializableMixin

class MyClient(JsonSerializableMixin):
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def to_dict(self):
        return {"name": self.name, "value": self.value}

# Create client
client = MyClient("example", 42)

# Simple JSON serialization
json_str = client.to_json()
# Output: '{"name": "example", "value": 42}'

# With content negotiation
content, headers = client.serialize_with_negotiation(
    accept_encoding="gzip, deflate"
)
# content: gzip-compressed bytes (if content is large enough)
# headers: {'Content-Type': 'application/json; charset=utf-8',
#           'Content-Encoding': 'gzip',
#           'Content-Length': '...'}
```

## FastAPI Integration

### Method 1: Using the Helper Function

```python
from fastapi import FastAPI, Header
from typing import Optional
from swiss_ai_mcp_commons.http.integration import fastapi_negotiated_response
from aareguru_mcp.client import AareguruClient

app = FastAPI()

@app.get("/api/client/state")
async def get_client_state(
    accept_encoding: Optional[str] = Header(None)
):
    """Get client state with automatic content negotiation."""
    async with AareguruClient() as client:
        return fastapi_negotiated_response(
            client,
            accept_encoding=accept_encoding,
            min_compress_size=1024  # Only compress if > 1KB
        )
```

### Method 2: Manual Integration

```python
from fastapi import FastAPI, Header, Response
from typing import Optional
from aareguru_mcp.client import AareguruClient

app = FastAPI()

@app.get("/api/client/state")
async def get_client_state(
    accept_encoding: Optional[str] = Header(None)
):
    """Get client state with manual content negotiation."""
    async with AareguruClient() as client:
        # Serialize with negotiation
        content, headers = client.serialize_with_negotiation(
            accept_encoding=accept_encoding,
            min_compress_size=1024
        )

        # Create response
        return Response(
            content=content if isinstance(content, bytes) else content.encode('utf-8'),
            headers=headers,
            media_type=headers.get("Content-Type", "application/json")
        )
```

### Method 3: As FastAPI Dependency

```python
from fastapi import FastAPI, Header, Depends
from typing import Optional

def get_accept_encoding(
    accept_encoding: Optional[str] = Header(None)
) -> Optional[str]:
    """Extract Accept-Encoding header."""
    return accept_encoding

@app.get("/api/client/state")
async def get_client_state(
    accept_encoding: Optional[str] = Depends(get_accept_encoding)
):
    async with AareguruClient() as client:
        return fastapi_negotiated_response(client, accept_encoding)
```

## Flask Integration

```python
from flask import Flask, request
from swiss_ai_mcp_commons.http.integration import flask_negotiated_response
from aareguru_mcp.client import AareguruClient

app = Flask(__name__)

@app.route('/api/client/state')
async def get_client_state():
    """Get client state with content negotiation."""
    async with AareguruClient() as client:
        return flask_negotiated_response(
            client,
            accept_encoding=request.headers.get('Accept-Encoding'),
            min_compress_size=1024
        )
```

## Starlette Integration

```python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from aareguru_mcp.client import AareguruClient

async def client_state(request):
    """Get client state with content negotiation."""
    async with AareguruClient() as client:
        content, headers = client.serialize_with_negotiation(
            accept_encoding=request.headers.get('accept-encoding'),
            min_compress_size=1024
        )

        return Response(
            content=content if isinstance(content, bytes) else content.encode('utf-8'),
            headers=headers,
            media_type=headers.get("Content-Type", "application/json")
        )

app = Starlette(routes=[
    Route('/api/client/state', client_state),
])
```

## Configuration Options

### serialize_with_negotiation() Parameters

```python
content, headers = client.serialize_with_negotiation(
    accept_encoding="gzip, deflate",  # Client's Accept-Encoding header
    min_compress_size=1024,            # Minimum bytes to compress (default: 1024)
    charset="utf-8",                   # Character encoding (default: utf-8)
    indent=2                           # JSON formatting (optional)
)
```

### Compression Behavior

- **Small content** (< min_compress_size): Always returns uncompressed JSON string
- **Large content** + **no Accept-Encoding**: Returns uncompressed JSON string
- **Large content** + **Accept-Encoding: gzip**: Returns gzip-compressed bytes
- **Automatic fallback**: If client doesn't support gzip, returns uncompressed

### Response Headers

The `headers` dict always includes:
- `Content-Type`: Always `application/json; charset=utf-8`
- `Content-Length`: Size of the actual content (compressed or uncompressed)
- `Content-Encoding`: Only present if content is compressed (e.g., `gzip`)

## Advanced Usage

### Custom Content Type Selection

```python
from swiss_ai_mcp_commons.http.content_negotiation import (
    parse_accept_header,
    select_content_type,
)

# Parse client's Accept header
accept = request.headers.get('Accept', '')
media_types = parse_accept_header(accept)

# Select best content type
available = ['application/json', 'application/xml']
best = select_content_type(accept, available)
# Returns: 'application/json' (if client accepts it)
```

### Manual Encoding Selection

```python
from swiss_ai_mcp_commons.http.content_negotiation import (
    select_encoding,
    should_compress,
)

accept_encoding = request.headers.get('Accept-Encoding', '')
content_size = len(json_data)

# Check if should compress
if should_compress(accept_encoding, content_size=content_size, min_size_bytes=1024):
    # Select best encoding
    encoding = select_encoding(
        accept_encoding,
        ['gzip', 'deflate', 'identity']
    )
    # Returns: 'gzip' (if client supports it)
```

## Testing Content Negotiation

### Testing with curl

```bash
# Request without compression
curl http://localhost:8000/api/client/state

# Request with gzip compression
curl -H "Accept-Encoding: gzip" \
     http://localhost:8000/api/client/state \
     --compressed

# Request with multiple encodings
curl -H "Accept-Encoding: gzip, deflate, br" \
     http://localhost:8000/api/client/state \
     --compressed
```

### Testing with Python requests

```python
import requests
import gzip

# Request with gzip support
response = requests.get(
    'http://localhost:8000/api/client/state',
    headers={'Accept-Encoding': 'gzip'}
)

# Check if compressed
if response.headers.get('Content-Encoding') == 'gzip':
    print("Response is gzip compressed")
    print(f"Compressed size: {len(response.content)} bytes")

# requests automatically decompresses
data = response.json()
```

### Testing in pytest

```python
import pytest
from fastapi.testclient import TestClient

def test_content_negotiation_without_compression(client: TestClient):
    """Test response without compression."""
    response = client.get("/api/client/state")

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json; charset=utf-8'
    assert 'Content-Encoding' not in response.headers
    assert response.json()['name'] == 'expected_value'

def test_content_negotiation_with_gzip(client: TestClient):
    """Test response with gzip compression."""
    response = client.get(
        "/api/client/state",
        headers={'Accept-Encoding': 'gzip'}
    )

    assert response.status_code == 200
    # TestClient automatically decompresses
    assert response.json()['name'] == 'expected_value'
```

## Best Practices

1. **Always use min_compress_size**: Set appropriate threshold (default 1024 bytes is good)
2. **Handle both formats**: Your endpoint should work with or without compression
3. **Test both paths**: Test with and without Accept-Encoding header
4. **Set Content-Length**: Always include Content-Length header (done automatically)
5. **Use framework helpers**: Prefer `fastapi_negotiated_response()` over manual
6. **Document endpoints**: Mention compression support in API documentation
7. **Monitor compression ratio**: Log compression effectiveness in production

## Performance Considerations

### Compression Overhead

- **Small responses** (<1KB): Compression overhead > savings, skip it
- **Medium responses** (1-10KB): Moderate savings, worthwhile if client supports
- **Large responses** (>10KB): Significant savings, always worth it

### Typical Compression Ratios

- **JSON with lots of text**: 60-80% compression
- **JSON with numbers**: 40-60% compression
- **Highly repetitive data**: 80-90% compression
- **Random/binary data**: Little to no compression

### Bandwidth Savings Example

```
Original JSON:     5,234 bytes
Gzipped:          1,456 bytes
Savings:          72% (3,778 bytes)
Transfer time:    72% faster on slow connections
```

## Migration Guide

### Updating Existing Endpoints

**Before:**
```python
@app.get("/api/client/state")
async def get_client_state():
    async with AareguruClient() as client:
        return client.to_dict()
```

**After:**
```python
@app.get("/api/client/state")
async def get_client_state(
    accept_encoding: Optional[str] = Header(None)
):
    async with AareguruClient() as client:
        return fastapi_negotiated_response(client, accept_encoding)
```

Changes:
1. Added `accept_encoding` parameter from Header
2. Return `fastapi_negotiated_response()` instead of `to_dict()`
3. Endpoint now supports compression automatically

## Troubleshooting

### Content Not Being Compressed

**Possible causes:**
1. Content too small (< min_compress_size)
2. Client didn't send Accept-Encoding header
3. Content already compressed or binary

**Solution:**
- Check content size
- Verify Accept-Encoding header in request
- Lower min_compress_size threshold if needed

### Clients Can't Decompress

**Possible causes:**
1. Client doesn't support gzip
2. Content-Encoding header missing
3. Double compression

**Solution:**
- Ensure Content-Encoding header is set
- Test with curl --compressed
- Check client HTTP library supports gzip

### Performance Issues

**Possible causes:**
1. Compressing small responses
2. Compressing already-compressed data
3. Too low compression threshold

**Solution:**
- Increase min_compress_size to 2048 or 4096
- Profile compression overhead
- Consider caching compressed responses

## Examples from MCP Servers

### aareguru-mcp Example

```python
from aareguru_mcp.client import AareguruClient
from swiss_ai_mcp_commons.http.integration import fastapi_negotiated_response

@app.get("/api/client/cache-info")
async def get_cache_info(accept_encoding: Optional[str] = Header(None)):
    """Get client cache information with compression support."""
    async with AareguruClient() as client:
        return fastapi_negotiated_response(
            client,
            accept_encoding=accept_encoding,
            min_compress_size=512  # Lower threshold for cache info
        )
```

### open-meteo-mcp Example

```python
from open_meteo_mcp.client import OpenMeteoClient
from swiss_ai_mcp_commons.http.integration import fastapi_negotiated_response

@app.get("/api/client/status")
async def get_client_status(accept_encoding: Optional[str] = Header(None)):
    """Get weather client status with compression."""
    client = OpenMeteoClient()
    return fastapi_negotiated_response(
        client,
        accept_encoding=accept_encoding
    )
```

## Further Reading

- [RFC 7231 - HTTP Content Negotiation](https://tools.ietf.org/html/rfc7231#section-5.3)
- [RFC 7230 - HTTP Message Format](https://tools.ietf.org/html/rfc7230)
- [MDN - Content Negotiation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Content_negotiation)
