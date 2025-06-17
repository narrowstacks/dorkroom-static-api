#!/usr/bin/env python3
"""
protocols.py

Protocol definitions for the Dorkroom Static API client.
"""

from typing import Protocol
import requests


class HTTPTransport(Protocol):
    """Protocol for HTTP transport layer dependency injection.
    
    This allows for easy testing by injecting mock transports.
    """
    
    def get(self, url: str, timeout: float) -> requests.Response:
        """Perform HTTP GET request.
        
        Args:
            url: The URL to request
            timeout: Request timeout in seconds
            
        Returns:
            requests.Response: The HTTP response object
        """
        ... 