#!/usr/bin/env python3
"""
Script to add new development combinations to the development_combinations.json file
"""

import json
import os
import uuid
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from github_issue_helper import handle_combination_submission

def get_data_file_path(filename: str) -> str:
    """Get the full path to a data file in the root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    return os.path.join(parent_dir, filename)

# Add fuzzy search dependencies
try:
    from rapidfuzz import fuzz, process
    from colorama import init, Fore, Style
    init(autoreset=True)
    SEARCH_AVAILABLE = True
except ImportError:
    print("Warning: fuzzy search packages not available. Install them with:")
    print("pip install rapidfuzz colorama")
    print("Falling back to basic list selection...")
    SEARCH_AVAILABLE = False
    # Define dummy color constants
    class Fore:
        GREEN = CYAN = MAGENTA = YELLOW = WHITE = RED = BLUE = ""
    class Style:
        RESET_ALL = ""

@dataclass
class SearchResult:
    """Container for search results with score"""
    item: Dict[Any, Any]
    score: int
    type: str

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def show_header():
    """Display the application header"""
    print("⚗️ Development Combination Addition Tool")
    print("=" * 40)
    print("💡 Tip: Type '<' or 'back' at any prompt to go back to the previous field")
    if SEARCH_AVAILABLE:
        print("🔍 Tip: Search for films and developers instead of browsing lists!")
    print()

def load_development_combinations() -> List[Dict[str, Any]]:
    """Load existing development combinations from JSON file"""
    combinations_path = get_data_file_path('development_combinations.json')
    if not os.path.exists(combinations_path):
        return []
    
    try:
        with open(combinations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Error reading development_combinations.json file. Starting with empty list.")
        return []

def save_development_combinations(combinations: List[Dict[str, Any]]) -> None:
    """Save development combinations list to JSON file"""
    combinations_path = get_data_file_path('development_combinations.json')
    with open(combinations_path, 'w', encoding='utf-8') as f:
        json.dump(combinations, f, indent=2, ensure_ascii=False)

def load_film_stocks() -> List[Dict[str, Any]]:
    """Load film stocks for selection"""
    try:
        film_stocks_path = get_data_file_path('film_stocks.json')
        with open(film_stocks_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Warning: Could not load film_stocks.json")
        return []

def load_developers() -> List[Dict[str, Any]]:
    """Load developers for selection"""
    try:
        developers_path = get_data_file_path('developers.json')
        with open(developers_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Warning: Could not load developers.json")
        return []

def generate_new_uuid() -> str:
    """Generate a new UUID for a development combination"""
    return str(uuid.uuid4())

def fuzzy_search_films(films: List[Dict[str, Any]], query: str, limit: int = 10) -> List[SearchResult]:
    """Search films using improved fuzzy matching, filtering out color/slide films that don't need custom development"""
    if not SEARCH_AVAILABLE:
        return []
    
    results = []
    query_lower = query.lower()
    
    for film in films:
        # Filter out color and slide films - they use standardized processes (C-41, E-6)
        colorType = film.get('colorType', '').lower()
        if colorType in ['color', 'slide']:
            continue
        # Create primary searchable text (name and brand - most important)
        primary_text = f"{film['brand']} {film['name']}".lower()
        
        # Create secondary searchable text (other attributes)
        secondary_text = f"{film['isoSpeed']} {film['colorType']}".lower()
        if film.get('description'):
            secondary_text += f" {film['description']}".lower()
        
        # Calculate multiple fuzzy scores
        # 1. Token sort ratio - good for handling word order differences
        primary_token_score = fuzz.token_sort_ratio(query_lower, primary_text)
        
        # 2. Partial ratio - good for substring matches
        primary_partial_score = fuzz.partial_ratio(query_lower, primary_text)
        
        # 3. Ratio - good for overall similarity
        primary_ratio_score = fuzz.ratio(query_lower, primary_text)
        
        # 4. Token set ratio - good for handling extra words
        primary_token_set_score = fuzz.token_set_ratio(query_lower, primary_text)
        
        # Calculate secondary scores (lower weight)
        secondary_partial_score = fuzz.partial_ratio(query_lower, secondary_text)
        
        # Weighted composite score - prioritize primary text heavily
        composite_score = (
            primary_token_score * 0.3 +
            primary_partial_score * 0.25 +
            primary_ratio_score * 0.2 +
            primary_token_set_score * 0.15 +
            secondary_partial_score * 0.1
        )
        
        # Bonus for exact word matches in primary text
        query_words = query_lower.split()
        primary_words = primary_text.split()
        exact_word_matches = sum(1 for word in query_words if word in primary_words)
        if exact_word_matches > 0:
            composite_score += exact_word_matches * 10  # Significant bonus
        
        # Bonus for matches at the beginning of the name/brand
        if primary_text.startswith(query_lower):
            composite_score += 15
        elif any(word.startswith(query_lower) for word in primary_words):
            composite_score += 10
        
        if composite_score > 40:  # Adjusted threshold
            results.append(SearchResult(film, int(composite_score), "film"))
    
    return sorted(results, key=lambda x: x.score, reverse=True)[:limit]

