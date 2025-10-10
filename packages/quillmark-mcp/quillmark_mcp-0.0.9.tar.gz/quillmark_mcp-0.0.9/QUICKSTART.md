# Quick Start Guide

This guide will help you get started with the Quillmark MCP server quickly.

## Installation

```bash
# Install from source
git clone https://github.com/nibsbin/quillmark-mcp.git
cd quillmark-mcp
pip install -e .
```

## Running the Server

### As a Python module

```bash
python -m quillmark_mcp
```

### Using the example script

```bash
python example.py
```

This will demonstrate all 6 MCP tools:
1. `list_quills` - List available templates
2. `get_quill_info` - Get template details
3. `get_markdown_template` - Get example markdown
4. `list_markdown_templates` - List markdown templates from manifest
5. `validate_frontmatter` - Validate document structure
6. `render_document` - Render to PDF/SVG
7. `save_rendered_file` - Save rendered documents to local filesystem

## MCP Client Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "quillmark": {
      "command": "python",
      "args": ["-m", "quillmark_mcp"]
    }
  }
}
```

On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Other MCP Clients

The server uses stdio transport and follows the MCP specification. Configure your client to run:

```bash
python -m quillmark_mcp
```

## Example Usage

### 1. Discover Templates

Ask the AI: "What document templates are available?"

The AI will call `list_quills()` and show you available templates.

### 2. Create a Document

Ask the AI: "Help me create a document using taro template"

The AI will:
1. Call `get_quill_info("taro")` to learn requirements
2. Call `get_markdown_template("taro")` for an example
3. Help you fill in the frontmatter fields
4. Call `validate_frontmatter()` to check correctness
5. Call `render_document()` to generate the PDF
6. Call `save_rendered_file()` to save the PDF to your local filesystem

### 3. Fix Errors

If your document has errors, the AI will receive detailed diagnostics:

```json
{
  "valid": false,
  "errors": [
    {
      "severity": "ERROR",
      "message": "Required field 'recipient' is missing",
      "hint": "Add 'recipient: <value>' to your frontmatter"
    }
  ]
}
```

The AI can use these hints to help you fix the issues.

## Development

### Run Tests

```bash
pytest
```

### Lint Code

```bash
ruff check src/
```

### Type Check

```bash
mypy src/quillmark_mcp
```

## Architecture

The server is organized as follows:

- `server.py` - Main MCP server setup and tool handlers
- `models.py` - Pydantic data models for all types
- `quill_loader.py` - Loads quills from tonguetoquill-collection
- `tools/` - Individual tool implementations (currently in server.py)
- `__main__.py` - Entry point for running as a module

## Current Status

The implementation uses actual quills from the tonguetoquill-collection repository:
- ✓ Quill loading from tonguetoquill-collection git subtree
- ✓ Template discovery and metadata
- ✓ All 7 MCP tools working
- ✓ File saving capability for local users

**Next steps for full production:**
1. Implement frontmatter schema extraction from Quill.toml `[fields]` section
2. Add actual PDF/SVG rendering via Quillmark package
3. Add comprehensive error handling
4. Extend quill collection with more templates

## Need Help?

- Read the [README](README.md) for full documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Review the [design document](designs/OVERALL.md) for architecture details
