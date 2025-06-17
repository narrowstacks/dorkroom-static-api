#!/usr/bin/env python3
"""
Test script for pulling and working with data from the Dorkroom Static API
Repository: https://github.com/narrowstacks/dorkroom-static-api
"""

import json
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import sys
import code
import argparse


class DorkroomAPI:
    """Client for accessing the Dorkroom Static API data from GitHub"""
    
    BASE_URL = "https://raw.githubusercontent.com/narrowstacks/dorkroom-static-api/main/"
    
    def __init__(self):
        self.film_stocks: List[Dict] = []
        self.developers: List[Dict] = []
        self.development_combinations: List[Dict] = []
        self.formats: List[Dict] = []
        self._loaded = False
    
    def fetch_json_data(self, filename: str) -> List[Dict]:
        """Fetch JSON data from GitHub repository"""
        url = urljoin(self.BASE_URL, filename)
        try:
            print(f"Fetching {filename} from {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"✓ Successfully loaded {len(data)} records from {filename}")
            return data
        except requests.RequestException as e:
            print(f"✗ Error fetching {filename}: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON from {filename}: {e}")
            return []
    
    def load_all_data(self):
        """Load all data from the repository"""
        print("Loading Dorkroom Static API data...")
        print("-" * 50)
        
        self.film_stocks = self.fetch_json_data("film_stocks.json")
        self.developers = self.fetch_json_data("developers.json")
        self.development_combinations = self.fetch_json_data("development_combinations.json")
        self.formats = self.fetch_json_data("formats.json")
        
        self._loaded = True
        print("-" * 50)
        print(f"Data loading complete!")
        print(f"Total records: {len(self.film_stocks) + len(self.developers) + len(self.development_combinations) + len(self.formats)}")
    
    def get_film_by_id(self, film_id: str) -> Optional[Dict]:
        """Get a film stock by its UUID"""
        return next((film for film in self.film_stocks if film.get('id') == film_id), None)
    
    def get_developer_by_id(self, developer_id: str) -> Optional[Dict]:
        """Get a developer by its UUID"""
        return next((dev for dev in self.developers if dev.get('id') == developer_id), None)
    
    def search_films(self, query: str, color_type: Optional[str] = None) -> List[Dict]:
        """Search film stocks by name/brand"""
        results = []
        query_lower = query.lower()
        
        for film in self.film_stocks:
            if (query_lower in film.get('name', '').lower() or 
                query_lower in film.get('brand', '').lower()):
                if color_type is None or film.get('color_type') == color_type:
                    results.append(film)
        
        return results
    
    def search_developers(self, query: str) -> List[Dict]:
        """Search developers by name/manufacturer"""
        results = []
        query_lower = query.lower()
        
        for dev in self.developers:
            if (query_lower in dev.get('name', '').lower() or 
                query_lower in dev.get('manufacturer', '').lower()):
                results.append(dev)
        
        return results
    
    def get_combinations_for_film(self, film_id: str) -> List[Dict]:
        """Get all development combinations for a specific film"""
        return [combo for combo in self.development_combinations 
                if combo.get('film_stock_id') == film_id]
    
    def get_combinations_for_developer(self, developer_id: str) -> List[Dict]:
        """Get all development combinations for a specific developer"""
        return [combo for combo in self.development_combinations 
                if combo.get('developer_id') == developer_id]
    
    def display_film_info(self, film: Dict):
        """Display detailed information about a film stock"""
        print(f"\n📷 {film.get('brand')} {film.get('name')}")
        print(f"   ID: {film.get('id')}")
        print(f"   ISO Speed: {film.get('iso_speed')}")
        print(f"   Color Type: {film.get('color_type', 'N/A').upper()}")
        print(f"   Discontinued: {'Yes' if film.get('discontinued') else 'No'}")
        
        if film.get('description'):
            desc = film.get('description', '')
            # Truncate long descriptions
            if len(desc) > 200:
                desc = desc[:200] + "..."
            print(f"   Description: {desc}")
        
        if film.get('manufacturer_notes'):
            print(f"   Key Features: {', '.join(film.get('manufacturer_notes', []))}")
    
    def display_developer_info(self, developer: Dict):
        """Display detailed information about a developer"""
        print(f"\n🧪 {developer.get('manufacturer')} {developer.get('name')}")
        print(f"   ID: {developer.get('id')}")
        print(f"   Type: {developer.get('type', 'N/A').title()}")
        print(f"   For: {developer.get('film_or_paper', 'N/A').title()}")
        print(f"   Discontinued: {'Yes' if developer.get('discontinued') else 'No'}")
        
        if developer.get('working_life_hours'):
            hours = developer.get('working_life_hours')
            days = hours / 24
            print(f"   Working Life: {hours} hours ({days:.1f} days)")
        
        if developer.get('stock_life_months'):
            print(f"   Stock Life: {developer.get('stock_life_months')} months")
        
        dilutions = developer.get('dilutions', [])
        if dilutions:
            print(f"   Available Dilutions: {len(dilutions)}")
            for dilution in dilutions[:3]:  # Show first 3
                print(f"     • {dilution.get('name', 'Unnamed')}: {dilution.get('dilution', 'N/A')}")
            if len(dilutions) > 3:
                print(f"     ... and {len(dilutions) - 3} more")
    
    def display_combination_info(self, combo: Dict):
        """Display detailed information about a development combination"""
        film = self.get_film_by_id(combo.get('film_stock_id', ''))
        developer = self.get_developer_by_id(combo.get('developer_id', ''))
        
        print(f"\n⚗️  {combo.get('name', 'Unnamed Combination')}")
        print(f"   ID: {combo.get('id')}")
        
        if film:
            print(f"   Film: {film.get('brand')} {film.get('name')}")
        else:
            print(f"   Film ID: {combo.get('film_stock_id', 'Unknown')}")
        
        if developer:
            print(f"   Developer: {developer.get('manufacturer')} {developer.get('name')}")
        else:
            print(f"   Developer ID: {combo.get('developer_id', 'Unknown')}")
        
        print(f"   Temperature: {combo.get('temperature_f', 'N/A')}°F")
        print(f"   Time: {combo.get('time_minutes', 'N/A')} minutes")
        print(f"   Shooting ISO: {combo.get('shooting_iso', 'N/A')}")
        
        push_pull = combo.get('push_pull', 0)
        if push_pull > 0:
            print(f"   Push: +{push_pull} stops")
        elif push_pull < 0:
            print(f"   Pull: {push_pull} stops")
        else:
            print(f"   Processing: Normal")
        
        if combo.get('agitation_schedule'):
            print(f"   Agitation: {combo.get('agitation_schedule')}")
        
        if combo.get('notes'):
            print(f"   Notes: {combo.get('notes')}")


def run_sample_queries(api: DorkroomAPI):
    """Run sample queries to demonstrate the API functionality"""
    
    print("\n" + "="*60)
    print("SAMPLE QUERIES AND DEMONSTRATIONS")
    print("="*60)
    
    # Sample 1: Search for popular films
    print("\n1. 🔍 Searching for 'Tri-X' films:")
    trix_films = api.search_films("Tri-X")
    for film in trix_films[:3]:  # Show first 3 results
        api.display_film_info(film)
    
    # Sample 2: Search for black and white films only
    print(f"\n2. 🔍 Searching for black and white films containing 'HP':")
    bw_films = api.search_films("HP", color_type="bw")
    for film in bw_films[:2]:  # Show first 2 results
        api.display_film_info(film)
    
    # Sample 3: Search for developers
    print(f"\n3. 🔍 Searching for 'HC-110' developer:")
    hc110_devs = api.search_developers("HC-110")
    for dev in hc110_devs[:1]:  # Show first result
        api.display_developer_info(dev)
    
    # Sample 4: Find development combinations for a specific film
    if api.film_stocks:
        sample_film = api.film_stocks[0]  # Get first film
        print(f"\n4. 🔍 Finding development combinations for {sample_film.get('brand')} {sample_film.get('name')}:")
        combinations = api.get_combinations_for_film(sample_film.get('id'))
        print(f"   Found {len(combinations)} combinations")
        for combo in combinations[:2]:  # Show first 2
            api.display_combination_info(combo)
    
    # Sample 5: Show statistics
    print(f"\n5. 📊 Database Statistics:")
    total_films = len(api.film_stocks)
    active_films = len([f for f in api.film_stocks if not f.get('discontinued')])
    bw_films = len([f for f in api.film_stocks if f.get('color_type') == 'bw'])
    color_films = len([f for f in api.film_stocks if f.get('color_type') == 'color'])
    slide_films = len([f for f in api.film_stocks if f.get('color_type') == 'slide'])
    
    print(f"   📷 Film Stocks: {total_films} total ({active_films} active)")
    print(f"      • Black & White: {bw_films}")
    print(f"      • Color Negative: {color_films}")
    print(f"      • Slide/Transparency: {slide_films}")
    print(f"   🧪 Developers: {len(api.developers)}")
    print(f"   ⚗️  Development Combinations: {len(api.development_combinations)}")
    print(f"   📐 Formats: {len(api.formats)}")
    
    # Sample 6: Show film brands
    if api.film_stocks:
        brands = set(film.get('brand', 'Unknown') for film in api.film_stocks)
        print(f"\n6. 🏭 Available Film Brands ({len(brands)}):")
        for brand in sorted(brands)[:10]:  # Show first 10
            brand_count = len([f for f in api.film_stocks if f.get('brand') == brand])
            print(f"   • {brand}: {brand_count} films")
        if len(brands) > 10:
            print(f"   ... and {len(brands) - 10} more brands")


def start_interactive_mode(api: DorkroomAPI):
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
    
    def show_film(film_or_id):
        """Display film info - accepts film dict or ID"""
        if isinstance(film_or_id, str):
            film = api.get_film_by_id(film_or_id)
            if not film:
                print(f"Film with ID '{film_or_id}' not found")
                return
        else:
            film = film_or_id
        api.display_film_info(film)
    
    def show_developer(dev_or_id):
        """Display developer info - accepts developer dict or ID"""
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
        print("  • api - The main DorkroomAPI instance")
        print("  • films - List of all film stocks")
        print("  • developers - List of all developers") 
        print("  • combinations - List of development combinations")
        print("  • formats - List of film formats")
        print("\n🔍 Search Functions:")
        print("  • search_films('query', color_type='bw') - Search films")
        print("  • search_developers('query') - Search developers")
        print("\n📖 Display Functions:")
        print("  • show_film(film_or_id) - Display film details")
        print("  • show_developer(dev_or_id) - Display developer details")
        print("  • show_combination(combo) - Display combination details")
        print("\n📊 Quick Stats:")
        print(f"  • Total films: {len(films)}")
        print(f"  • Total developers: {len(developers)}")
        print(f"  • Total combinations: {len(combinations)}")
        print("\n💡 Examples:")
        print("  • kodak_films = search_films('Kodak')")
        print("  • show_film(films[0])")
        print("  • bw_films = search_films('tri-x', 'bw')")
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
    
    # Initialize API client
    api = DorkroomAPI()
    
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
