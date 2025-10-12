"""
mcpadserver - Ad monetization SDK for MCP servers

Copyright (c) 2025 mcpadserver
Licensed under MIT License
"""

__version__ = "0.1.0"

from .client import AdClient
from .types import AdRequest, AdResponse

__all__ = ["AdClient", "AdRequest", "AdResponse"]
