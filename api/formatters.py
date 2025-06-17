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