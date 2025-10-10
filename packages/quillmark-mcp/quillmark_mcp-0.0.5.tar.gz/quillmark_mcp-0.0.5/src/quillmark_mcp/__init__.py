"""Quillmark MCP Server - Model Context Protocol server for Quillmark."""

from .server import create_server
from importlib.metadata import version

__version__ = version("quillmark-mcp")
__all__ = ["create_server"]
