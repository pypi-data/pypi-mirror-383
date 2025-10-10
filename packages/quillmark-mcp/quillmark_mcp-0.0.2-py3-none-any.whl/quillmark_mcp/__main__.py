"""Main entry point for Quillmark MCP server."""

import asyncio

from quillmark_mcp import create_server


async def main() -> None:
    """Run the Quillmark MCP server."""
    server = create_server()

    # Run the server using stdio transport
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