def fuzzy_search_developers(developers: List[Dict[str, Any]], query: str, limit: int = 10) -> List[SearchResult]:
    """Search developers using improved fuzzy matching (copied from darkroom_search.py)"""
    if not SEARCH_AVAILABLE:
        return []
    
    results = []
    query_lower = query.lower()
    
    for dev in developers:
        # Create primary searchable text (name and manufacturer - most important)
        primary_text = f"{dev['name']} {dev['manufacturer']}".lower()
        
        # Create secondary searchable text (other attributes)
        secondary_text = f"{dev['type']} {dev['filmOrPaper']}".lower()
        if dev.get('notes'):
            secondary_text += f" {dev['notes']}".lower()
        
        # Calculate multiple fuzzy scores
        primary_token_score = fuzz.token_sort_ratio(query_lower, primary_text)
        primary_partial_score = fuzz.partial_ratio(query_lower, primary_text)
        primary_ratio_score = fuzz.ratio(query_lower, primary_text)
        primary_token_set_score = fuzz.token_set_ratio(query_lower, primary_text)
        
        # Calculate secondary scores (lower weight)
        secondary_partial_score = fuzz.partial_ratio(query_lower, secondary_text)
        
        # Weighted composite score - prioritize primary text heavily
        composite_score = (
            primary_token_score * 0.3 +
            primary_partial_score * 0.25 +
            primary_ratio_score * 0.2 +
            primary_token_set_score * 0.15 +
            secondary_partial_score * 0.1
        )
        
        # Bonus for exact word matches in primary text
        query_words = query_lower.split()
        primary_words = primary_text.split()
        exact_word_matches = sum(1 for word in query_words if word in primary_words)
        if exact_word_matches > 0:
            composite_score += exact_word_matches * 10
        
        # Bonus for matches at the beginning of the name/manufacturer
        if primary_text.startswith(query_lower):
            composite_score += 15
        elif any(word.startswith(query_lower) for word in primary_words):
            composite_score += 10
        
        if composite_score > 40:
            results.append(SearchResult(dev, int(composite_score), "developer"))
    
    return sorted(results, key=lambda x: x.score, reverse=True)[:limit]

def calculate_push_pull_stops(film_iso: float, shooting_iso: float) -> int:
    """Calculate push/pull stops based on ISO difference"""
    if film_iso <= 0 or shooting_iso <= 0:
        return 0
    
    # Calculate stops using log base 2
    stops_float = math.log2(shooting_iso / film_iso)
    
    # Round to nearest half stop, then to nearest integer
    # This handles cases like 1.33 stops -> 1 stop, 1.67 stops -> 2 stops
    return round(stops_float)

