#!/usr/bin/env python3
"""
types.py

Data types and dataclasses for the Dorkroom Static API client.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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