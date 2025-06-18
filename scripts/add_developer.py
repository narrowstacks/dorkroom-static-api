#!/usr/bin/env python3
"""
Script to add new developers to the developers.json file
"""

import json
import os
import uuid
from typing import List, Dict, Any, Optional
from github_issue_helper import handle_developer_submission

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
    print("🧪 Developer Addition Tool")
    print("=" * 30)
    print("💡 Tip: Type '<' or 'back' at any prompt to go back to the previous field")
    print()

def load_developers() -> List[Dict[str, Any]]:
    """Load existing developers from JSON file"""
    developers_path = get_data_file_path('developers.json')
    if not os.path.exists(developers_path):
        return []
    
    try:
        with open(developers_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Error reading developers.json file. Starting with empty list.")
        return []

def save_developers(developers: List[Dict[str, Any]]) -> None:
    """Save developers list to JSON file"""
    developers_path = get_data_file_path('developers.json')
    with open(developers_path, 'w', encoding='utf-8') as f:
        json.dump(developers, f, indent=2, ensure_ascii=False)

def generate_new_uuid() -> str:
    """Generate a new UUID for a developer"""
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
            elif input_type == 'bool':
                return value.lower() in ['yes', 'y', '1', 'true']
            elif input_type == 'list':
                if not value:
                    return []
                return [url.strip() for url in value.split(',') if url.strip()]
            else:
                return value
                
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue

def select_type(allow_back: bool = True) -> str:
    """Let user select developer type from available options"""
    types = ["concentrate", "powder"]
    
    while True:
        print("\nSelect developer type:")
        for i, dev_type in enumerate(types, 1):
            print(f"{i}. {dev_type}")
        
        try:
            if allow_back:
                choice_str = input("Enter choice (1-2) (or '<' to go back): ").strip()
            else:
                choice_str = input("Enter choice (1-2): ").strip()
            
            # Check for back command
            if allow_back and choice_str.lower() in ['<', 'back']:
                return "<<<BACK>>>"
            
            choice = int(choice_str)
            if 1 <= choice <= len(types):
                return types[choice - 1]
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def select_film_or_paper(allow_back: bool = True) -> str:
    """Let user select whether developer is for film or paper"""
    options = ["film", "paper"]
    
    while True:
        print("\nSelect film or paper:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        try:
            if allow_back:
                choice_str = input("Enter choice (1-2) (or '<' to go back): ").strip()
            else:
                choice_str = input("Enter choice (1-2): ").strip()
            
            # Check for back command
            if allow_back and choice_str.lower() in ['<', 'back']:
                return "<<<BACK>>>"
            
            choice = int(choice_str)
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_existing_developers(developers: List[Dict[str, Any]]) -> None:
    """Display list of existing developers for selection"""
    print("\nExisting developers:")
    for i, dev in enumerate(developers, 1):
        dilution_count = len(dev.get('dilutions', []))
        print(f"{i:2d}. {dev['name']} ({dev['manufacturer']}) - {dilution_count} dilutions")

def select_developer_to_copy(developers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Let user select a developer to copy dilutions from"""
    if not developers:
        print("No existing developers to copy from.")
        return None
    
    display_existing_developers(developers)
    
    while True:
        try:
            choice = input("\nEnter developer number to copy dilutions from (or press Enter to skip): ").strip()
            if not choice:
                return None
            
            dev_index = int(choice) - 1  # Convert to 0-based index
            
            if 0 <= dev_index < len(developers):
                selected_dev = developers[dev_index]
                if not selected_dev.get('dilutions'):
                    print("Selected developer has no dilutions to copy.")
                    continue
                return selected_dev
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(developers)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_dilutions(developers: List[Dict[str, Any]], allow_back: bool = True) -> Any:
    """Get dilutions from user input"""
    # Ask if they want to copy from existing developer
    if developers:
        copy_response = get_user_input("Do you want to copy dilutions from an existing developer? (yes/no)", input_type='bool', allow_back=allow_back)
        if copy_response == "<<<BACK>>>":
            return "<<<BACK>>>"
        
        if copy_response:
            selected_dev = select_developer_to_copy(developers)
            if selected_dev:
                print(f"\nCopying dilutions from {selected_dev['name']}:")
                for dilution in selected_dev['dilutions']:
                    print(f"  - {dilution['name']}: {dilution['dilution']}")
                
                use_response = get_user_input("Use these dilutions? (yes/no)", input_type='bool', allow_back=False)
                if use_response:
                    # Re-number the dilutions to start from 1
                    copied_dilutions = []
                    for i, dilution in enumerate(selected_dev['dilutions'], 1):
                        copied_dilutions.append({
                            "id": i,
                            "name": dilution['name'],
                            "dilution": dilution['dilution']
                        })
                    return copied_dilutions
    
    # Get number of dilutions to add (minimum 1)
    while True:
        try:
            num_input = get_user_input("\nHow many dilutions do you want to add? (minimum 1)", allow_back=allow_back)
            if num_input == "<<<BACK>>>":
                return "<<<BACK>>>"
            
            num_dilutions = int(num_input)
            if num_dilutions >= 1:
                break
            else:
                print("You must add at least 1 dilution.")
        except (ValueError, TypeError):
            print("Invalid input. Please enter a number.")
    
    dilutions = []
    print(f"\nEntering {num_dilutions} dilution(s):")
    
    for i in range(1, num_dilutions + 1):
        print(f"\nDilution {i}:")
        name = get_user_input(f"  Name (e.g., '1+4', 'Standard')", allow_back=False)
        dilution_ratio = get_user_input(f"  Ratio (e.g., '1+4', '1:15')", allow_back=False)
        
        dilutions.append({
            "id": i,
            "name": name,
            "dilution": dilution_ratio
        })
    
    return dilutions

def display_current_progress(developer_data: Dict[str, Any], current_step: int, total_steps: int) -> None:
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
        ("name", "Developer Name"),
        ("manufacturer", "Manufacturer"),
        ("type", "Type"),
        ("filmOrPaper", "Film/Paper"),
        ("workingLifeHours", "Working Life (hours)"),
        ("stockLifeMonths", "Stock Life (months)"),
        ("discontinued", "Discontinued"),
        ("notes", "Notes"),
        ("mixingInstructions", "Mixing Instructions"),
        ("safetyNotes", "Safety Notes"),
        ("datasheetUrl", "Datasheet URLs"),
        ("dilutions", "Dilutions")
    ]
    
    for i, (field_key, field_name) in enumerate(all_fields, 1):
        value = developer_data.get(field_key)
        
        if value is not None:
            # Field has been filled
            if field_key == "discontinued":
                display_value = "Yes" if value else "No"
            elif field_key == "dilutions" and isinstance(value, list):
                display_value = f"{len(value)} dilution(s)" if value else "None"
            elif field_key == "datasheetUrl" and isinstance(value, list):
                display_value = f"{len(value)} URL(s)" if value else "None"
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

def collect_developer_data(developers: List[Dict[str, Any]], new_uuid: str) -> Optional[Dict[str, Any]]:
    """Collect developer data with simple back navigation"""
    developer_data = {"id": new_uuid}
    
    # Field collection order and info
    fields = [
        ("name", "Developer name", True, lambda: get_user_input("Developer name: ")),
        ("manufacturer", "Manufacturer", True, lambda: get_user_input("Manufacturer: ")),
        ("type", "Type", True, lambda: select_type()),
        ("filmOrPaper", "Film or paper", True, lambda: select_film_or_paper()),
        ("workingLifeHours", "Working life (hours)", False, lambda: get_user_input("Working life in hours (or press Enter for none): ", required=False, input_type='int')),
        ("stockLifeMonths", "Stock life (months)", False, lambda: get_user_input("Stock life in months (or press Enter for none): ", required=False, input_type='int')),
        ("discontinued", "Discontinued", True, lambda: 1 if get_user_input("Is discontinued? (yes/no): ", input_type='bool') else 0),
        ("notes", "Notes", False, lambda: get_user_input("Notes (or press Enter for none): ", required=False)),
        ("mixingInstructions", "Mixing instructions", False, lambda: get_user_input("Mixing instructions (or press Enter for none): ", required=False)),
        ("safetyNotes", "Safety notes", False, lambda: get_user_input("Safety notes (or press Enter for none): ", required=False)),
        ("datasheetUrl", "Datasheet URLs", False, lambda: get_user_input("Datasheet URLs (comma-separated, or press Enter for none): ", required=False, input_type='list')),
        ("dilutions", "Dilutions", True, lambda: get_dilutions(developers))
    ]
    
    current_field = 0
    
    while current_field < len(fields):
        # Clear screen and show header
        clear_screen()
        show_header()
        
        field_key, field_name, required, input_func = fields[current_field]
        
        # Show progress
        display_current_progress(developer_data, current_field + 1, len(fields))
        
        print(f"\n--- {field_name} ---")
        
        # Get input for current field
        if current_field == 0:
            # First field, no back option
            if field_key == "name":
                result = get_user_input("Developer name: ", allow_back=False)
            elif field_key == "type":
                result = select_type(allow_back=False)
            elif field_key == "filmOrPaper":
                result = select_film_or_paper(allow_back=False)
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
        developer_data[field_key] = result
        current_field += 1
    
    return developer_data

def display_developer(developer: Dict[str, Any]) -> None:
    """Display a developer's information for confirmation"""
    clear_screen()
    show_header()
    
    print("="*50)
    print("FINAL DEVELOPER PREVIEW")
    print("="*50)
    print(f"ID: {developer['id']}")
    print(f"Name: {developer['name']}")
    print(f"Manufacturer: {developer['manufacturer']}")
    print(f"Type: {developer['type']}")
    print(f"Film or Paper: {developer['filmOrPaper']}")
    print(f"Working Life (hours): {developer['workingLifeHours']}")
    print(f"Stock Life (months): {developer['stockLifeMonths']}")
    print(f"Discontinued: {'Yes' if developer['discontinued'] else 'No'}")
    print(f"Notes: {developer['notes']}")
    print(f"Mixing Instructions: {developer['mixingInstructions']}")
    print(f"Safety Notes: {developer['safetyNotes']}")
    print(f"Datasheet URLs: {', '.join(developer['datasheetUrl']) if developer['datasheetUrl'] else 'None'}")
    
    if developer['dilutions']:
        print("Dilutions:")
        for dilution in developer['dilutions']:
            print(f"  - {dilution['name']}: {dilution['dilution']}")
    else:
        print("Dilutions: None")
    print("="*50)

def main():
    """Main function"""
    clear_screen()
    show_header()
    
    # Load existing developers
    developers = load_developers()
    print(f"Loaded {len(developers)} existing developers.")
    
    while True:
        print("\n" + "-" * 30)
        print("Adding new developer...")
        input("Press Enter to continue...")
        
        # Generate new UUID
        new_uuid = generate_new_uuid()
        
        # Collect developer information with back navigation
        developer_data = collect_developer_data(developers, new_uuid)
        
        if developer_data is None:
            clear_screen()
            show_header()
            print("❌ Developer creation cancelled.")
            if not get_user_input("\nAdd another developer? (yes/no): ", input_type='bool', allow_back=False):
                break
            continue
        
        # Final confirmation
        display_developer(developer_data)
        
        if get_user_input("\nAdd this developer? (yes/no): ", input_type='bool', allow_back=False):
            # Use the GitHub issue helper to handle submission
            def save_locally():
                developers.append(developer_data)
                save_developers(developers)
            
            handle_developer_submission(developer_data, save_locally)
        else:
            clear_screen()
            show_header()
            print("❌ Developer not added.")
        
        # Ask if user wants to add another
        if not get_user_input("\nAdd another developer? (yes/no): ", input_type='bool', allow_back=False):
            break
    
    clear_screen()
    show_header()
    print(f"🎉 Finished! Total developers: {len(developers)}")

if __name__ == "__main__":
    main() 