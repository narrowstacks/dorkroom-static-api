#!/usr/bin/env python3
"""
Dorkroom Static API Client

A robust, typed, and configurable Python client for the
Dorkroom Static API.
"""

# Import main classes and types
from .client import DorkroomClient
from .types import Film, Developer, Combination
from .exceptions import (
    DorkroomAPIError,
    DataFetchError,
    DataParseError,
    DataNotLoadedError,
)
from .formatters import CLIFormatter
from .protocols import HTTPTransport

# Version info
__version__ = "0.1.0"

# Public API
__all__ = [
    "DorkroomClient",
    "Film",
    "Developer", 
    "Combination",
    "CLIFormatter",
    "HTTPTransport",
    "DorkroomAPIError",
    "DataFetchError",
    "DataParseError",
    "DataNotLoadedError",
] 