#!/usr/bin/env python3
"""
Script to add new film stocks to the film_stocks.json file
"""

import json
import os
import uuid
from typing import List, Dict, Any, Optional
from github_issue_helper import handle_film_stock_submission

def get_data_file_path(filename: str) -> str:
    """Get the full path to a data file in the root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    return os.path.join(parent_dir, filename)

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def show_header():
    """Display the application header"""
    print("🎞️ Film Stock Addition Tool")
    print("=" * 30)
    print("💡 Tip: Type '<' or 'back' at any prompt to go back to the previous field")
    print()

def load_film_stocks() -> List[Dict[str, Any]]:
    """Load existing film stocks from JSON file"""
    film_stocks_path = get_data_file_path('film_stocks.json')
    if not os.path.exists(film_stocks_path):
        return []
    
    try:
        with open(film_stocks_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Error reading film_stocks.json file. Starting with empty list.")
        return []

def save_film_stocks(film_stocks: List[Dict[str, Any]]) -> None:
    """Save film stocks list to JSON file"""
    film_stocks_path = get_data_file_path('film_stocks.json')
    with open(film_stocks_path, 'w', encoding='utf-8') as f:
        json.dump(film_stocks, f, indent=2, ensure_ascii=False)

def generate_new_uuid() -> str:
    """Generate a new UUID for a film stock"""
    return str(uuid.uuid4())

def get_user_input(prompt: str, required: bool = True, input_type: str = 'str', allow_back: bool = True) -> Any:
    """Get user input with validation and back navigation"""
    back_commands = ['<', 'back']
    
    while True:
        try:
            if allow_back:
                value = input(prompt + " (or '<' to go back): ").strip()
            else:
                value = input(prompt).strip()
            
            # Check for back command
            if allow_back and value.lower() in back_commands:
                return "<<<BACK>>>"
            
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
            elif input_type == 'list':
                if not value:
                    return []
                return [note.strip() for note in value.split(',') if note.strip()]
            else:
                return value
                
        except ValueError:
            if input_type == 'float':
                print("Invalid input. Please enter a valid number (decimals allowed).")
            else:
                print("Invalid input. Please enter a valid number.")
            continue

def select_color_type(allow_back: bool = True) -> str:
    """Let user select color type from available options"""
    types = ["bw", "color", "slide"]
    
    while True:
        print("\nSelect color type:")
        for i, color_type in enumerate(types, 1):
            print(f"{i}. {color_type}")
        
        try:
            if allow_back:
                choice_str = input("Enter choice (1-3) (or '<' to go back): ").strip()
            else:
                choice_str = input("Enter choice (1-3): ").strip()
            
            # Check for back command
            if allow_back and choice_str.lower() in ['<', 'back']:
                return "<<<BACK>>>"
            
            choice = int(choice_str)
            if 1 <= choice <= len(types):
                return types[choice - 1]
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_current_progress(film_stock_data: Dict[str, Any], current_step: int, total_steps: int) -> None:
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
        ("brand", "Brand"),
        ("name", "Name"),
        ("iso_speed", "ISO Speed"),
        ("color_type", "Color Type"),
        ("grain_structure", "Grain Structure"),
        ("reciprocity_failure", "Reciprocity Failure"),
        ("discontinued", "Discontinued"),
        ("description", "Description"),
        ("manufacturer_notes", "Manufacturer Notes")
    ]
    
    for i, (field_key, field_name) in enumerate(all_fields, 1):
        value = film_stock_data.get(field_key)
        
        if value is not None:
            # Field has been filled
            if field_key == "discontinued":
                display_value = "Yes" if value else "No"
            elif field_key == "manufacturer_notes" and isinstance(value, list):
                display_value = f"{len(value)} note(s)" if value else "None"
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

def collect_film_stock_data(new_uuid: str) -> Optional[Dict[str, Any]]:
    """Collect film stock data with simple back navigation"""
    film_stock_data = {"id": new_uuid}
    
    # Field collection order and info
    fields = [
        ("brand", "Brand", True, lambda: get_user_input("Brand/Manufacturer: ")),
        ("name", "Name", True, lambda: get_user_input("Film name: ")),
        ("iso_speed", "ISO Speed", True, lambda: get_user_input("ISO speed: ", input_type='float')),
        ("color_type", "Color type", True, lambda: select_color_type()),
        ("grain_structure", "Grain structure", False, lambda: get_user_input("Grain structure (or press Enter for none): ", required=False)),
        ("reciprocity_failure", "Reciprocity failure", False, lambda: get_user_input("Reciprocity failure characteristics (or press Enter for none): ", required=False)),
        ("discontinued", "Discontinued", True, lambda: 1 if get_user_input("Is discontinued? (yes/no): ", input_type='bool') else 0),
        ("description", "Description", False, lambda: get_user_input("Description (or press Enter for none): ", required=False)),
        ("manufacturer_notes", "Manufacturer notes", False, lambda: get_user_input("Manufacturer notes (comma-separated, or press Enter for none): ", required=False, input_type='list'))
    ]
    
    current_field = 0
    
    while current_field < len(fields):
        # Clear screen and show header
        clear_screen()
        show_header()
        
        field_key, field_name, required, input_func = fields[current_field]
        
        # Show progress
        display_current_progress(film_stock_data, current_field + 1, len(fields))
        
        print(f"\n--- {field_name} ---")
        
        # Get input for current field
        if current_field == 0:
            # First field, no back option
            if field_key == "brand":
                result = get_user_input("Brand/Manufacturer: ", allow_back=False)
            elif field_key == "color_type":
                result = select_color_type(allow_back=False)
            else:
                result = input_func()
        else:
            # Regular field with back option
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
        film_stock_data[field_key] = result
        current_field += 1
    
    return film_stock_data

def display_film_stock(film_stock: Dict[str, Any]) -> None:
    """Display a film stock's information for confirmation"""
    clear_screen()
    show_header()
    
    print("="*50)
    print("FINAL FILM STOCK PREVIEW")
    print("="*50)
    print(f"ID: {film_stock['id']}")
    print(f"Brand: {film_stock['brand']}")
    print(f"Name: {film_stock['name']}")
    print(f"ISO Speed: {film_stock['iso_speed']}")
    print(f"Color Type: {film_stock['color_type']}")
    print(f"Grain Structure: {film_stock['grain_structure']}")
    print(f"Reciprocity Failure: {film_stock['reciprocity_failure']}")
    print(f"Discontinued: {'Yes' if film_stock['discontinued'] else 'No'}")
    print(f"Description: {film_stock['description']}")
    
    if film_stock['manufacturer_notes']:
        print("Manufacturer Notes:")
        for note in film_stock['manufacturer_notes']:
            print(f"  - {note}")
    else:
        print("Manufacturer Notes: None")
    print("="*50)

