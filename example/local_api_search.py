#!/usr/bin/env python3
"""
Darkroom Search Tool
A command-line tool for locally searching film stocks, developers, and development combinations
with fuzzy search capabilities and custom combination management. Does not access the Dorkroom Static API GitHub repository.
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse

try:
    from rapidfuzz import fuzz, process
    from tabulate import tabulate
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Missing required packages. Please install them with:")
    print("pip install rapidfuzz tabulate colorama")
    exit(1)


@dataclass
class SearchResult:
    """Container for search results with score"""
    item: Dict[Any, Any]
    score: int
    type: str


class DarkroomAPI:
    """Main class for managing darkroom data and search functionality"""
    
    def __init__(self, data_dir: str = ".."):
        self.data_dir = data_dir
        self.films = []
        self.developers = []
        self.combinations = []
        self.formats = []
        self.custom_combinations = []
        self.custom_combinations_file = os.path.join(data_dir, "custom_combinations.json")
        
        self.load_data()
        self.load_custom_combinations()
    
    def load_data(self):
        """Load all JSON data files"""
        try:
            with open(os.path.join(self.data_dir, "film_stocks.json"), 'r') as f:
                self.films = json.load(f)
            
            with open(os.path.join(self.data_dir, "developers.json"), 'r') as f:
                self.developers = json.load(f)
            
            with open(os.path.join(self.data_dir, "development_combinations.json"), 'r') as f:
                self.combinations = json.load(f)
            
            with open(os.path.join(self.data_dir, "formats.json"), 'r') as f:
                self.formats = json.load(f)
                
            print(f"{Fore.GREEN}✓ Loaded {len(self.films)} films, {len(self.developers)} developers, {len(self.combinations)} combinations")
        except FileNotFoundError as e:
            print(f"{Fore.RED}Error loading data files: {e}")
            exit(1)
    
    def load_custom_combinations(self):
        """Load custom combinations from file"""
        if os.path.exists(self.custom_combinations_file):
            try:
                with open(self.custom_combinations_file, 'r') as f:
                    self.custom_combinations = json.load(f)
                print(f"{Fore.GREEN}✓ Loaded {len(self.custom_combinations)} custom combinations")
            except json.JSONDecodeError:
                print(f"{Fore.YELLOW}Warning: Could not parse custom combinations file")
                self.custom_combinations = []
        else:
            self.custom_combinations = []
    
    def save_custom_combinations(self):
        """Save custom combinations to file"""
        try:
            with open(self.custom_combinations_file, 'w') as f:
                json.dump(self.custom_combinations, f, indent=2)
            print(f"{Fore.GREEN}✓ Saved custom combinations to {self.custom_combinations_file}")
        except Exception as e:
            print(f"{Fore.RED}Error saving custom combinations: {e}")
    
    def fuzzy_search_films(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search films using improved fuzzy matching"""
        results = []
        query_lower = query.lower()
        
        for film in self.films:
            # Create primary searchable text (name and brand - most important)
            primary_text = f"{film['brand']} {film['name']}".lower()
            
            # Create secondary searchable text (other attributes)
            secondary_text = f"{film['iso_speed']} {film['color_type']}".lower()
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
    
    def fuzzy_search_developers(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search developers using improved fuzzy matching"""
        results = []
        query_lower = query.lower()
        
        for dev in self.developers:
            # Create primary searchable text (name and manufacturer - most important)
            primary_text = f"{dev['name']} {dev['manufacturer']}".lower()
            
            # Create secondary searchable text (other attributes)
            secondary_text = f"{dev['type']} {dev['film_or_paper']}".lower()
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
    
    def fuzzy_search_combinations(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search development combinations using improved fuzzy matching"""
        results = []
        query_lower = query.lower()
        all_combinations = self.combinations + self.custom_combinations
        
        for combo in all_combinations:
            # Create primary searchable text (combination name - most important)
            primary_text = combo['name'].lower()
            
            # Create enhanced searchable text with film and developer info
            enhanced_text = primary_text
            
            # Add film info if available
            if combo.get('film_stock_id'):
                film = self.get_film_by_id(combo['film_stock_id'])
                if film:
                    enhanced_text += f" {film['brand']} {film['name']}".lower()
            
            # Add developer info if available
            if combo.get('developer_id'):
                developer = self.get_developer_by_id(combo['developer_id'])
                if developer:
                    enhanced_text += f" {developer['name']}".lower()
            
            # Create secondary searchable text (notes)
            secondary_text = ""
            if combo.get('notes'):
                secondary_text = combo['notes'].lower()
            
            # Calculate multiple fuzzy scores
            primary_token_score = fuzz.token_sort_ratio(query_lower, primary_text)
            primary_partial_score = fuzz.partial_ratio(query_lower, primary_text)
            primary_ratio_score = fuzz.ratio(query_lower, primary_text)
            
            # Enhanced text scores (includes film/developer names)
            enhanced_partial_score = fuzz.partial_ratio(query_lower, enhanced_text)
            enhanced_token_score = fuzz.token_sort_ratio(query_lower, enhanced_text)
            
            # Secondary scores
            secondary_partial_score = fuzz.partial_ratio(query_lower, secondary_text) if secondary_text else 0
            
            # Weighted composite score
            composite_score = (
                primary_token_score * 0.25 +
                primary_partial_score * 0.2 +
                primary_ratio_score * 0.15 +
                enhanced_partial_score * 0.2 +
                enhanced_token_score * 0.15 +
                secondary_partial_score * 0.05
            )
            
            # Bonus for exact word matches
            query_words = query_lower.split()
            enhanced_words = enhanced_text.split()
            exact_word_matches = sum(1 for word in query_words if word in enhanced_words)
            if exact_word_matches > 0:
                composite_score += exact_word_matches * 8
            
            # Bonus for matches at the beginning
            if primary_text.startswith(query_lower) or enhanced_text.startswith(query_lower):
                composite_score += 12
            elif any(word.startswith(query_lower) for word in enhanced_words):
                composite_score += 8
            
            if composite_score > 35:
                combo_type = "custom" if combo in self.custom_combinations else "standard"
                results.append(SearchResult(combo, int(composite_score), combo_type))
        
        return sorted(results, key=lambda x: x.score, reverse=True)[:limit]
    
    def search_all(self, query: str, limit: int = 5) -> Dict[str, List[SearchResult]]:
        """Search across all categories"""
        return {
            "films": self.fuzzy_search_films(query, limit),
            "developers": self.fuzzy_search_developers(query, limit),
            "combinations": self.fuzzy_search_combinations(query, limit)
        }
    
    def get_film_by_id(self, film_id: int) -> Optional[Dict]:
        """Get film by ID"""
        return next((f for f in self.films if f['id'] == film_id), None)
    
    def get_developer_by_id(self, dev_id: int) -> Optional[Dict]:
        """Get developer by ID"""
        return next((d for d in self.developers if d['id'] == dev_id), None)
    
    def create_custom_combination(self, name: str, film_stock_id: int, developer_id: int, 
                                dilution_id: int, temperature_f: float, time_minutes: float,
                                agitation_schedule: str, push_pull: int = 0, notes: str = ""):
        """Create a new custom development combination"""
        
        # Validate film and developer exist
        film = self.get_film_by_id(film_stock_id)
        developer = self.get_developer_by_id(developer_id)
        
        if not film:
            raise ValueError(f"Film with ID {film_stock_id} not found")
        if not developer:
            raise ValueError(f"Developer with ID {developer_id} not found")
        
        # Find the dilution
        dilution = next((d for d in developer['dilutions'] if d['id'] == dilution_id), None)
        if not dilution:
            raise ValueError(f"Dilution with ID {dilution_id} not found for developer {developer['name']}")
        
        # Generate new ID
        max_id = max([c.get('id', 0) for c in self.custom_combinations] + [0])
        new_id = max_id + 1
        
        custom_combo = {
            "id": new_id,
            "name": name,
            "film_stock_id": film_stock_id,
            "temperature_f": temperature_f,
            "time_minutes": time_minutes,
            "agitation_schedule": agitation_schedule,
            "push_pull": push_pull,
            "notes": notes,
            "developer_id": developer_id,
            "dilution_id": dilution_id,
            "custom_dilution": None,
            "created_date": datetime.now().isoformat()
        }
        
        self.custom_combinations.append(custom_combo)
        self.save_custom_combinations()
        
        return custom_combo


class DarkroomDisplay:
    """Class for formatting and displaying search results"""
    
    @staticmethod
    def display_film(film: Dict, show_details: bool = True):
        """Display film information in a formatted way"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{film['brand']} {film['name']}")
        print(f"{Fore.CYAN}{'='*60}")
        
        basic_info = [
            ["ISO Speed", film['iso_speed']],
            ["Type", film['color_type'].upper()],
            ["ID", film['id']],
            ["Status", "Discontinued" if film.get('discontinued', 0) else "Available"]
        ]
        
        print(f"{Fore.WHITE}{tabulate(basic_info, tablefmt='grid')}")
        
        if show_details and film.get('description'):
            print(f"\n{Fore.YELLOW}Description:")
            print(f"{Fore.WHITE}{film['description']}")
        
        if show_details and film.get('manufacturer_notes'):
            print(f"\n{Fore.YELLOW}Key Features:")
            for note in film['manufacturer_notes']:
                print(f"{Fore.WHITE}• {note}")
    
    @staticmethod
    def display_developer(developer: Dict, show_details: bool = True):
        """Display developer information in a formatted way"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}{developer['name']} - {developer['manufacturer']}")
        print(f"{Fore.MAGENTA}{'='*60}")
        
        basic_info = [
            ["Type", developer['type'].title()],
            ["For", developer['film_or_paper'].title()],
            ["ID", developer['id']],
            ["Status", "Discontinued" if developer.get('discontinued', 0) else "Available"]
        ]
        
        print(f"{Fore.WHITE}{tabulate(basic_info, tablefmt='grid')}")
        
        if developer.get('dilutions'):
            print(f"\n{Fore.YELLOW}Available Dilutions:")
            dilution_table = []
            for dilution in developer['dilutions']:
                dilution_table.append([dilution['id'], dilution['name'], dilution['dilution']])
            print(f"{Fore.WHITE}{tabulate(dilution_table, headers=['ID', 'Name', 'Ratio'], tablefmt='grid')}")
        
        if show_details and developer.get('notes'):
            print(f"\n{Fore.YELLOW}Notes:")
            print(f"{Fore.WHITE}{developer['notes']}")
    
    @staticmethod
    def display_combination(combo: Dict, api: DarkroomAPI, combo_type: str = "standard"):
        """Display development combination with enhanced information"""
        print(f"\n{Fore.GREEN}{'='*60}")
        combo_title = f"{combo['name']}"
        if combo_type == "custom":
            combo_title += " (Custom)"
        print(f"{Fore.GREEN}{combo_title}")
        print(f"{Fore.GREEN}{'='*60}")
        
        # Get film and developer details
        film = api.get_film_by_id(combo['film_stock_id'])
        developer = api.get_developer_by_id(combo['developer_id'])
        
        film_name = f"{film['brand']} {film['name']}" if film else f"Film ID {combo['film_stock_id']}"
        dev_name = developer['name'] if developer else f"Developer ID {combo['developer_id']}"
        
        # Find dilution name
        dilution_name = "Unknown"
        if developer and combo.get('dilution_id'):
            dilution = next((d for d in developer['dilutions'] if d['id'] == combo['dilution_id']), None)
            if dilution:
                dilution_name = f"{dilution['name']} ({dilution['dilution']})"
        
        combo_info = [
            ["Film", film_name],
            ["Developer", dev_name],
            ["Dilution", dilution_name],
            ["Temperature", f"{combo['temperature_f']}°F"],
            ["Time", f"{combo['time_minutes']} minutes"],
            ["Agitation", combo['agitation_schedule']],
            ["Push/Pull", f"{combo['push_pull']:+d} stop" if combo['push_pull'] != 0 else "Normal"],
        ]
        
        if combo_type == "custom" and combo.get('created_date'):
            combo_info.append(["Created", combo['created_date'][:10]])
        
        print(f"{Fore.WHITE}{tabulate(combo_info, tablefmt='grid')}")
        
        if combo.get('notes'):
            print(f"\n{Fore.YELLOW}Notes:")
            print(f"{Fore.WHITE}{combo['notes']}")
    
    @staticmethod
    def display_search_results(results: Dict[str, List[SearchResult]], api: DarkroomAPI):
        """Display search results across all categories"""
        total_results = sum(len(category_results) for category_results in results.values())
        
        if total_results == 0:
            print(f"{Fore.RED}No results found.")
            return
        
        print(f"\n{Fore.WHITE}Found {total_results} results:")
        
        # Display Films
        if results["films"]:
            print(f"\n{Fore.CYAN}FILMS ({len(results['films'])} results):")
            for i, result in enumerate(results["films"], 1):
                film = result.item
                status = "(Discontinued)" if film.get('discontinued', 0) else ""
                print(f"{Fore.WHITE}{i:2}. {film['brand']} {film['name']} - ISO {film['iso_speed']} ({film['color_type']}) {status}")
                print(f"    {Fore.BLUE}Match: {result.score}% | ID: {film['id']}")
        
        # Display Developers
        if results["developers"]:
            print(f"\n{Fore.MAGENTA}DEVELOPERS ({len(results['developers'])} results):")
            for i, result in enumerate(results["developers"], 1):
                dev = result.item
                status = "(Discontinued)" if dev.get('discontinued', 0) else ""
                print(f"{Fore.WHITE}{i:2}. {dev['name']} - {dev['manufacturer']} ({dev['type']}) {status}")
                print(f"    {Fore.BLUE}Match: {result.score}% | ID: {dev['id']}")
        
        # Display Combinations
        if results["combinations"]:
            print(f"\n{Fore.GREEN}COMBINATIONS ({len(results['combinations'])} results):")
            for i, result in enumerate(results["combinations"], 1):
                combo = result.item
                combo_type_label = "(Custom)" if result.type == "custom" else ""
                print(f"{Fore.WHITE}{i:2}. {combo['name']} {combo_type_label}")
                print(f"    {Fore.BLUE}Match: {result.score}% | {combo['time_minutes']}min @ {combo['temperature_f']}°F")


