#!/usr/bin/env python3
"""
dorkroom_client.py

A robust, typed, and configurable Python client for the
Dorkroom Static API. This module provides backward compatibility
by re-importing all classes from the new modular structure.

For new code, consider importing directly from the specific modules:
- from .client import DorkroomClient
- from .types import Film, Developer, Combination
- from .formatters import CLIFormatter
- from .exceptions import DorkroomAPIError, etc.
"""

# Import all components from the new modular structure for backward compatibility
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


# Example usage:
if __name__ == "__main__":
    client = DorkroomClient()
    client.load_all()

    # Simple search
    films = client.search_films("tri-x")
    for f in films:
        CLIFormatter.print_lines(CLIFormatter.format_film(f))
        print()

    # Fuzzy search
    top = client.fuzzy_search_films("tri x", limit=5)
    for f in top:
        CLIFormatter.print_lines(CLIFormatter.format_film(f))
        print()