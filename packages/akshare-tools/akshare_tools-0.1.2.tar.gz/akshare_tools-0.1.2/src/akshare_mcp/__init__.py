"""AKShare MCP Server

A Model Context Protocol server for accessing Chinese stock market data via AKShare.
"""

__version__ = "0.1.2"
__author__ = "Fanfei Gao"
__email__ = "gfanfei@gmail.com"

from .server import mcp, main

__all__ = ["mcp", "main", "__version__"]