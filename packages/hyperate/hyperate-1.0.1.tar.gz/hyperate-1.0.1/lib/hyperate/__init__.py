"""
HypeRate package for connecting to HypeRate WebSocket API.

This package provides a client for connecting to HypeRate's real-time heartbeat
and clip data service via WebSocket.
"""

# __init__.py for hyperate package
from .hyperate import Device, HypeRate

__version__ = "1.0.1"
__all__ = ["HypeRate", "Device"]