def get_user_input(prompt: str, required: bool = True, input_type: str = 'str', allow_back: bool = True, default_value: Any = None) -> Any:
    """Get user input with validation and back navigation"""
    back_commands = ['<', 'back']
    
    while True:
        try:
            # Modify prompt to show default value if provided
            display_prompt = prompt
            if default_value is not None:
                display_prompt = prompt.rstrip(': ') + f" (default: {default_value}): "
            
            if allow_back:
                value = input(display_prompt + " (or '<' to go back): " if default_value is None else display_prompt).strip()
            else:
                value = input(display_prompt).strip()
            
            # Check for back command
            if allow_back and value.lower() in back_commands:
                return "<<<BACK>>>"
            
            # If no value provided and we have a default, use it
            if not value and default_value is not None:
                return default_value
            
            if not value and not required:
                return None
            
            if not value and required:
                print("This field is required. Please enter a value.")
                continue
            
            if input_type == 'int':
                return int(value)
            elif input_type == 'float':
                return float(value)
            elif input_type == 'bool':
                return value.lower() in ['yes', 'y', '1', 'true']
            else:
                return value
                
        except ValueError:
            if input_type == 'float':
                print("Invalid input. Please enter a valid number (decimals allowed).")
            else:
                print("Invalid input. Please enter a valid number.")
            continue

def select_film_stock(film_stocks: List[Dict[str, Any]], allow_back: bool = True) -> Any:
    """Let user search and select a film stock"""
    if not film_stocks:
        print("No film stocks available. Please add film stocks first.")
        return None
    
    while True:
        print(f"\n{Fore.CYAN}🎞️  FILM STOCK SELECTION")
        print(f"{Fore.WHITE}Enter search terms to find black & white films (e.g., 'tri-x', 'hp5', 'tmax')")
        print(f"{Fore.WHITE}Or type 'browse' to see a list of available films")
        print(f"{Fore.YELLOW}Note: Only black & white films are shown (color/slide films use standardized processes)")
        
        if allow_back:
            search_query = input(f"{Fore.CYAN}Search films (or '<' to go back): {Fore.WHITE}").strip()
        else:
            search_query = input(f"{Fore.CYAN}Search films: {Fore.WHITE}").strip()
        
        # Check for back command
        if allow_back and search_query.lower() in ['<', 'back']:
            return "<<<BACK>>>"
        
        # Handle browse mode
        if search_query.lower() == 'browse':
            browse_result = _browse_film_stocks(film_stocks, allow_back)
            if browse_result is None:
                continue  # User wants to go back to search
            return browse_result
        
        if not search_query:
            print(f"{Fore.RED}Please enter a search query or 'browse' to see all films.")
            continue
        
        # Search for films
        if SEARCH_AVAILABLE:
            search_results = fuzzy_search_films(film_stocks, search_query, limit=15)
        else:
            # Fallback to simple filtering
            search_results = []
            query_lower = search_query.lower()
            for film in film_stocks:
                # Filter out color and slide films
                colorType = film.get('colorType', '').lower()
                if colorType in ['color', 'slide']:
                    continue
                film_text = f"{film['brand']} {film['name']}".lower()
                if query_lower in film_text:
                    search_results.append(SearchResult(film, 100, "film"))
        
        if not search_results:
            print(f"{Fore.RED}No films found matching '{search_query}'. Try different search terms.")
            continue
        
        # Display search results
        print(f"\n{Fore.GREEN}Found {len(search_results)} film(s):")
        for i, result in enumerate(search_results, 1):
            film = result.item
            status = f"{Fore.RED}(Discontinued)" if film.get('discontinued', 0) else ""
            match_info = f"({result.score}% match)" if SEARCH_AVAILABLE else ""
            print(f"{Fore.WHITE}{i:2d}. {film['brand']} {film['name']} - ISO {film['isoSpeed']} {status} {match_info}")
        
        # Let user select from results
        try:
            choice_str = input(f"\n{Fore.CYAN}Enter choice (1-{len(search_results)}) or 'search' for new search: {Fore.WHITE}").strip()
            
            if choice_str.lower() == 'search':
                continue
            
            choice = int(choice_str)
            if 1 <= choice <= len(search_results):
                selected_film = search_results[choice - 1].item
                print(f"{Fore.GREEN}Selected: {selected_film['brand']} {selected_film['name']}")
                return selected_film['id']
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and {len(search_results)}.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.")

