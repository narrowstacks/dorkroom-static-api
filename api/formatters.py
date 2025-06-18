#!/usr/bin/env python3
"""
formatters.py

Formatting utilities for the Dorkroom Static API client.
"""

from typing import List
from .types import Film, Developer


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
            f"📷 {f.brand} {f.name} (ISO {int(f.isoSpeed)})",
            f"   ID: {f.id}",
            f"   Color: {f.colorType}",
            f"   Discontinued: {'Yes' if f.discontinued != 0 else 'No'}",
        ]
        if f.description:
            desc = f.description if len(f.description) <= 200 else f.description[:200] + "..."
            lines.append(f"   Desc: {desc}")
        if f.manufacturerNotes:
            lines.append(f"   Notes: {', '.join(f.manufacturerNotes)}")
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
            f"   Type: {d.type} for {d.filmOrPaper}",
            f"   Discontinued: {'Yes' if d.discontinued != 0 else 'No'}",
        ]
        if d.workingLifeHours is not None:
            hrs = d.workingLifeHours
            days, rem = divmod(hrs, 24)
            wl = f"{days}d {rem}h" if days else f"{rem}h"
            lines.append(f"   Working life: {wl}")
        if d.stockLifeMonths:
            lines.append(f"   Stock life: {d.stockLifeMonths} months")
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