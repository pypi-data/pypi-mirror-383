# MCP Resources Implementation

This document describes the implementation of MCP Resources for rendered documents in the Quillmark MCP server.

## Overview

The MCP Resources feature replaces direct base64 returns with clean resource URIs, enabling better document management and reusability. Documents are now cached and can be accessed multiple times through the MCP resource protocol.

## Implementation Details

### 1. Core Components

#### Render Cache (`server.py`)
```python
RENDER_CACHE: dict[str, tuple[bytes, str]] = {}
MAX_CACHE_SIZE = 50  # Maximum number of documents to cache
```

The render cache stores rendered documents with:
- **Key**: UUID string (e.g., `"abc-123-def-456"`)
- **Value**: Tuple of `(bytes, mime_type)`
  - `bytes`: Raw document bytes (PDF or SVG)
  - `mime_type`: MIME type string (`"application/pdf"` or `"image/svg+xml"`)

#### Cache Management
- **Size Limit**: Maximum 50 documents
- **Eviction Policy**: FIFO (First In, First Out)
- When cache is full, the oldest entry is removed before adding a new one

### 2. Data Model Changes

#### Artifact Model (`models.py`)
```python
class Artifact(BaseModel):
    format: str
    bytes_base64: str
    mime_type: str
    size_bytes: int
    resource_uri: str | None = None  # NEW FIELD
```

The `resource_uri` field is optional to maintain backward compatibility. When present, it contains a URI like `quillmark://render/{uuid}`.

### 3. MCP Resource Handlers

#### List Resources (`@server.list_resources()`)
Returns all cached rendered documents as Resource objects:

```python
@server.list_resources()
async def list_resources() -> list[Resource]:
    """List all cached rendered documents as resources."""
```

**Returns**: List of `Resource` objects with:
- `uri`: `quillmark://render/{uuid}`
- `name`: Descriptive name (e.g., "Rendered document (pdf)")
- `mimeType`: Document MIME type

#### Read Resource (`@server.read_resource()`)
Retrieves a cached document by URI:

```python
@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a cached rendered document resource."""
```

**Parameters**:
- `uri`: Resource URI in format `quillmark://render/{uuid}`

**Returns**: Base64-encoded document bytes

**Errors**:
- Raises `ValueError` if URI format is invalid
- Raises `ValueError` if resource not found in cache

### 4. Render Document Changes

The `handle_render_document()` function now:

1. **Generates UUID** for each artifact
   ```python
   render_id = str(uuid.uuid4())
   ```

2. **Enforces cache size limit** before storing
   ```python
   if len(RENDER_CACHE) >= MAX_CACHE_SIZE:
       oldest_key = next(iter(RENDER_CACHE))
       del RENDER_CACHE[oldest_key]
   ```

3. **Stores in cache** with UUID key
   ```python
   RENDER_CACHE[render_id] = (artifact_bytes, mime_type)
   ```

4. **Includes resource URI** in artifact response
   ```python
   resource_uri = f"quillmark://render/{render_id}"
   artifact = Artifact(
       # ... other fields ...
       resource_uri=resource_uri,
   )
   ```

## Usage Examples

### Example 1: Rendering a Document

**Request**:
```json
{
  "tool": "render_document",
  "arguments": {
    "markdown": "---\nQUILL: taro\n---\n# Hello",
    "output_format": "PDF"
  }
}
```

**Response**:
```json
{
  "success": true,
  "artifacts": [
    {
      "format": "PDF",
      "bytes_base64": "JVBERi0xLjcK...",
      "mime_type": "application/pdf",
      "size_bytes": 12345,
      "resource_uri": "quillmark://render/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
  ]
}
```

### Example 2: Listing Resources

**Request**: Call `list_resources()`

**Response**:
```json
[
  {
    "uri": "quillmark://render/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Rendered document (pdf)",
    "mimeType": "application/pdf"
  },
  {
    "uri": "quillmark://render/9876fedc-ba09-8765-4321-0fedcba98765",
    "name": "Rendered document (svg)",
    "mimeType": "image/svg+xml"
  }
]
```

### Example 3: Reading a Resource

**Request**:
```
read_resource("quillmark://render/a1b2c3d4-e5f6-7890-abcd-ef1234567890")
```

**Response**:
```
"JVBERi0xLjcKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCj..."
```

## Benefits

1. **Clean URIs**: AI agents receive `quillmark://render/{uuid}` instead of large base64 strings
2. **Persistence**: Documents can be read multiple times without re-rendering
3. **Memory Management**: FIFO eviction prevents unbounded growth
4. **Backward Compatible**: base64 data still included in initial response
5. **MCP Compliance**: Standard resource protocol implementation

## Testing

Tests are included in `tests/test_server.py`:

- `test_artifact_with_resource_uri()`: Validates Artifact model changes
- `test_render_cache_constants()`: Verifies cache configuration
- `test_resource_uri_format()`: Validates URI structure and UUID format

## Future Enhancements

Potential improvements:
- **TTL/Expiration**: Add time-based cache expiration
- **Cache Clearing Tool**: MCP tool to manually clear cache
- **Size-Based Eviction**: Evict by total byte size instead of count
- **Persistent Cache**: Store cache to disk for server restarts
- **Resource Metadata**: Include render timestamp, quill name in Resource objects
