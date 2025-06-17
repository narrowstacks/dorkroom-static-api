#!/usr/bin/env python3
"""
Test script for pulling and working with data from the Dorkroom Static API
Repository: https://github.com/narrowstacks/dorkroom-static-api
"""

import sys
import code
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Add the parent directory to the Python path to import from api module
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.dorkroom_client import DorkroomClient, CLIFormatter, Film, Developer, Combination


@dataclass
class SearchResult:
    """Container for fuzzy search results to maintain compatibility"""
    score: float
    item: Any


class DorkroomAPIWrapper:
    """Wrapper around DorkroomClient to maintain compatibility with existing test code"""
    
    def __init__(self):
        self.client = DorkroomClient()
        self.formatter = CLIFormatter()
        self._loaded = False
    
    def load_all_data(self):
        """Load all data - wrapper around client.load_all()"""
        self.client.load_all()
        self._loaded = True
    
    @property
    def film_stocks(self) -> List[Film]:
        """Access to films data"""
        return self.client._films
    
    @property
    def developers(self) -> List[Developer]:
        """Access to developers data"""
        return self.client._devs
    
    @property
    def development_combinations(self) -> List[Combination]:
        """Access to combinations data"""
        return self.client._combinations
    
    @property
    def formats(self) -> List[Dict]:
        """Placeholder for formats - not implemented in new client"""
        return []
    
    def search_films(self, query: str, color_type: Optional[str] = None) -> List[Film]:
        """Search films using the new client"""
        return self.client.search_films(query, color_type)
    
    def search_developers(self, query: str) -> List[Developer]:
        """Search developers - implementing since it doesn't exist in new client"""
        q = query.lower()
        return [
            d for d in self.client._devs
            if (q in d.name.lower() or q in d.manufacturer.lower())
        ]
    
    def fuzzy_search_films(self, query: str, limit: int = 10, color_type: Optional[str] = None) -> List[SearchResult]:
        """Fuzzy search films with compatibility wrapper"""
        films = self.client.fuzzy_search_films(query, limit)
        # Filter by color_type if specified
        if color_type:
            films = [f for f in films if f.color_type == color_type]
        # Wrap in SearchResult for compatibility
        return [SearchResult(score=100.0, item=film) for film in films]
    
    def fuzzy_search_developers(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Fuzzy search developers with compatibility wrapper"""
        devs = self.client.fuzzy_search_devs(query, limit)
        # Wrap in SearchResult for compatibility  
        return [SearchResult(score=100.0, item=dev) for dev in devs]
    
    def get_film_by_id(self, film_id: str) -> Optional[Film]:
        """Get film by ID"""
        return self.client.get_film(film_id)
    
    def get_developer_by_id(self, dev_id: str) -> Optional[Developer]:
        """Get developer by ID"""
        return self.client.get_developer(dev_id)
    
    def get_combinations_for_film(self, film_id: str) -> List[Combination]:
        """Get combinations for a film"""
        return self.client.list_combinations_for_film(film_id)
    
    def display_film_info(self, film: Film):
        """Display film information using CLIFormatter"""
        lines = self.formatter.format_film(film)
        self.formatter.print_lines(lines)
    
    def display_developer_info(self, dev: Developer):
        """Display developer information using CLIFormatter"""
        lines = self.formatter.format_dev(dev)
        self.formatter.print_lines(lines)
    
    def display_combination_info(self, combo: Combination):
        """Display combination information"""
        film = self.get_film_by_id(combo.film_stock_id)
        dev = self.get_developer_by_id(combo.developer_id)
        
        film_name = f"{film.brand} {film.name}" if film else f"Film ID: {combo.film_stock_id}"
        dev_name = f"{dev.manufacturer} {dev.name}" if dev else f"Developer ID: {combo.developer_id}"
        
        lines = [
            f"⚗️  {combo.name}",
            f"   ID: {combo.id}",
            f"   Film: {film_name}",
            f"   Developer: {dev_name}",
            f"   Temperature: {combo.temperature_f}°F",
            f"   Time: {combo.time_minutes} minutes",
            f"   Shooting ISO: {int(combo.shooting_iso)}",
        ]
        
        if combo.push_pull != 0:
            push_pull_str = f"+{combo.push_pull}" if combo.push_pull > 0 else str(combo.push_pull)
            lines.append(f"   Push/Pull: {push_pull_str} stops")
        
        if combo.agitation_schedule:
            lines.append(f"   Agitation: {combo.agitation_schedule}")
        
        if combo.notes:
            lines.append(f"   Notes: {combo.notes}")
        
        self.formatter.print_lines(lines)
    
    def display_search_results(self, results: List[SearchResult]):
        """Display fuzzy search results"""
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result.score:.1f}")
            if isinstance(result.item, Film):
                self.display_film_info(result.item)
            elif isinstance(result.item, Developer):
                self.display_developer_info(result.item)
            else:
                print(f"   {result.item}")
    
    def _format_working_life(self, hours: int) -> str:
        """Format working life hours into a readable string"""
        if hours < 24:
            return f"{hours}h"
        else:
            days, rem_hours = divmod(hours, 24)
            if rem_hours == 0:
                return f"{days}d"
            else:
                return f"{days}d {rem_hours}h"


def run_sample_queries(api: DorkroomAPIWrapper):
    """Run sample queries to demonstrate the API functionality"""
    
    print("\n" + "="*60)
    print("SAMPLE QUERIES AND DEMONSTRATIONS")
    print("="*60)
    
    # Sample 1: Search for popular films
    print("\n1. 🔍 Searching for 'Tri-X' films:")
    trix_films = api.search_films("Tri-X")
    for film in trix_films[:3]:  # Show first 3 results
        api.display_film_info(film)
        print()
    
    # Sample 1b: Fuzzy search comparison
    print(f"\n1b. 🎯 Fuzzy search for 'tri-x' (with improved matching):")
    fuzzy_trix = api.fuzzy_search_films("tri-x", limit=3)
    api.display_search_results(fuzzy_trix)
    
    # Sample 2: Search for black and white films only
    print(f"\n2. 🔍 Searching for black and white films containing 'HP':")
    bw_films = api.search_films("HP", color_type="bw")
    for film in bw_films[:2]:  # Show first 2 results
        api.display_film_info(film)
        print()
    
    # Sample 2b: Fuzzy search with color filter
    print(f"\n2b. 🎯 Fuzzy search for 'kodak' black & white films:")
    fuzzy_bw = api.fuzzy_search_films("kodak", limit=3, color_type="bw")
    api.display_search_results(fuzzy_bw)
    
    # Sample 3: Search for developers
    print(f"\n3. 🔍 Searching for 'HC-110' developer:")
    hc110_devs = api.search_developers("HC-110")
    for dev in hc110_devs[:1]:  # Show first result
        api.display_developer_info(dev)
        print()
    
    # Sample 3b: Fuzzy developer search
    print(f"\n3b. 🎯 Fuzzy search for 'd76' developers:")
    fuzzy_devs = api.fuzzy_search_developers("d76", limit=3)
    api.display_search_results(fuzzy_devs)
    if fuzzy_devs:
        print("\nDetailed info for first fuzzy result (showing improved working life display):")
        api.display_developer_info(fuzzy_devs[0].item)
    
    # Sample 4: Find development combinations for a specific film
    print(f"\n4. 🔍 Searching for Tri-X film for combination demo...")
    tri_x_results = api.fuzzy_search_films("tri x", limit=1)    
    # Debug: Let's test what the fuzzy search is actually comparing
    if hasattr(api.client, 'fuzzy_search') and len(api.film_stocks) > 0:
        # Find the Tri-X film manually to see what text is being compared
        trix_film = None
        for film in api.film_stocks:
            if "tri-x" in film.name.lower():
                trix_film = film
                break
        if trix_film:
            search_text = f"{trix_film.brand} {trix_film.name}".lower()
            # Test fuzzy score manually
            try:
                from rapidfuzz import fuzz
                token_score = fuzz.token_sort_ratio("tri x", search_text)
                partial_score = fuzz.partial_ratio("tri x", search_text)
            except ImportError:
                print(f"   Debug: rapidfuzz not available")
    
    # Fallback to regular search if fuzzy search fails
    if not tri_x_results:
        print(f"   Debug: Trying regular search for 'Tri-X'...")
        regular_results = api.search_films("Tri-X")
        print(f"   Debug: Regular search for 'Tri-X' returned {len(regular_results)} results")
        if regular_results:
            sample_film = regular_results[0]
            print(f"   Using regular search result: {sample_film.brand} {sample_film.name}")
        else:
            # Final fallback to any film
            print(f"   Debug: No Tri-X found, using first available film...")
            if api.film_stocks:
                sample_film = api.film_stocks[0]
                print(f"   Using fallback film: {sample_film.brand} {sample_film.name}")
            else:
                sample_film = None
    else:
        sample_film = tri_x_results[0].item
        print(f"   Using fuzzy search result: {sample_film.brand} {sample_film.name}")
    
    if sample_film:
        print(f"\n   Finding development combinations for {sample_film.brand} {sample_film.name}:")
        combinations = api.get_combinations_for_film(sample_film.id)
        print(f"   Found {len(combinations)} combinations")
        for combo in combinations[:2]:  # Show first 2
            api.display_combination_info(combo)
            print()
    else:
        print("   No films available for combination demo")
    
    # Sample 5: Show statistics
    print(f"\n5. 📊 Database Statistics:")
    total_films = len(api.film_stocks)
    active_films = len([f for f in api.film_stocks if f.discontinued == 0])
    bw_films = len([f for f in api.film_stocks if f.color_type == 'bw'])
    color_films = len([f for f in api.film_stocks if f.color_type == 'color'])
    slide_films = len([f for f in api.film_stocks if f.color_type == 'slide'])
    
    print(f"   📷 Film Stocks: {total_films} total ({active_films} active)")
    print(f"      • Black & White: {bw_films}")
    print(f"      • Color Negative: {color_films}")
    print(f"      • Slide/Transparency: {slide_films}")
    print(f"   🧪 Developers: {len(api.developers)}")
    print(f"   ⚗️  Development Combinations: {len(api.development_combinations)}")
    print(f"   📐 Formats: {len(api.formats)}")
    
    # Sample 6: Show film brands
    if api.film_stocks:
        brands = set(film.brand for film in api.film_stocks)
        print(f"\n6. 🏭 Available Film Brands ({len(brands)}):")
        for brand in sorted(brands)[:10]:  # Show first 10
            brand_count = len([f for f in api.film_stocks if f.brand == brand])
            print(f"   • {brand}: {brand_count} films")
        if len(brands) > 10:
            print(f"   ... and {len(brands) - 10} more brands")
            
    # Sample 7: Working life formatting demonstration
    print(f"\n7. ⏰ Working Life Formatting Examples:")
    test_hours = [6, 24, 25, 48, 72, 168]
    for hours in test_hours:
        formatted = api._format_working_life(hours)
        print(f"   {hours:3d} hours → {formatted}")


def start_interactive_mode(api: DorkroomAPIWrapper):
    """Start interactive Python shell with API client available"""
    
    # Create helpful shortcuts
    films = api.film_stocks
    developers = api.developers
    combinations = api.development_combinations
    formats = api.formats
    
    # Helper functions for interactive use
    def search_films(query, color_type=None):
        """Shortcut for api.search_films()"""
        return api.search_films(query, color_type)
    
    def search_developers(query):
        """Shortcut for api.search_developers()"""
        return api.search_developers(query)
        
    def fuzzy_search_films(query, limit=10, color_type=None):
        """Shortcut for api.fuzzy_search_films()"""
        return api.fuzzy_search_films(query, limit, color_type)
    
    def fuzzy_search_developers(query, limit=10):
        """Shortcut for api.fuzzy_search_developers()"""
        return api.fuzzy_search_developers(query, limit)
    
    def show_search_results(results):
        """Shortcut for api.display_search_results()"""
        api.display_search_results(results)
    
    def show_film(film_or_id):
        """Display film info - accepts film object or ID"""
        if isinstance(film_or_id, str):
            film = api.get_film_by_id(film_or_id)
            if not film:
                print(f"Film with ID '{film_or_id}' not found")
                return
        else:
            film = film_or_id
        api.display_film_info(film)
    
    def show_developer(dev_or_id):
        """Display developer info - accepts developer object or ID"""
        if isinstance(dev_or_id, str):
            dev = api.get_developer_by_id(dev_or_id)
            if not dev:
                print(f"Developer with ID '{dev_or_id}' not found")
                return
        else:
            dev = dev_or_id
        api.display_developer_info(dev)
    
    def show_combination(combo):
        """Display combination info"""
        api.display_combination_info(combo)
    
    def help_commands():
        """Show available commands"""
        print("\n🔧 Available Commands:")
        print("  • api - The main DorkroomAPIWrapper instance")
        print("  • films - List of all film stocks")
        print("  • developers - List of all developers") 
        print("  • combinations - List of development combinations")
        print("  • formats - List of film formats")
        print("\n🔍 Search Functions:")
        print("  • search_films('query', color_type='bw') - Basic search films")
        print("  • search_developers('query') - Basic search developers")
        print("  • fuzzy_search_films('query', limit=10, color_type=None) - Fuzzy search films")
        print("  • fuzzy_search_developers('query', limit=10) - Fuzzy search developers")
        print("  • show_search_results(results) - Display fuzzy search results")
        print("\n📖 Display Functions:")
        print("  • show_film(film_or_id) - Display film details")
        print("  • show_developer(dev_or_id) - Display developer details")  
        print("  • show_combination(combo) - Display combination details")
        print("\n📊 Quick Stats:")
        print(f"  • Total films: {len(films)}")
        print(f"  • Total developers: {len(developers)}")
        print(f"  • Total combinations: {len(combinations)}")
        print("\n💡 Examples:")
        print("  • results = fuzzy_search_films('kodak')")
        print("  • show_search_results(results)")
        print("  • show_film(results[0].item)  # Show details of first result")
        print("  • dev_results = fuzzy_search_developers('d76')")
        print("  • bw_films = fuzzy_search_films('tri-x', color_type='bw')")
        print("  • help_commands() - Show this help again")
        print("\n🚪 Exit: Type 'exit()' or press Ctrl+D")
    
    # Set up the interactive namespace
    interactive_namespace = {
        'api': api,
        'films': films,
        'developers': developers,
        'combinations': combinations,
        'formats': formats,
        'search_films': search_films,
        'search_developers': search_developers,
        'fuzzy_search_films': fuzzy_search_films,
        'fuzzy_search_developers': fuzzy_search_developers,
        'show_search_results': show_search_results,
        'show_film': show_film,
        'show_developer': show_developer,
        'show_combination': show_combination,
        'help_commands': help_commands,
        'help': help_commands,  # Alternative help command
    }
    
    print("\n🎯 Entering Interactive Mode...")
    print("=" * 60)
    help_commands()
    
    # Start the interactive interpreter
    try:
        code.interact(
            banner=f"\nPython Interactive Shell - Dorkroom API Ready!\nType 'help_commands()' for available commands.",
            local=interactive_namespace
        )
    except (EOFError, KeyboardInterrupt):
        print("\n\nExiting interactive mode. Goodbye! 👋")


def main():
    """Main function to run the test script"""
    parser = argparse.ArgumentParser(description='Dorkroom Static API Test Script')
    parser.add_argument('--no-demo', action='store_true', 
                       help='Skip demo queries and go straight to interactive mode')
    parser.add_argument('--no-interactive', action='store_true',
                       help='Skip interactive mode after demo')
    args = parser.parse_args()
    
    print("Dorkroom Static API Test Script")
    print("Repository: https://github.com/narrowstacks/dorkroom-static-api")
    print("=" * 60)
    
    # Initialize API client wrapper
    api = DorkroomAPIWrapper()
    
    try:
        # Load all data
        api.load_all_data()
        
        if not api._loaded:
            print("Failed to load data. Exiting.")
            sys.exit(1)
        
        # Run sample queries unless skipped
        if not args.no_demo:
            run_sample_queries(api)
            
            print("\n" + "="*60)
            print("✓ Demo completed successfully!")
            print("="*60)
        
        # Enter interactive mode unless skipped
        if not args.no_interactive:
            start_interactive_mode(api)
        
        return api
        
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the test script
    api_client = main() 
