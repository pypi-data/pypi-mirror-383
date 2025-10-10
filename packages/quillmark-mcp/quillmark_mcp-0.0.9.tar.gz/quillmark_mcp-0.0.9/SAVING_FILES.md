# Saving Rendered Files Locally

## Overview

When running the Quillmark MCP server locally with Claude Code or other MCP clients, you can now save rendered documents directly to your filesystem using the `save_rendered_file` tool.

## Workflow Diagram

### The Complete Flow

```
┌──────────────────┐
│   User/Claude    │
└────────┬─────────┘
         │ 1. render_document
         ▼
┌──────────────────┐
│  MCP Server      │
│  - Renders doc   │
│  - Stores in     │
│    cache         │
│  - Returns:      │
│    • base64      │
│    • resource_uri│
└────────┬─────────┘
         │ 2. Response
         ▼
┌──────────────────┐
│   User/Claude    │
└────────┬─────────┘
         │ 3. save_rendered_file(uri, path)
         ▼
┌──────────────────┐
│  MCP Server      │
│  - Reads from    │
│    cache         │
│  - Writes to     │
│    filesystem    │
└────────┬─────────┘
         │ 4. Success
         ▼
┌──────────────────┐
│  ~/Documents/    │
│  document.pdf    │
└──────────────────┘
```

## Workflow

1. **Render a document** using `render_document` tool
2. **Extract the `resource_uri`** from the response
3. **Save the file** using `save_rendered_file` with the resource URI

## Example Usage

### Step 1: Render a Document

```json
{
  "tool": "render_document",
  "arguments": {
    "markdown": "---\nQUILL: taro\nauthor: John\ntitle: My Document\n---\n# Content",
    "output_format": "PDF"
  }
}
```

**Response:**
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

### Step 2: Save to Filesystem

```json
{
  "tool": "save_rendered_file",
  "arguments": {
    "resource_uri": "quillmark://render/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "file_path": "/Users/john/Documents/my_document.pdf"
  }
}
```

**Response:**
```json
{
  "success": true,
  "file_path": "/Users/john/Documents/my_document.pdf",
  "file_size": 12345,
  "mime_type": "application/pdf",
  "format": "PDF"
}
```

## Features

- **Automatic Directory Creation**: Parent directories are created automatically if they don't exist
- **Path Expansion**: Supports `~` for home directory (e.g., `~/Documents/file.pdf`)
- **Path Resolution**: Automatically resolves relative paths to absolute paths
- **Error Handling**: Provides detailed error messages for permission issues, invalid URIs, etc.

## Error Scenarios

### Invalid Resource URI

```json
{
  "success": false,
  "error_type": "InvalidResourceURI",
  "error_message": "Invalid resource URI format: invalid://uri"
}
```

### Resource Not Found

```json
{
  "success": false,
  "error_type": "ResourceNotFound",
  "error_message": "Resource not found in cache: quillmark://render/nonexistent-uuid"
}
```

### Permission Denied

```json
{
  "success": false,
  "error_type": "PermissionError",
  "error_message": "Permission denied writing to /root/file.pdf: ..."
}
```

## Cache Behavior

- Rendered documents are stored in an in-memory cache (up to 50 documents)
- Cache uses FIFO (First In, First Out) eviction when full
- Resource URIs remain valid until evicted from cache
- If you need to save a file, do it soon after rendering

## Claude Code Integration

When using Claude Code with this MCP server:

1. Ask Claude to render a document
2. Claude will automatically use `render_document` and receive the resource URI
3. Ask Claude to save the file (e.g., "Save this to ~/Documents/memo.pdf")
4. Claude will use `save_rendered_file` to write the file to your filesystem
5. You can then open the file directly from your file system

## Example Conversation with Claude

```
User: "Create a memo using the taro template with author 'John Doe' and title 'Q1 Report'"

Claude: [Uses render_document tool]
"I've created your memo. Here's the rendered PDF."

User: "Save it to ~/Documents/q1-report.pdf"

Claude: [Uses save_rendered_file tool]
"I've saved the PDF to /Users/john/Documents/q1-report.pdf (12.3 KB)"
```

## Technical Details

- Files are written as binary data (bytes)
- The MIME type determines the file format
- Supported formats: PDF (`application/pdf`) and SVG (`image/svg+xml`)
- No file size limits (other than system constraints)
- UTF-8 paths are supported

## Security Considerations

- The tool requires an absolute path or expandable path
- Parent directories are created with default permissions
- No validation of file extensions (user is responsible)
- Overwrites existing files without confirmation
- Runs with the permissions of the MCP server process