def _browse_film_stocks(film_stocks: List[Dict[str, Any]], allow_back: bool = True) -> Any:
    """Browse film stocks in list format (fallback mode)"""
    # Filter out color and slide films
    bw_films = [f for f in film_stocks if f.get('colorType', '').lower() not in ['color', 'slide']]
    
    while True:
        print(f"\n{Fore.CYAN}Available black & white film stocks:")
        for i, stock in enumerate(bw_films[:20], 1):  # Show first 20
            status = f"{Fore.RED}(Discontinued)" if stock.get('discontinued', 0) else ""
            print(f"{Fore.WHITE}{i:2d}. {stock['brand']} {stock['name']} (ISO {stock['isoSpeed']}) {status}")
        
        if len(bw_films) > 20:
            print(f"{Fore.WHITE}... and {len(bw_films) - 20} more")
        
        try:
            if allow_back:
                choice_str = input(f"{Fore.CYAN}Enter choice (1-{min(20, len(bw_films))}) or 'search' to go back to search: {Fore.WHITE}").strip()
            else:
                choice_str = input(f"{Fore.CYAN}Enter choice (1-{min(20, len(bw_films))}): {Fore.WHITE}").strip()
            
            if choice_str.lower() == 'search':
                return None  # Return to search mode
            
            choice = int(choice_str)
            if 1 <= choice <= min(20, len(bw_films)):
                selected_stock = bw_films[choice - 1]
                print(f"{Fore.GREEN}Selected: {selected_stock['brand']} {selected_stock['name']}")
                return selected_stock['id']
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and {min(20, len(bw_films))}.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.")

def select_developer_and_dilution(developers: List[Dict[str, Any]], allow_back: bool = True) -> Any:
    """Let user search and select a developer and dilution"""
    if not developers:
        print("No developers available. Please add developers first.")
        return None, None
    
    # First select developer using search
    selected_dev = None
    while selected_dev is None:
        print(f"\n{Fore.MAGENTA}⚗️  DEVELOPER SELECTION")
        print(f"{Fore.WHITE}Enter search terms to find developers (e.g., 'rodinal', 'kodak d76', 'ilford')")
        print(f"{Fore.WHITE}Or type 'browse' to see a list of available developers")
        
        if allow_back:
            search_query = input(f"{Fore.CYAN}Search developers (or '<' to go back): {Fore.WHITE}").strip()
        else:
            search_query = input(f"{Fore.CYAN}Search developers: {Fore.WHITE}").strip()
        
        # Check for back command
        if allow_back and search_query.lower() in ['<', 'back']:
            return "<<<BACK>>>", None
        
        # Handle browse mode
        if search_query.lower() == 'browse':
            browse_result = _browse_developers(developers, allow_back)
            if browse_result == "<<<BACK>>>":
                return "<<<BACK>>>", None
            elif browse_result is None:
                continue  # User wants to go back to search
            else:
                selected_dev = next((d for d in developers if d['id'] == browse_result), None)
                break
        
        if not search_query:
            print(f"{Fore.RED}Please enter a search query or 'browse' to see all developers.")
            continue
        
        # Search for developers
        if SEARCH_AVAILABLE:
            search_results = fuzzy_search_developers(developers, search_query, limit=15)
        else:
            # Fallback to simple filtering
            search_results = []
            query_lower = search_query.lower()
            for dev in developers:
                dev_text = f"{dev['name']} {dev['manufacturer']}".lower()
                if query_lower in dev_text:
                    search_results.append(SearchResult(dev, 100, "developer"))
        
        if not search_results:
            print(f"{Fore.RED}No developers found matching '{search_query}'. Try different search terms.")
            continue
        
        # Display search results
        print(f"\n{Fore.GREEN}Found {len(search_results)} developer(s):")
        for i, result in enumerate(search_results, 1):
            dev = result.item
            dilution_count = len(dev.get('dilutions', []))
            status = f"{Fore.RED}(Discontinued)" if dev.get('discontinued', 0) else ""
            match_info = f"({result.score}% match)" if SEARCH_AVAILABLE else ""
            print(f"{Fore.WHITE}{i:2d}. {dev['name']} ({dev['manufacturer']}) - {dilution_count} dilutions {status} {match_info}")
        
        # Let user select from results
        try:
            choice_str = input(f"\n{Fore.CYAN}Enter choice (1-{len(search_results)}) or 'search' for new search: {Fore.WHITE}").strip()
            
            if choice_str.lower() == 'search':
                continue
            
            choice = int(choice_str)
            if 1 <= choice <= len(search_results):
                selected_dev = search_results[choice - 1].item
                print(f"{Fore.GREEN}Selected: {selected_dev['name']} ({selected_dev['manufacturer']})")
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and {len(search_results)}.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.")
    
    # Then select dilution
    if not selected_dev.get('dilutions'):
        print(f"{Fore.YELLOW}Selected developer has no dilutions configured.")
        return selected_dev['id'], None
    
    while True:
        print(f"\n{Fore.YELLOW}Available dilutions for {selected_dev['name']}:")
        for dilution in selected_dev['dilutions']:
            print(f"{Fore.WHITE}{dilution['id']:2d}. {dilution['name']}: {dilution['dilution']}")
        
        try:
            choice_str = input(f"{Fore.CYAN}Enter dilution choice (or 'custom' for custom dilution): {Fore.WHITE}").strip()
            
            if choice_str.lower() == 'custom':
                custom_dilution = get_user_input("Enter custom dilution (e.g., '1:31', '1+15'): ", allow_back=False)
                return selected_dev['id'], None, custom_dilution
            
            choice = int(choice_str)
            selected_dilution = next((d for d in selected_dev['dilutions'] if d['id'] == choice), None)
            
            if selected_dilution:
                return selected_dev['id'], selected_dilution['id'], None
            else:
                print(f"{Fore.RED}Invalid dilution choice.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number or 'custom'.")