class InteractiveInterface:
    """Interactive terminal interface for the darkroom tool"""
    
    def __init__(self, api: DarkroomAPI):
        self.api = api
        self.display = DarkroomDisplay()
        self.running = True
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Display the application header"""
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🎞️  DARKROOM SEARCH TOOL  🎞️")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.WHITE}Films: {len(self.api.films)} | Developers: {len(self.api.developers)} | Combinations: {len(self.api.combinations)} | Custom: {len(self.api.custom_combinations)}")
        print()
    
    def show_main_menu(self):
        """Display the main menu options"""
        print(f"{Fore.YELLOW}🔍 MAIN MENU")
        print(f"{Fore.WHITE}1. Search All")
        print(f"{Fore.WHITE}2. Search Films")
        print(f"{Fore.WHITE}3. Search Developers") 
        print(f"{Fore.WHITE}4. Search Combinations")
        print(f"{Fore.WHITE}5. Show Item by ID")
        print(f"{Fore.WHITE}6. List Items")
        print(f"{Fore.WHITE}7. Create Custom Combination")
        print(f"{Fore.WHITE}8. Help")
        print(f"{Fore.RED}9. Exit")
        print()
    
    def get_user_input(self, prompt: str, input_type: type = str, required: bool = True):
        """Get validated user input"""
        while True:
            try:
                user_input = input(f"{Fore.CYAN}{prompt}: {Fore.WHITE}").strip()
                
                if not user_input and required:
                    print(f"{Fore.RED}This field is required. Please try again.")
                    continue
                elif not user_input and not required:
                    return None
                
                if input_type == int:
                    return int(user_input)
                elif input_type == float:
                    return float(user_input)
                else:
                    return user_input
                    
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a valid {input_type.__name__}.")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operation cancelled.")
                return None
    
    def wait_for_enter(self):
        """Wait for user to press enter"""
        input(f"\n{Fore.BLUE}Press Enter to continue...")
    
    def search_interface(self, search_type: str = "all"):
        """Interactive search interface"""
        self.clear_screen()
        self.show_header()
        
        search_types = {
            "all": "All Categories",
            "film": "Films", 
            "developer": "Developers",
            "combination": "Combinations"
        }
        
        print(f"{Fore.YELLOW}🔍 SEARCH {search_types[search_type].upper()}")
        print()
        
        query = self.get_user_input("Enter search query")
        if not query:
            return
        
        limit = self.get_user_input("Number of results (default: 5)", int, False) or 5
        
        print(f"\n{Fore.BLUE}Searching for '{query}'...")
        print()
        
        if search_type == "all":
            results = self.api.search_all(query, limit)
            self.display.display_search_results(results, self.api)
        elif search_type == "film":
            results = self.api.fuzzy_search_films(query, limit)
            if results:
                for result in results:
                    self.display.display_film(result.item, False)
            else:
                print(f"{Fore.RED}No films found matching '{query}'")
        elif search_type == "developer":
            results = self.api.fuzzy_search_developers(query, limit)
            if results:
                for result in results:
                    self.display.display_developer(result.item, False)
            else:
                print(f"{Fore.RED}No developers found matching '{query}'")
        elif search_type == "combination":
            results = self.api.fuzzy_search_combinations(query, limit)
            if results:
                for result in results:
                    self.display.display_combination(result.item, self.api, result.type)
            else:
                print(f"{Fore.RED}No combinations found matching '{query}'")
        
        self.wait_for_enter()
    
    def show_item_interface(self):
        """Interface for showing specific items by ID"""
        self.clear_screen()
        self.show_header()
        
        print(f"{Fore.YELLOW}📋 SHOW ITEM BY ID")
        print()
        print(f"{Fore.WHITE}1. Film")
        print(f"{Fore.WHITE}2. Developer")
        print(f"{Fore.WHITE}3. Go Back")
        print()
        
        choice = self.get_user_input("Select item type (1-3)", int)
        if choice == 3 or choice is None:
            return
        
        item_id = self.get_user_input("Enter item ID", int)
        if item_id is None:
            return
        
        print()
        
        if choice == 1:
            film = self.api.get_film_by_id(item_id)
            if film:
                self.display.display_film(film, True)
            else:
                print(f"{Fore.RED}Film with ID {item_id} not found")
        
        elif choice == 2:
            developer = self.api.get_developer_by_id(item_id)
            if developer:
                self.display.display_developer(developer, True)
            else:
                print(f"{Fore.RED}Developer with ID {item_id} not found")
        
        self.wait_for_enter()
    
    def list_items_interface(self):
        """Interface for listing items"""
        self.clear_screen()
        self.show_header()
        
        print(f"{Fore.YELLOW}📋 LIST ITEMS")
        print()
        print(f"{Fore.WHITE}1. Films")
        print(f"{Fore.WHITE}2. Developers")
        print(f"{Fore.WHITE}3. Combinations")
        print(f"{Fore.WHITE}4. Custom Combinations")
        print(f"{Fore.WHITE}5. Go Back")
        print()
        
        choice = self.get_user_input("Select list type (1-5)", int)
        if choice == 5 or choice is None:
            return
        
        limit = self.get_user_input("Number of items to show (default: 20)", int, False) or 20
        
        print()
        
        if choice == 1:
            print(f"{Fore.CYAN}Available Films (showing first {limit}):")
            for i, film in enumerate(self.api.films[:limit], 1):
                status = " (Discontinued)" if film.get('discontinued', 0) else ""
                print(f"{i:3}. [{film['id']:3}] {film['brand']} {film['name']} - ISO {film['iso_speed']}{status}")
        
        elif choice == 2:
            print(f"{Fore.MAGENTA}Available Developers (showing first {limit}):")
            for i, dev in enumerate(self.api.developers[:limit], 1):
                status = " (Discontinued)" if dev.get('discontinued', 0) else ""
                print(f"{i:3}. [{dev['id']:2}] {dev['name']} - {dev['manufacturer']}{status}")
        
        elif choice == 3:
            print(f"{Fore.GREEN}Available Combinations (showing first {limit}):")
            for i, combo in enumerate(self.api.combinations[:limit], 1):
                print(f"{i:3}. [{combo['id']:2}] {combo['name']}")
        
        elif choice == 4:
            if self.api.custom_combinations:
                print(f"{Fore.GREEN}Custom Combinations ({len(self.api.custom_combinations)}):")
                for i, combo in enumerate(self.api.custom_combinations, 1):
                    print(f"{i:3}. [{combo['id']:2}] {combo['name']} (Created: {combo.get('created_date', 'Unknown')[:10]})")
            else:
                print(f"{Fore.YELLOW}No custom combinations found")
        
        self.wait_for_enter()
    
    def create_combination_interface(self):
        """Interface for creating custom combinations"""
        self.clear_screen()
        self.show_header()
        
        print(f"{Fore.YELLOW}➕ CREATE CUSTOM COMBINATION")
        print()
        
        # Get combination details
        name = self.get_user_input("Combination name")
        if not name:
            return
        
        # Show available films
        print(f"\n{Fore.CYAN}Recent Films (for full list, use 'List Items'):")
        for film in self.api.films[:10]:
            print(f"  [{film['id']:3}] {film['brand']} {film['name']} - ISO {film['iso_speed']}")
        
        film_id = self.get_user_input("Film ID", int)
        if film_id is None:
            return
        
        # Validate film exists
        film = self.api.get_film_by_id(film_id)
        if not film:
            print(f"{Fore.RED}Film with ID {film_id} not found")
            self.wait_for_enter()
            return
        
        # Show available developers
        print(f"\n{Fore.MAGENTA}Recent Developers (for full list, use 'List Items'):")
        for dev in self.api.developers[:10]:
            print(f"  [{dev['id']:2}] {dev['name']} - {dev['manufacturer']}")
        
        developer_id = self.get_user_input("Developer ID", int)
        if developer_id is None:
            return
        
        # Validate developer exists and show dilutions
        developer = self.api.get_developer_by_id(developer_id)
        if not developer:
            print(f"{Fore.RED}Developer with ID {developer_id} not found")
            self.wait_for_enter()
            return
        
        print(f"\n{Fore.YELLOW}Available Dilutions for {developer['name']}:")
        for dilution in developer.get('dilutions', []):
            print(f"  [{dilution['id']}] {dilution['name']} - {dilution['dilution']}")
        
        dilution_id = self.get_user_input("Dilution ID", int)
        if dilution_id is None:
            return
        
        # Validate dilution exists
        dilution = next((d for d in developer['dilutions'] if d['id'] == dilution_id), None)
        if not dilution:
            print(f"{Fore.RED}Dilution with ID {dilution_id} not found")
            self.wait_for_enter()
            return
        
        # Get development parameters
        temperature = self.get_user_input("Temperature (°F)", float)
        if temperature is None:
            return
        
        time = self.get_user_input("Development time (minutes)", float)
        if time is None:
            return
        
        agitation = self.get_user_input("Agitation schedule")
        if not agitation:
            return
        
        push_pull = self.get_user_input("Push/pull stops (0 for normal)", int, False) or 0
        notes = self.get_user_input("Notes (optional)", str, False) or ""
        
        # Create the combination
        try:
            combo = self.api.create_custom_combination(
                name, film_id, developer_id, dilution_id,
                temperature, time, agitation, push_pull, notes
            )
            print(f"\n{Fore.GREEN}✓ Successfully created custom combination!")
            self.display.display_combination(combo, self.api, "custom")
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}")
        
        self.wait_for_enter()
    
    def show_help(self):
        """Show help information"""
        self.clear_screen()
        self.show_header()
        
        print(f"{Fore.YELLOW}📖 HELP")
        print()
        print(f"{Fore.WHITE}This tool helps you search and manage darkroom film development data.")
        print()
        print(f"{Fore.CYAN}Features:")
        print(f"{Fore.WHITE}• Search films by brand, name, ISO, or type")
        print(f"{Fore.WHITE}• Search developers by name, manufacturer, or type")
        print(f"{Fore.WHITE}• Search development combinations")
        print(f"{Fore.WHITE}• View detailed information about any item")
        print(f"{Fore.WHITE}• Create custom development combinations")
        print(f"{Fore.WHITE}• List all available items")
        print()
        print(f"{Fore.CYAN}Tips:")
        print(f"{Fore.WHITE}• Use fuzzy search - partial matches work great!")
        print(f"{Fore.WHITE}• Try searching for 'kodak portra' or 'rodinal'")
        print(f"{Fore.WHITE}• Custom combinations are saved automatically")
        print(f"{Fore.WHITE}• Use Ctrl+C to cancel any operation")
        print()
        print(f"{Fore.CYAN}Command Line Usage:")
        print(f"{Fore.WHITE}• python darkroom_search.py search 'kodak'")
        print(f"{Fore.WHITE}• python darkroom_search.py list films")
        print(f"{Fore.WHITE}• python darkroom_search.py show film 15")
        
        self.wait_for_enter()
    
    def run(self):
        """Main interactive loop"""
        try:
            while self.running:
                self.clear_screen()
                self.show_header()
                self.show_main_menu()
                
                choice = self.get_user_input("Select option (1-9)", int)
                
                if choice == 1:
                    self.search_interface("all")
                elif choice == 2:
                    self.search_interface("film")
                elif choice == 3:
                    self.search_interface("developer")
                elif choice == 4:
                    self.search_interface("combination")
                elif choice == 5:
                    self.show_item_interface()
                elif choice == 6:
                    self.list_items_interface()
                elif choice == 7:
                    self.create_combination_interface()
                elif choice == 8:
                    self.show_help()
                elif choice == 9:
                    self.running = False
                    print(f"\n{Fore.GREEN}Thanks for using Darkroom Search Tool! 📸")
                else:
                    print(f"{Fore.RED}Invalid choice. Please select 1-9.")
                    self.wait_for_enter()
                    
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Goodbye! 👋")
            sys.exit(0)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Darkroom Search Tool")
    parser.add_argument("--data-dir", default=".", help="Directory containing JSON data files")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search films, developers, or combinations")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", choices=["film", "developer", "combination", "all"], 
                              default="all", help="Type of item to search for")
    search_parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
    search_parser.add_argument("--details", action="store_true", help="Show detailed information")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show specific item by ID")
    show_parser.add_argument("type", choices=["film", "developer", "combination"], help="Type of item")
    show_parser.add_argument("id", type=int, help="Item ID")
    
    # Create combination command
    create_parser = subparsers.add_parser("create", help="Create custom development combination")
    create_parser.add_argument("--name", required=True, help="Name for the combination")
    create_parser.add_argument("--film-id", type=int, required=True, help="Film stock ID")
    create_parser.add_argument("--developer-id", type=int, required=True, help="Developer ID")
    create_parser.add_argument("--dilution-id", type=int, required=True, help="Dilution ID")
    create_parser.add_argument("--temperature", type=float, required=True, help="Temperature in Fahrenheit")
    create_parser.add_argument("--time", type=float, required=True, help="Development time in minutes")
    create_parser.add_argument("--agitation", required=True, help="Agitation schedule")
    create_parser.add_argument("--push-pull", type=int, default=0, help="Push/pull stops")
    create_parser.add_argument("--notes", default="", help="Additional notes")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available items")
    list_parser.add_argument("type", choices=["films", "developers", "combinations", "custom"], 
                            help="Type of items to list")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of items to show")
    
    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Launch interactive interface")
    
    args = parser.parse_args()
    
    # Initialize API
    api = DarkroomAPI(args.data_dir)
    display = DarkroomDisplay()
    
    # If no command provided, launch interactive interface
    if not args.command:
        interactive = InteractiveInterface(api)
        interactive.run()
        return
    
    if args.command == "interactive":
        interactive = InteractiveInterface(api)
        interactive.run()
    
    elif args.command == "search":
        if args.type == "all":
            results = api.search_all(args.query, args.limit)
            display.display_search_results(results, api)
        elif args.type == "film":
            results = api.fuzzy_search_films(args.query, args.limit)
            for result in results:
                display.display_film(result.item, args.details)
        elif args.type == "developer":
            results = api.fuzzy_search_developers(args.query, args.limit)
            for result in results:
                display.display_developer(result.item, args.details)
        elif args.type == "combination":
            results = api.fuzzy_search_combinations(args.query, args.limit)
            for result in results:
                display.display_combination(result.item, api, result.type)
    
    elif args.command == "show":
        if args.type == "film":
            film = api.get_film_by_id(args.id)
            if film:
                display.display_film(film)
            else:
                print(f"{Fore.RED}Film with ID {args.id} not found")
        
        elif args.type == "developer":
            developer = api.get_developer_by_id(args.id)
            if developer:
                display.display_developer(developer)
            else:
                print(f"{Fore.RED}Developer with ID {args.id} not found")
    
    elif args.command == "create":
        try:
            combo = api.create_custom_combination(
                args.name, args.film_id, args.developer_id, args.dilution_id,
                args.temperature, args.time, args.agitation, args.push_pull, args.notes
            )
            print(f"{Fore.GREEN}✓ Created custom combination: {combo['name']}")
            display.display_combination(combo, api, "custom")
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}")
    
    elif args.command == "list":
        if args.type == "films":
            print(f"{Fore.CYAN}Available Films (showing first {args.limit}):")
            for i, film in enumerate(api.films[:args.limit], 1):
                status = " (Discontinued)" if film.get('discontinued', 0) else ""
                print(f"{i:3}. [{film['id']:3}] {film['brand']} {film['name']} - ISO {film['iso_speed']}{status}")
        
        elif args.type == "developers":
            print(f"{Fore.MAGENTA}Available Developers (showing first {args.limit}):")
            for i, dev in enumerate(api.developers[:args.limit], 1):
                status = " (Discontinued)" if dev.get('discontinued', 0) else ""
                print(f"{i:3}. [{dev['id']:2}] {dev['name']} - {dev['manufacturer']}{status}")
        
        elif args.type == "combinations":
            print(f"{Fore.GREEN}Available Combinations (showing first {args.limit}):")
            for i, combo in enumerate(api.combinations[:args.limit], 1):
                print(f"{i:3}. [{combo['id']:2}] {combo['name']}")
        
        elif args.type == "custom":
            if api.custom_combinations:
                print(f"{Fore.GREEN}Custom Combinations ({len(api.custom_combinations)}):")
                for i, combo in enumerate(api.custom_combinations, 1):
                    print(f"{i:3}. [{combo['id']:2}] {combo['name']}")
            else:
                print(f"{Fore.YELLOW}No custom combinations found")


if __name__ == "__main__":
    main() 