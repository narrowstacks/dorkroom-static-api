#!/usr/bin/env python3
"""
client.py

Main client class for the Dorkroom Static API.
"""

import json
import logging
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin
from urllib3.util.retry import Retry

from .types import Film, Developer, Combination
from .exceptions import DataFetchError, DataParseError, DataNotLoadedError
from .protocols import HTTPTransport

# Try rapidfuzz for fuzzy matching
try:
    from rapidfuzz import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False


class DorkroomClient:
    """Main client for interacting with the Dorkroom Static API.
    
    This client provides methods to fetch film stocks, developers, and 
    development combinations from the Dorkroom Static API. It features:
    - Automatic retries and timeouts
    - Indexed lookups for O(1) performance
    - Optional fuzzy searching
    - Comprehensive error handling
    
    Attributes:
        base_url: Base URL for the API
        timeout: Request timeout in seconds
        session: Configured requests session
        transport: HTTP transport (for dependency injection)
        logger: Logger instance
    """
    
    def __init__(
        self,
        base_url: str = "https://raw.githubusercontent.com/narrowstacks/dorkroom-static-api/camelCase/",
        timeout: float = 10.0,
        max_retries: int = 3,
        transport: HTTPTransport = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the DorkroomClient.
        
        Args:
            base_url: Base URL for the API endpoints
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            transport: Custom HTTP transport (for testing)
            logger: Custom logger instance
        """
        self.base_url = base_url
        self.timeout = timeout

        # HTTP session with retries
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=0.3,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        # Allow injecting a custom transport for testing
        self.transport = transport or self.session

        # Logger
        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
            self.logger.addHandler(h)
        self.logger.setLevel(logging.INFO)

        # Data storage
        self._films: List[Film] = []
        self._devs: List[Developer] = []
        self._combinations: List[Combination] = []
        self._loaded = False

        # Indexes for O(1) lookup
        self._film_index: Dict[str, Film] = {}
        self._dev_index: Dict[str, Developer] = {}
        self._comb_index: Dict[str, Combination] = {}

        if not FUZZY_AVAILABLE:
            self.logger.warning("No fuzzy library available; fuzzy searches disabled.")

    def _fetch(self, filename: str) -> Any:
        """Fetch and parse a JSON file from the API.
        
        Args:
            filename: Name of the JSON file to fetch
            
        Returns:
            Any: Parsed JSON data
            
        Raises:
            DataFetchError: If HTTP request fails
            DataParseError: If JSON parsing fails
        """
        url = urljoin(self.base_url, filename)
        try:
            self.logger.debug(f"GET {url}")
            resp = self.transport.get(url, timeout=self.timeout)
            resp.raise_for_status()
        except Exception as e:
            raise DataFetchError(f"Failed to fetch {filename}: {e}") from e

        try:
            return resp.json()
        except json.JSONDecodeError as e:
            raise DataParseError(f"Invalid JSON in {filename}: {e}") from e

    def load_all(self) -> None:
        """Fetch and parse all JSON data, building internal indexes.
        
        This method must be called before using any other client methods.
        It fetches film stocks, developers, and development combinations
        from the API and builds internal indexes for fast lookups.
        
        Raises:
            DataFetchError: If any HTTP request fails
            DataParseError: If any JSON parsing fails
        """
        raw_films = self._fetch("film_stocks.json")
        raw_devs = self._fetch("developers.json")
        raw_combos = self._fetch("development_combinations.json")

        self._films = [Film(**f) for f in raw_films]
        self._devs = [Developer(**d) for d in raw_devs]
        self._combinations = [Combination(**c) for c in raw_combos]

        # Build indexes
        self._film_index = {f.id: f for f in self._films}
        self._dev_index = {d.id: d for d in self._devs}
        self._comb_index = {c.id: c for c in self._combinations}

        self._loaded = True
        self.logger.info(
            f"Loaded {len(self._films)} films, "
            f"{len(self._devs)} developers, "
            f"{len(self._combinations)} combinations."
        )

    def _ensure_loaded(self):
        """Ensure data has been loaded before performing operations.
        
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        if not self._loaded:
            raise DataNotLoadedError("Call load_all() before using the client.")

    @lru_cache(maxsize=None)
    def get_film(self, film_id: str) -> Optional[Film]:
        """Get a film by its ID.
        
        Args:
            film_id: The unique ID of the film
            
        Returns:
            Optional[Film]: The film object if found, None otherwise
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        self._ensure_loaded()
        return self._film_index.get(film_id)

    @lru_cache(maxsize=None)
    def get_developer(self, dev_id: str) -> Optional[Developer]:
        """Get a developer by its ID.
        
        Args:
            dev_id: The unique ID of the developer
            
        Returns:
            Optional[Developer]: The developer object if found, None otherwise
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        self._ensure_loaded()
        return self._dev_index.get(dev_id)

    def list_combinations_for_film(self, film_id: str) -> List[Combination]:
        """Get all development combinations for a specific film.
        
        Args:
            film_id: The unique ID of the film
            
        Returns:
            List[Combination]: List of combinations using this film
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        self._ensure_loaded()
        return [c for c in self._combinations if c.filmStockId == film_id]

    def list_combinations_for_developer(self, dev_id: str) -> List[Combination]:
        """Get all development combinations for a specific developer.
        
        Args:
            dev_id: The unique ID of the developer
            
        Returns:
            List[Combination]: List of combinations using this developer
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        self._ensure_loaded()
        return [c for c in self._combinations if c.developerId == dev_id]

    def search_films(self, query: str, colorType: Optional[str] = None) -> List[Film]:
        """Search films by name or brand using substring matching.
        
        Args:
            query: Search term to match against film name and brand
            colorType: Optional filter by color type (e.g., "Color", "B&W")
            
        Returns:
            List[Film]: List of matching films
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        self._ensure_loaded()
        q = query.lower()
        return [
            f for f in self._films
            if (q in f.name.lower() or q in f.brand.lower())
            and (colorType is None or f.colorType == colorType)
        ]

    def fuzzy_search(
        self,
        items: List[Any],
        key_funcs: List[Callable[[Any], str]],
        query: str,
        limit: int = 10,
        threshold: float = 60.0,
    ) -> List[Any]:
        """Generic fuzzy search using rapidfuzz.
        
        This method performs fuzzy string matching against multiple text fields
        from each item using the provided key functions.
        
        Args:
            items: List of items to search through
            key_funcs: List of functions to extract searchable text from each item
            query: Search query string
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0-100) to include in results
            
        Returns:
            List[Any]: List of matching items, sorted by relevance score
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        self._ensure_loaded()
        if not FUZZY_AVAILABLE:
            self.logger.warning("Fuzzy search not available; returning simple search.")
            return items[:limit]

        scores = []
        qi = query.lower()
        for item in items:
            text = " ".join(fn(item).lower() for fn in key_funcs)
            # Use token_sort_ratio for primary scoring (handles reordered words well)
            # But also check partial_ratio for substring matches
            token_score = fuzz.token_sort_ratio(qi, text)
            partial_score = fuzz.partial_ratio(qi, text)
            
            # Weight token_sort_ratio higher, but boost with partial_ratio for substring matches
            if partial_score > 80:  # Strong substring match
                score = max(token_score, partial_score * 0.9)  # Slight penalty for partial matches
            else:
                score = token_score
                
            if score >= threshold:
                scores.append((score, item))
        scores.sort(reverse=True, key=lambda x: x[0])
        return [it for _, it in scores[:limit]]

    def fuzzy_search_films(self, query: str, limit: int = 10) -> List[Film]:
        """Fuzzy search for films by name, brand, and description.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List[Film]: List of matching films, sorted by relevance
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        return self.fuzzy_search(
            self._films,
            key_funcs=[lambda f: f"{f.brand} {f.name}", lambda f: f.description or ""],
            query=query,
            limit=limit,
        )

    def fuzzy_search_devs(self, query: str, limit: int = 10) -> List[Developer]:
        """Fuzzy search for developers by manufacturer, name, and notes.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List[Developer]: List of matching developers, sorted by relevance
            
        Raises:
            DataNotLoadedError: If load_all() hasn't been called yet
        """
        return self.fuzzy_search(
            self._devs,
            key_funcs=[lambda d: f"{d.manufacturer} {d.name}", lambda d: d.notes or ""],
            query=query,
            limit=limit,
        ) 