def _browse_developers(developers: List[Dict[str, Any]], allow_back: bool = True) -> Any:
    """Browse developers in list format (fallback mode)"""
    while True:
        print(f"\n{Fore.MAGENTA}Available developers:")
        for i, dev in enumerate(developers[:20], 1):  # Show first 20
            dilution_count = len(dev.get('dilutions', []))
            status = f"{Fore.RED}(Discontinued)" if dev.get('discontinued', 0) else ""
            print(f"{Fore.WHITE}{i:2d}. {dev['name']} ({dev['manufacturer']}) - {dilution_count} dilutions {status}")
        
        if len(developers) > 20:
            print(f"{Fore.WHITE}... and {len(developers) - 20} more")
        
        try:
            if allow_back:
                choice_str = input(f"{Fore.CYAN}Enter choice (1-{min(20, len(developers))}) or 'search' to go back to search: {Fore.WHITE}").strip()
            else:
                choice_str = input(f"{Fore.CYAN}Enter choice (1-{min(20, len(developers))}): {Fore.WHITE}").strip()
            
            if choice_str.lower() == 'search':
                return None  # Return to search mode
            
            choice = int(choice_str)
            if 1 <= choice <= min(20, len(developers)):
                selected_dev = developers[choice - 1]
                print(f"{Fore.GREEN}Selected: {selected_dev['name']} ({selected_dev['manufacturer']})")
                return selected_dev['id']
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and {min(20, len(developers))}.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.")