def main():
    """Main function"""
    clear_screen()
    show_header()
    
    # Load existing film stocks
    film_stocks = load_film_stocks()
    print(f"Loaded {len(film_stocks)} existing film stocks.")
    
    while True:
        print("\n" + "-" * 30)
        print("Adding new film stock...")
        input("Press Enter to continue...")
        
        # Generate new UUID
        new_uuid = generate_new_uuid()
        
        # Collect film stock information with back navigation
        film_stock_data = collect_film_stock_data(new_uuid)
        
        if film_stock_data is None:
            clear_screen()
            show_header()
            print("❌ Film stock creation cancelled.")
            if not get_user_input("\nAdd another film stock? (yes/no): ", input_type='bool', allow_back=False):
                break
            continue
        
        # Final confirmation
        display_film_stock(film_stock_data)
        
        if get_user_input("\nAdd this film stock? (yes/no): ", input_type='bool', allow_back=False):
            # Use the GitHub issue helper to handle submission
            def save_locally():
                film_stocks.append(film_stock_data)
                save_film_stocks(film_stocks)
            
            handle_film_stock_submission(film_stock_data, save_locally)
        else:
            clear_screen()
            show_header()
            print("❌ Film stock not added.")
        
        # Ask if user wants to add another
        if not get_user_input("\nAdd another film stock? (yes/no): ", input_type='bool', allow_back=False):
            break
    
    clear_screen()
    show_header()
    print(f"🎉 Finished! Total film stocks: {len(film_stocks)}")

if __name__ == "__main__":
    main() 