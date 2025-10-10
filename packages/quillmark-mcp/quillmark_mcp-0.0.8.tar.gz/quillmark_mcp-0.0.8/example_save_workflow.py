#!/usr/bin/env python
"""
Example demonstrating the save_rendered_file workflow.

This script shows how to:
1. Render a document
2. Extract the resource URI
3. Save the file to disk
"""

import asyncio
import json
import tempfile
from pathlib import Path


async def example_workflow():
    """Demonstrate the complete workflow."""
    
    print("=" * 60)
    print("Quillmark MCP Server - File Saving Example")
    print("=" * 60)
    
    # Step 1: Render a document
    print("\n📄 Step 1: Render a document")
    print("-" * 60)
    
    render_request = {
        "tool": "render_document",
        "arguments": {
            "markdown": """---
QUILL: taro
author: John Doe
title: Example Document
ice_cream: Taro
---

# My Example Document

This is a test document rendered using the taro template.
""",
            "output_format": "PDF"
        }
    }
    
    print("Request:")
    print(json.dumps(render_request, indent=2))
    
    # Simulated response from render_document
    render_response = {
        "success": True,
        "artifacts": [
            {
                "format": "PDF",
                "bytes_base64": "JVBERi0xLjcK...(truncated)",
                "mime_type": "application/pdf",
                "size_bytes": 12345,
                "resource_uri": "quillmark://render/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            }
        ]
    }
    
    print("\nResponse:")
    print(json.dumps(render_response, indent=2))
    
    # Step 2: Extract the resource URI
    print("\n🔗 Step 2: Extract resource URI")
    print("-" * 60)
    
    resource_uri = render_response["artifacts"][0]["resource_uri"]
    print(f"Resource URI: {resource_uri}")
    
    # Step 3: Save the file
    print("\n💾 Step 3: Save to filesystem")
    print("-" * 60)
    
    # Use a temporary directory for this example
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "example_document.pdf"
        
        save_request = {
            "tool": "save_rendered_file",
            "arguments": {
                "resource_uri": resource_uri,
                "file_path": str(output_path)
            }
        }
        
        print("Request:")
        print(json.dumps(save_request, indent=2))
        
        # Simulated response from save_rendered_file
        save_response = {
            "success": True,
            "file_path": str(output_path),
            "file_size": 12345,
            "mime_type": "application/pdf",
            "format": "PDF"
        }
        
        print("\nResponse:")
        print(json.dumps(save_response, indent=2))
        
        print(f"\n✅ File saved to: {output_path}")
        print(f"   Size: {save_response['file_size']} bytes")
        print(f"   Format: {save_response['format']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
The workflow is complete! Here's what happened:

1. We rendered a markdown document using the 'taro' template
2. The server returned a resource URI along with base64 data
3. We used the resource URI to save the file to disk
4. The file is now available at the specified path

In a real scenario with Claude Code:
- Claude would automatically handle these tool calls
- You would just ask "Create a document and save it to ~/Documents/memo.pdf"
- Claude would execute both steps and confirm the file was saved
""")


if __name__ == "__main__":
    asyncio.run(example_workflow())