def display_current_progress(combination_data: Dict[str, Any], current_step: int, total_steps: int) -> None:
    """Display current progress with colored field status"""
    # ANSI color codes
    GREEN = '\033[92m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    print(f"📋 Progress: {current_step}/{total_steps}")
    print()
    
    # All fields in order
    all_fields = [
        ("name", "Combination Name"),
        ("filmStockId", "Film Stock"),
        ("developerId", "Developer"),
        ("dilutionId", "Dilution"),
        ("shootingIso", "Shooting ISO"),
        ("temperatureF", "Temperature (°F)"),
        ("timeMinutes", "Time (minutes)"),
        ("agitationSchedule", "Agitation Schedule"),
        ("notes", "Notes")
    ]
    
    for i, (field_key, field_name) in enumerate(all_fields, 1):
        value = combination_data.get(field_key)
        
        if value is not None or (field_key == "name" and i <= current_step):
            # Field has been filled or is the name field that's been processed
            if field_key in ["filmStockId", "developerId"]:
                display_value = "Selected"
            elif field_key == "name" and (value is None or value == ""):
                display_value = "[Automatic]"
            elif field_key == "dilutionId" and value is None and combination_data.get("customDilution"):
                display_value = f"Custom: {combination_data['customDilution']}"
            elif field_key == "shootingIso":
                if value == "film_stock_default":
                    display_value = "Film Stock Default"
                else:
                    display_value = str(value)
            elif value == "":
                display_value = "None"
            else:
                display_value = str(value)
            
            # Current field gets bold, completed fields get green
            if i == current_step:
                print(f"{BOLD}{GREEN}{i:2d}. {field_name:<20}: {display_value}{RESET}")
            else:
                print(f"{GREEN}{i:2d}. {field_name:<20}: {display_value}{RESET}")
        else:
            # Field not yet filled
            if i == current_step:
                print(f"{BOLD}{i:2d}. {field_name:<20}: [Current]{RESET}")
            else:
                print(f"{GRAY}{i:2d}. {field_name:<20}: [Pending]{RESET}")

def get_shooting_iso(film_stocks: List[Dict[str, Any]], film_stock_id: str, allow_back: bool = True) -> Any:
    """Get shooting ISO from user, with film stock default as fallback"""
    # Find the selected film stock
    film_stock = next((f for f in film_stocks if f['id'] == film_stock_id), None)
    if not film_stock:
        return "film_stock_default"
    
    film_iso = film_stock['isoSpeed']
    
    while True:
        try:
            prompt = f"Shooting ISO (press Enter for film stock default of {film_iso}): "
            if allow_back:
                value = input(prompt + " (or '<' to go back): ").strip()
            else:
                value = input(prompt).strip()
            
            # Check for back command
            if allow_back and value.lower() in ['<', 'back']:
                return "<<<BACK>>>"
            
            # If empty, use film stock default
            if not value:
                return "film_stock_default"
            
            # Try to parse as float/int
            shooting_iso = float(value)
            if shooting_iso <= 0:
                print("ISO must be a positive number.")
                continue
            
            # Calculate and show push/pull
            push_pull = calculate_push_pull_stops(film_iso, shooting_iso)
            if push_pull > 0:
                print(f"This will be a {push_pull} stop push (from ISO {film_iso} to {shooting_iso})")
            elif push_pull < 0:
                print(f"This will be a {abs(push_pull)} stop pull (from ISO {film_iso} to {shooting_iso})")
            else:
                print(f"This will be normal development (ISO {shooting_iso})")
            
            return shooting_iso
            
        except ValueError:
            print("Invalid input. Please enter a valid ISO number.")
            continue

def generate_automatic_name(combination_data: Dict[str, Any], film_stocks: List[Dict[str, Any]], developers: List[Dict[str, Any]]) -> str:
    """Generate an automatic combination name in the format: [Film Stock Name] @ [Shooting ISO] in [Developer Name] [Developer Dilution]"""
    
    # Get film stock info
    film_stock = next((f for f in film_stocks if f['id'] == combination_data['filmStockId']), None)
    film_stock_name = f"{film_stock['brand']} {film_stock['name']}" if film_stock else "Unknown Film"
    
    # Get shooting ISO
    shooting_iso = combination_data.get('shootingIso')
    if shooting_iso == "film_stock_default" and film_stock:
        shooting_iso = film_stock['isoSpeed']
    iso_text = str(int(shooting_iso)) if isinstance(shooting_iso, (int, float)) else str(shooting_iso)
    
    # Get developer info
    developer = next((d for d in developers if d['id'] == combination_data['developerId']), None)
    developer_name = developer['name'] if developer else "Unknown Developer"
    
    # Get dilution info
    dilution_text = ""
    if combination_data.get('dilutionId') and developer:
        dilution = next((d for d in developer.get('dilutions', []) if d['id'] == combination_data['dilutionId']), None)
        if dilution:
            dilution_text = dilution['dilution']
    elif combination_data.get('customDilution'):
        dilution_text = combination_data['customDilution']
    else:
        dilution_text = "Unknown Dilution"
    
    return f"{film_stock_name} @ {iso_text} in {developer_name} {dilution_text}"

