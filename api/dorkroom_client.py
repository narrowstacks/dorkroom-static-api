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

# Try rapidfuzz first, then fuzzywuzzy
try:
    from rapidfuzz import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    try:
        from fuzzywuzzy import fuzz
        FUZZY_AVAILABLE = True
    except ImportError:
        FUZZY_AVAILABLE = False


class HTTPTransport(Protocol):
    def get(self, url: str, timeout: float) -> requests.Response:
        ...


@dataclass
class Film:
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
    def __init__(
        self,
        base_url: str = "https://raw.githubusercontent.com/narrowstacks/dorkroom-static-api/main/",
        timeout: float = 10.0,
        max_retries: int = 3,
        transport: HTTPTransport = None,
        logger: Optional[logging.Logger] = None,
    ):
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
        """Fetch and parse all JSON, build indexes."""
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
        if not self._loaded:
            raise DataNotLoadedError("Call load_all() before using the client.")

    @lru_cache(maxsize=None)
    def get_film(self, film_id: str) -> Optional[Film]:
        self._ensure_loaded()
        return self._film_index.get(film_id)

    @lru_cache(maxsize=None)
    def get_developer(self, dev_id: str) -> Optional[Developer]:
        self._ensure_loaded()
        return self._dev_index.get(dev_id)

    def list_combinations_for_film(self, film_id: str) -> List[Combination]:
        self._ensure_loaded()
        return [c for c in self._combinations if c.film_stock_id == film_id]

    def list_combinations_for_developer(self, dev_id: str) -> List[Combination]:
        self._ensure_loaded()
        return [c for c in self._combinations if c.developer_id == dev_id]

    def search_films(self, query: str, color_type: Optional[str] = None) -> List[Film]:
        """Simple substring search."""
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
        """Generic fuzzy search using rapidfuzz/fuzzywuzzy."""
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
        return self.fuzzy_search(
            self._films,
            key_funcs=[lambda f: f"{f.brand} {f.name}", lambda f: f.description or ""],
            query=query,
            limit=limit,
        )

    def fuzzy_search_devs(self, query: str, limit: int = 10) -> List[Developer]:
        return self.fuzzy_search(
            self._devs,
            key_funcs=[lambda d: f"{d.manufacturer} {d.name}", lambda d: d.notes or ""],
            query=query,
            limit=limit,
        )


# --- CLI formatting moved out of core client ---

class CLIFormatter:
    @staticmethod
    def format_film(f: Film) -> List[str]:
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