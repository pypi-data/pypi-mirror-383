"""
iCost App MCP Server

A Model Context Protocol (MCP) server for iCost application integration.
"""

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A Model Context Protocol server for iCost application"

# Package level imports
from .server import mcp

__all__ = ["mcp", "__version__"]