def collect_combination_data(film_stocks: List[Dict[str, Any]], developers: List[Dict[str, Any]], new_uuid: str) -> Optional[Dict[str, Any]]:
    """Collect development combination data with simple back navigation"""
    combination_data = {"id": new_uuid}
    
    # Field collection order and info
    fields = [
        ("name", "Combination name", False, lambda: get_user_input("Combination name (press Enter for automatic): ", required=False)),
        ("filmStockId", "Film stock", True, lambda: select_film_stock(film_stocks)),
        ("developer_dilution", "Developer and dilution", True, lambda: select_developer_and_dilution(developers)),
        ("shootingIso", "Shooting ISO", True, lambda: get_shooting_iso(film_stocks, combination_data.get('filmStockId', ''))),
        ("temperatureF", "Temperature", True, lambda: get_user_input("Temperature in Fahrenheit", input_type='int', default_value=68)),
        ("timeMinutes", "Development time", True, lambda: get_user_input("Development time in minutes: ", input_type='float')),
        ("agitationSchedule", "Agitation schedule", True, lambda: get_user_input("Agitation schedule", default_value='30s initial, then 10s every 60s')),
        ("notes", "Notes", False, lambda: get_user_input("Additional notes (or press Enter for none): ", required=False))
    ]
    
    current_field = 0
    
    while current_field < len(fields):
        # Clear screen and show header
        clear_screen()
        show_header()
        
        field_key, field_name, required, input_func = fields[current_field]
        
        # Show progress
        display_current_progress(combination_data, current_field + 1, len(fields))
        
        print(f"\n--- {field_name} ---")
        
        # Get input for current field
        if current_field == 0:
            # First field, no back option, but now optional
            result = get_user_input("Combination name (press Enter for automatic): ", required=False, allow_back=False)
        else:
            # Special handling for developer/dilution selection
            if field_key == "developer_dilution":
                result = select_developer_and_dilution(developers)
                if result == "<<<BACK>>>":
                    current_field -= 1
                    continue
                elif result and len(result) >= 2:
                    combination_data["developerId"] = result[0]
                    combination_data["dilutionId"] = result[1]
                    if len(result) > 2:
                        combination_data["customDilution"] = result[2]
                    current_field += 1
                    continue
            else:
                result = input_func()
        
        # Handle back navigation
        if result == "<<<BACK>>>" and current_field > 0:
            current_field -= 1
            continue
        elif result == "<<<BACK>>>" and current_field == 0:
            print("Cannot go back from the first field.")
            input("Press Enter to continue...")
            continue
        
        # Store the result and move forward
        combination_data[field_key] = result
        current_field += 1
    
    # Calculate and store push/pull stops based on ISO
    film_stock = next((f for f in film_stocks if f['id'] == combination_data['filmStockId']), None)
    if film_stock:
        film_iso = film_stock['isoSpeed']
        shooting_iso = combination_data.get('shootingIso')
        
        if shooting_iso == "film_stock_default":
            shooting_iso = film_iso
            combination_data['shootingIso'] = film_iso
        
        # Calculate push/pull stops
        combination_data['pushPull'] = calculate_push_pull_stops(film_iso, shooting_iso)
    else:
        combination_data['pushPull'] = 0
    
    # Generate automatic name if none was provided
    if not combination_data.get('name'):
        combination_data['name'] = generate_automatic_name(combination_data, film_stocks, developers)
    
    return combination_data

