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
        isoSpeed: ISO speed rating
        colorType: Type of film (color, b&w, etc.)
        description: Optional detailed description
        discontinued: Whether film is discontinued (0=no, 1=yes)
        manufacturerNotes: List of notes from manufacturer
        grainStructure: Description of grain characteristics
        reciprocityFailure: Information about reciprocity failure
        staticImageURL: URL to product image of the film
        dateAdded: ISO timestamp when the film was added to the database
    """
    id: str
    name: str
    brand: str
    isoSpeed: float
    colorType: str
    description: Optional[str] = None
    discontinued: int = 0
    manufacturerNotes: List[str] = field(default_factory=list)
    grainStructure: Optional[str] = None
    reciprocityFailure: Optional[str] = None
    staticImageURL: Optional[str] = None
    dateAdded: Optional[str] = None


@dataclass
class Developer:
    """Represents a film/paper developer with all its properties.
    
    Attributes:
        id: Unique identifier for the developer
        name: Display name of the developer
        manufacturer: Manufacturer/brand name
        type: Type of developer (e.g., "Black & White Film")
        filmOrPaper: Whether for film or paper development
        dilutions: List of available dilution ratios
        workingLifeHours: Working solution lifetime in hours
        stockLifeMonths: Stock solution lifetime in months
        notes: Additional notes about the developer
        discontinued: Whether developer is discontinued (0=no, 1=yes)
        mixingInstructions: How to prepare the developer
        safetyNotes: Safety information and warnings
        datasheetUrl: URLs to manufacturer datasheets
    """
    id: str
    name: str
    manufacturer: str
    type: str
    filmOrPaper: str
    dilutions: List[Dict[str, Any]] = field(default_factory=list)
    workingLifeHours: Optional[int] = None
    stockLifeMonths: Optional[int] = None
    notes: Optional[str] = None
    discontinued: int = 0
    mixingInstructions: Optional[str] = None
    safetyNotes: Optional[str] = None
    datasheetUrl: Optional[List[str]] = None


@dataclass
class Combination:
    """Represents a film+developer combination with development parameters.
    
    Attributes:
        id: Unique identifier for the combination
        name: Display name describing the combination
        filmStockId: ID of the film used
        developerId: ID of the developer used
        temperatureF: Development temperature in Fahrenheit
        timeMinutes: Development time in minutes
        shootingIso: ISO at which the film was shot
        pushPull: Push/pull processing offset (0=normal, +1=push 1 stop, etc.)
        agitationSchedule: Description of agitation pattern
        notes: Additional development notes
        dilutionId: ID of specific dilution used
        customDilution: Custom dilution ratio if not standard
    """
    id: str
    name: str
    filmStockId: str
    developerId: str
    temperatureF: float
    timeMinutes: float
    shootingIso: float
    pushPull: int = 0
    agitationSchedule: Optional[str] = None
    notes: Optional[str] = None
    dilutionId: Optional[int] = None
    customDilution: Optional[str] = None 