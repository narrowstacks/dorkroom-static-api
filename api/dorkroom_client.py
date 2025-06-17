#!/usr/bin/env python3
"""
dorkroom_client.py

A robust, typed, and configurable Python client for the
Dorkroom Static API. Features:
 - requests.Session with retries & timeouts
 - dataclasses for Film, Developer, Combination
 - O(1) lookups via indexed dicts
 - optional fuzzy search via rapidfuzz
 - separation of CLI formatting
 - easy-to-test, dependency-injectable HTTP transport
"""

import json
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Protocol

import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin
from urllib3.util.retry import Retry

# Try rapidfuzz for fuzzy matching
try:
    from rapidfuzz import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False


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


@dataclass
class Film:
    """Represents a film stock with all its properties.
    
    Attributes:
        id: Unique identifier for the film
        name: Display name of the film
        brand: Manufacturer/brand name
        iso_speed: ISO speed rating
        color_type: Type of film (color, b&w, etc.)
        description: Optional detailed description
        discontinued: Whether film is discontinued (0=no, 1=yes)
        manufacturer_notes: List of notes from manufacturer
        grain_structure: Description of grain characteristics
        reciprocity_failure: Information about reciprocity failure
    """
    id: str
    name: str
    brand: str
    iso_speed: float
    color_type: str
    description: Optional[str] = None
    discontinued: int = 0
    manufacturer_notes: List[str] = field(default_factory=list)
    grain_structure: Optional[str] = None
    reciprocity_failure: Optional[str] = None


@dataclass
class Developer:
    """Represents a film/paper developer with all its properties.
    
    Attributes:
        id: Unique identifier for the developer
        name: Display name of the developer
        manufacturer: Manufacturer/brand name
        type: Type of developer (e.g., "Black & White Film")
        film_or_paper: Whether for film or paper development
        dilutions: List of available dilution ratios
        working_life_hours: Working solution lifetime in hours
        stock_life_months: Stock solution lifetime in months
        notes: Additional notes about the developer
        discontinued: Whether developer is discontinued (0=no, 1=yes)
        mixing_instructions: How to prepare the developer
        safety_notes: Safety information and warnings
        datasheet_url: URLs to manufacturer datasheets
    """
    id: str
    name: str
    manufacturer: str
    type: str
    film_or_paper: str
    dilutions: List[Dict[str, Any]] = field(default_factory=list)
    working_life_hours: Optional[int] = None
    stock_life_months: Optional[int] = None
    notes: Optional[str] = None
    discontinued: int = 0
    mixing_instructions: Optional[str] = None
    safety_notes: Optional[str] = None
    datasheet_url: Optional[List[str]] = None


@dataclass
class Combination:
    """Represents a film+developer combination with development parameters.
    
    Attributes:
        id: Unique identifier for the combination
        name: Display name describing the combination
        film_stock_id: ID of the film used
        developer_id: ID of the developer used
        temperature_f: Development temperature in Fahrenheit
        time_minutes: Development time in minutes
        shooting_iso: ISO at which the film was shot
        push_pull: Push/pull processing offset (0=normal, +1=push 1 stop, etc.)
        agitation_schedule: Description of agitation pattern
        notes: Additional development notes
        dilution_id: ID of specific dilution used
        custom_dilution: Custom dilution ratio if not standard
    """
    id: str
    name: str
    film_stock_id: str
    developer_id: str
    temperature_f: float
    time_minutes: float
    shooting_iso: float
    push_pull: int = 0
    agitation_schedule: Optional[str] = None
    notes: Optional[str] = None
    dilution_id: Optional[int] = None
    custom_dilution: Optional[str] = None


class DorkroomAPIError(Exception):
    """Base exception for Dorkroom API errors."""


class DataFetchError(DorkroomAPIError):
    """Raised when HTTP fetch fails."""


class DataParseError(DorkroomAPIError):
    """Raised when JSON parsing fails."""


class DataNotLoadedError(DorkroomAPIError):
    """Raised when data operations are attempted before loading."""


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
        base_url: str = "https://raw.githubusercontent.com/narrowstacks/dorkroom-static-api/main/",
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
        return [c for c in self._combinations if c.film_stock_id == film_id]

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
        return [c for c in self._combinations if c.developer_id == dev_id]

    def search_films(self, query: str, color_type: Optional[str] = None) -> List[Film]:
        """Search films by name or brand using substring matching.
        
        Args:
            query: Search term to match against film name and brand
            color_type: Optional filter by color type (e.g., "Color", "B&W")
            
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
            and (color_type is None or f.color_type == color_type)
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


# --- CLI formatting moved out of core client ---

class CLIFormatter:
    """Utility class for formatting data objects for CLI display."""
    
    @staticmethod
    def format_film(f: Film) -> List[str]:
        """Format a Film object for CLI display.
        
        Args:
            f: Film object to format
            
        Returns:
            List[str]: List of formatted lines for display
        """
        lines = [
            f"📷 {f.brand} {f.name} (ISO {int(f.iso_speed)})",
            f"   ID: {f.id}",
            f"   Color: {f.color_type}",
            f"   Discontinued: {'Yes' if f.discontinued != 0 else 'No'}",
        ]
        if f.description:
            desc = f.description if len(f.description) <= 200 else f.description[:200] + "..."
            lines.append(f"   Desc: {desc}")
        if f.manufacturer_notes:
            lines.append(f"   Notes: {', '.join(f.manufacturer_notes)}")
        return lines

    @staticmethod
    def format_dev(d: Developer) -> List[str]:
        """Format a Developer object for CLI display.
        
        Args:
            d: Developer object to format
            
        Returns:
            List[str]: List of formatted lines for display
        """
        lines = [
            f"🧪 {d.manufacturer} {d.name}",
            f"   ID: {d.id}",
            f"   Type: {d.type} for {d.film_or_paper}",
            f"   Discontinued: {'Yes' if d.discontinued != 0 else 'No'}",
        ]
        if d.working_life_hours is not None:
            hrs = d.working_life_hours
            days, rem = divmod(hrs, 24)
            wl = f"{days}d {rem}h" if days else f"{rem}h"
            lines.append(f"   Working life: {wl}")
        if d.stock_life_months:
            lines.append(f"   Stock life: {d.stock_life_months} months")
        if d.dilutions:
            lines.append(f"   Dilutions: {len(d.dilutions)} available")
        return lines

    @staticmethod
    def print_lines(lines: List[str]) -> None:
        """Print a list of lines to stdout.
        
        Args:
            lines: List of strings to print
        """
        for ln in lines:
            print(ln)


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