def display_combination(combination: Dict[str, Any], film_stocks: List[Dict[str, Any]], developers: List[Dict[str, Any]]) -> None:
    """Display a development combination's information for confirmation"""
    clear_screen()
    show_header()
    
    # Get film stock and developer names for display
    film_stock = next((f for f in film_stocks if f['id'] == combination['filmStockId']), None)
    developer = next((d for d in developers if d['id'] == combination['developerId']), None)
    
    dilution_info = "Custom"
    if combination.get('dilutionId') and developer:
        dilution = next((d for d in developer.get('dilutions', []) if d['id'] == combination['dilutionId']), None)
        if dilution:
            dilution_info = f"{dilution['name']}: {dilution['dilution']}"
    elif combination.get('customDilution'):
        dilution_info = f"Custom: {combination['customDilution']}"
    
    # Format push/pull display
    push_pull = combination.get('pushPull', 0)
    if push_pull > 0:
        push_pull_text = f"+{push_pull} stop{'s' if push_pull != 1 else ''} (push)"
    elif push_pull < 0:
        push_pull_text = f"{push_pull} stop{'s' if push_pull != -1 else ''} (pull)"
    else:
        push_pull_text = "Normal development"
    
    # Format ISO display
    film_iso = film_stock['isoSpeed'] if film_stock else 'Unknown'
    shooting_iso = combination.get('shootingIso', film_iso)
    if shooting_iso == film_iso:
        iso_text = f"ISO {shooting_iso} (film stock default)"
    else:
        iso_text = f"ISO {shooting_iso} (film stock: {film_iso})"
    
    print("="*50)
    print("FINAL DEVELOPMENT COMBINATION PREVIEW")
    print("="*50)
    print(f"ID: {combination['id']}")
    print(f"Name: {combination['name']}")
    print(f"Film Stock: {film_stock['brand'] + ' ' + film_stock['name'] if film_stock else 'Unknown'}")
    print(f"Shooting ISO: {iso_text}")
    print(f"Push/Pull: {push_pull_text}")
    print(f"Developer: {developer['name'] + ' (' + developer['manufacturer'] + ')' if developer else 'Unknown'}")
    print(f"Dilution: {dilution_info}")
    print(f"Temperature: {combination['temperatureF']}°F")
    print(f"Time: {combination['timeMinutes']} minutes")
    print(f"Agitation: {combination['agitationSchedule']}")
    print(f"Notes: {combination['notes'] or 'None'}")
    print("="*50)

def main():
    """Main function"""
    clear_screen()
    show_header()
    
    # Load existing data
    combinations = load_development_combinations()
    film_stocks = load_film_stocks()
    developers = load_developers()
    
    print(f"Loaded {len(combinations)} existing development combinations.")
    print(f"Loaded {len(film_stocks)} film stocks and {len(developers)} developers.")
    
    if not film_stocks:
        print("❌ No film stocks found. Please add film stocks first using add_film_stock.py")
        return
    
    if not developers:
        print("❌ No developers found. Please add developers first using add_developer.py")
        return
    
    while True:
        print("\n" + "-" * 40)
        print("Adding new development combination...")
        input("Press Enter to continue...")
        
        # Generate new UUID
        new_uuid = generate_new_uuid()
        
        # Collect combination information with back navigation
        combination_data = collect_combination_data(film_stocks, developers, new_uuid)
        
        if combination_data is None:
            clear_screen()
            show_header()
            print("❌ Development combination creation cancelled.")
            if not get_user_input("\nAdd another combination? (yes/no): ", input_type='bool', allow_back=False):
                break
            continue
        
        # Final confirmation
        display_combination(combination_data, film_stocks, developers)
        
        if get_user_input("\nAdd this development combination? (yes/no): ", input_type='bool', allow_back=False):
            # Use the GitHub issue helper to handle submission
            def save_locally():
                combinations.append(combination_data)
                save_development_combinations(combinations)
            
            handle_combination_submission(combination_data, film_stocks, developers, save_locally)
        else:
            clear_screen()
            show_header()
            print("❌ Development combination not added.")
        
        # Ask if user wants to add another
        if not get_user_input("\nAdd another development combination? (yes/no): ", input_type='bool', allow_back=False):
            break
    
    clear_screen()
    show_header()
    print(f"🎉 Finished! Total development combinations: {len(combinations)}")

if __name__ == "__main__":
    main() 