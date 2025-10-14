"""DART MCP - Model Context Protocol server for DART (Dallas Area Rapid Transit) schedules."""

from . import gtfs
from .server import main

__version__ = "0.1.0"

# Expose key functions for library usage
__all__ = [
    "gtfs",
    "main",
]
