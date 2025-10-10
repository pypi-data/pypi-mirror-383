#!/usr/bin/env python3
"""Example script demonstrating Quillmark MCP server functionality."""

import asyncio
import json
import sys

# Add src to path for local testing
sys.path.insert(0, "src")

from quillmark_mcp import create_server


async def demonstrate_tools() -> None:
    """Demonstrate each MCP tool."""
    server = create_server()
    
    # Get the handlers (this is for demonstration purposes)
    # In a real MCP client, these would be called via JSON-RPC
    from quillmark_mcp.server import (
        handle_list_quills,
        handle_get_quill_info,
        handle_get_markdown_template,
        handle_list_markdown_templates,
        handle_validate_frontmatter,
        handle_render_document,
    )
    
    print("=" * 70)
    print("Quillmark MCP Server - Tool Demonstrations")
    print("=" * 70)
    
    # 1. List available quills
    print("\n1. LIST_QUILLS - Discover available templates")
    print("-" * 70)
    result = await handle_list_quills({})
    print(result[0].text)
    
    # 2. Get quill info
    print("\n2. GET_QUILL_INFO - Get detailed template information")
    print("-" * 70)
    result = await handle_get_quill_info({"quill_name": "taro"})
    info = json.loads(result[0].text)
    print(json.dumps(info, indent=2))
    
    # 4. List markdown templates
    print("\n4. LIST_MARKDOWN_TEMPLATES - List available markdown templates")
    print("-" * 70)
    result = await handle_list_markdown_templates({})
    print(result[0].text)

    # 3. Get markdown template
    print("\n3. GET_MARKDOWN_TEMPLATE - Get example markdown")
    print("-" * 70)
    result = await handle_get_markdown_template({"template_name": "Taro Template"})
    print(result[0].text)



    # 5. Validate frontmatter - success case
    print("\n5. VALIDATE_FRONTMATTER - Check frontmatter (valid)")
    print("-" * 70)
    valid_markdown = """---
QUILL: taro
author: John Doe
ice_cream: Taro
title: "My Favorite Ice Cream"
---

I love Taro ice cream for its unique flavor and texture.
"""
    result = await handle_validate_frontmatter({"markdown": valid_markdown})
    validation = json.loads(result[0].text)
    print(json.dumps(validation, indent=2))

    # 6. Validate frontmatter - error case
    print("\n6. VALIDATE_FRONTMATTER - Check frontmatter (missing fields)")
    print("-" * 70)
    invalid_markdown = """---
QUILL: taro
author: John Doe
---

Missing some fields here.
"""
    result = await handle_validate_frontmatter({"markdown": invalid_markdown})
    validation = json.loads(result[0].text)
    print(json.dumps(validation, indent=2))

    # 7. Render document
    print("\n7. RENDER_DOCUMENT - Generate PDF")
    print("-" * 70)
    result = await handle_render_document({
        "markdown": valid_markdown,
        "output_format": "PDF"
    })
    render_result = json.loads(result[0].text)
    print(f"Success: {render_result.get('success')}")
    if render_result.get('success'):
        artifacts = render_result.get('artifacts', [])
        if artifacts:
            print(f"Generated {len(artifacts)} artifact(s)")
            for artifact in artifacts:
                print(f"  - Format: {artifact['format']}")
                print(f"  - Size: {artifact['size_bytes']} bytes")
                print(f"  - MIME: {artifact['mime_type']}")
                print(f"  - URI: {artifact.get('resource_uri')}")
    
    print("\n" + "=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demonstrate_tools())
