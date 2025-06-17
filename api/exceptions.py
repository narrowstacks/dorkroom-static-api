#!/usr/bin/env python3
"""
exceptions.py

Custom exception classes for the Dorkroom Static API client.
"""


class DorkroomAPIError(Exception):
    """Base exception for Dorkroom API errors."""


class DataFetchError(DorkroomAPIError):
    """Raised when HTTP fetch fails."""


class DataParseError(DorkroomAPIError):
    """Raised when JSON parsing fails."""


class DataNotLoadedError(DorkroomAPIError):
    """Raised when data operations are attempted before loading.""" 