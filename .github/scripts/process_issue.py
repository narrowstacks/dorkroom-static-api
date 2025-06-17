#!/usr/bin/env python3
"""
GitHub Issue to PR Data Processor
Converts approved GitHub issues into JSON data and creates pull requests
"""

import argparse
import json
import os
import re
import sys
import uuid
from typing import Dict, List, Any, Optional, Tuple
import urllib.parse


def load_json_file(filename: str) -> List[Dict[str, Any]]:
    """Load JSON file safely"""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Error reading {filename}. Starting with empty list.")
        return []


def save_json_file(filename: str, data: List[Dict[str, Any]]) -> None:
    """Save JSON file with proper formatting"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_uuid() -> str:
    """Generate new UUID"""
    return str(uuid.uuid4())


def parse_issue_body(issue_body: str) -> Dict[str, str]:
    """Parse GitHub issue body and extract form data"""
    data = {}
    
    # Split the issue body into sections based on ### headers
    sections = re.split(r'\n### ', issue_body)
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Handle the first section which might not have ### stripped
        if section.startswith('###'):
            section = section[3:].strip()
        
        lines = section.split('\n', 1)  # Split into header and content
        if len(lines) < 2:
            continue
            
        field_name = lines[0].strip()
        field_content = lines[1].strip() if len(lines) > 1 else ""
        
        # Skip empty content
        if not field_content:
            continue
            
        # Clean up field name for consistent mapping
        field_key = field_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
        field_key = re.sub(r'[^a-z0-9_]', '', field_key)
        
        # Handle checkbox fields (- [x] format)
        if field_content.startswith('- [x]'):
            field_content = field_content[5:].strip()
        
        # Stop at comment sections or end-of-form markers
        if '<!-- ' in field_content:
            field_content = field_content.split('<!-- ')[0].strip()
            
        # Store the field data
        if field_content and field_key:
            data[field_key] = field_content
    
    return data


def clean_no_response(text: str) -> Optional[str]:
    """Clean up 'No response' placeholders from GitHub forms"""
    if not text or not text.strip():
        return None
    
    cleaned = text.strip()
    
    # Handle various "No response" formats from GitHub forms
    no_response_patterns = [
        "_No response_",
        "No response", 
        "_no response_",
        "no response",
        "_No Response_",
        "No Response"
    ]
    
    if cleaned in no_response_patterns:
        return None
    
    # Normalize whitespace and newlines for better JSON output
    # Replace multiple consecutive newlines with double newlines
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    # Clean up extra whitespace but preserve intentional line breaks
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    
    return cleaned.strip() if cleaned.strip() else None


def process_film_stock_issue(issue_data: Dict[str, str]) -> Dict[str, Any]:
    """Convert issue data to film stock JSON format"""
    
    # Map form fields to JSON structure
    film_stock = {
        "id": generate_uuid(),
        "brand": issue_data.get("brandmanufacturer", "").strip(),
        "name": issue_data.get("film_name", "").strip(),
        "iso_speed": float(issue_data.get("iso_speed", "0")) if issue_data.get("iso_speed", "").replace(".", "").isdigit() else 0.0,
        "color_type": convert_color_type(issue_data.get("film_type", "")),
        "grain_structure": clean_no_response(issue_data.get("grain_structure", "")),
        "reciprocity_failure": clean_no_response(issue_data.get("reciprocity_failure_characteristics", "")),
        "discontinued": 1 if "discontinued" in issue_data.get("current_production_status", "").lower() else 0,
        "description": clean_no_response(issue_data.get("description", "")),
        "manufacturer_notes": parse_manufacturer_notes(issue_data.get("manufacturer_notes", ""))
    }
    
    return film_stock


def process_developer_issue(issue_data: Dict[str, str]) -> Dict[str, Any]:
    """Convert issue data to developer JSON format"""
    
    developer = {
        "id": generate_uuid(),
        "name": issue_data.get("developer_name", "").strip(),
        "manufacturer": issue_data.get("manufacturer", "").strip(),
        "type": issue_data.get("developer_type", "").strip(),
        "film_or_paper": issue_data.get("intended_use", "").strip(),
        "working_life_hours": parse_numeric_field(issue_data.get("working_life_hours", "")),
        "stock_life_months": parse_numeric_field(issue_data.get("stock_life_months", "")),
        "discontinued": 1 if "discontinued" in issue_data.get("current_production_status", "").lower() else 0,
        "notes": clean_no_response(issue_data.get("notes", "")),
        "mixing_instructions": clean_no_response(issue_data.get("mixing_instructions", "")),
        "safety_notes": clean_no_response(issue_data.get("safety_notes", "")),
        "datasheet_url": parse_urls(issue_data.get("datasheet_urls", "")),
        "dilutions": parse_dilutions(issue_data.get("common_dilutions", ""))
    }
    
    return developer


def process_combination_issue(issue_data: Dict[str, str], film_stocks: List[Dict[str, Any]], developers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convert issue data to development combination JSON format"""
    
    # Find matching film stock
    film_brand = issue_data.get("film_brand", "").strip()
    film_name = issue_data.get("film_name", "").strip()
    film_stock_id = find_film_stock_id(film_stocks, film_brand, film_name)
    
    if not film_stock_id:
        print(f"Warning: Could not find film stock: {film_brand} {film_name}")
        return None
    
    # Find matching developer
    developer_manufacturer = issue_data.get("developer_manufacturer", "").strip()
    developer_name = issue_data.get("developer_name", "").strip()
    developer_id, dilution_id = find_developer_and_dilution(developers, developer_manufacturer, developer_name, issue_data.get("dilution_name", ""))
    
    if not developer_id:
        print(f"Warning: Could not find developer: {developer_manufacturer} {developer_name}")
        return None
    
    # Parse push/pull stops
    push_pull_str = issue_data.get("push_pull_stops", "0").strip()
    push_pull = parse_push_pull(push_pull_str)
    
    combination = {
        "id": generate_uuid(),
        "name": issue_data.get("combination_name", "").strip(),
        "film_stock_id": film_stock_id,
        "developer_id": developer_id,
        "dilution_id": dilution_id,
        "custom_dilution": None if dilution_id else issue_data.get("dilution_name", "").strip(),
        "temperature_f": int(float(issue_data.get("temperature_f", "68"))),
        "time_minutes": float(issue_data.get("time_minutes", "0")),
        "shooting_iso": float(issue_data.get("shooting_iso", "0")),
        "push_pull": push_pull,
        "agitation_schedule": issue_data.get("agitation_schedule", "").strip(),
        "notes": clean_no_response(issue_data.get("notes", ""))
    }
    
    return combination


def convert_color_type(film_type_text: str) -> str:
    """Convert form selection to database color_type"""
    if "Black & White" in film_type_text or "bw" in film_type_text.lower():
        return "bw"
    elif "Color Negative" in film_type_text or "color" in film_type_text.lower():
        return "color"
    elif "Slide" in film_type_text or "slide" in film_type_text.lower() or "transparency" in film_type_text.lower():
        return "slide"
    return "bw"  # default


def parse_manufacturer_notes(notes_text: str) -> List[str]:
    """Parse manufacturer notes into list"""
    cleaned_text = clean_no_response(notes_text)
    if not cleaned_text:
        return []
    
    # Split by newlines and clean up
    notes = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    return notes


def parse_numeric_field(field_value: str) -> Optional[int]:
    """Parse numeric field, return None if empty or invalid"""
    if not field_value.strip():
        return None
    
    try:
        return int(float(field_value.strip()))
    except ValueError:
        return None


def parse_urls(urls_text: str) -> List[str]:
    """Parse URLs from text"""
    if not urls_text.strip():
        return []
    
    urls = []
    for line in urls_text.split('\n'):
        line = line.strip()
        if line and (line.startswith('http://') or line.startswith('https://')):
            urls.append(line)
    
    return urls


def parse_dilutions(dilutions_text: str) -> List[Dict[str, Any]]:
    """Parse dilutions from text format 'Name:Ratio'"""
    if not dilutions_text.strip():
        return []
    
    dilutions = []
    dilution_id = 1
    
    for line in dilutions_text.split('\n'):
        line = line.strip()
        if ':' in line:
            name, ratio = line.split(':', 1)
            dilutions.append({
                "id": dilution_id,
                "name": name.strip(),
                "dilution": ratio.strip()
            })
            dilution_id += 1
    
    return dilutions


def find_film_stock_id(film_stocks: List[Dict[str, Any]], brand: str, name: str) -> Optional[str]:
    """Find film stock ID by brand and name"""
    for film in film_stocks:
        if (film.get("brand", "").lower() == brand.lower() and 
            film.get("name", "").lower() == name.lower()):
            return film.get("id")
    return None


def find_developer_and_dilution(developers: List[Dict[str, Any]], manufacturer: str, name: str, dilution_name: str) -> Tuple[Optional[str], Optional[int]]:
    """Find developer ID and dilution ID"""
    for dev in developers:
        if (dev.get("manufacturer", "").lower() == manufacturer.lower() and 
            dev.get("name", "").lower() == name.lower()):
            
            developer_id = dev.get("id")
            
            # Find dilution ID if specified
            dilution_id = None
            if dilution_name and "dilutions" in dev:
                for dilution in dev.get("dilutions", []):
                    if (dilution.get("name", "").lower() == dilution_name.lower() or
                        dilution.get("dilution", "").lower() == dilution_name.lower()):
                        dilution_id = dilution.get("id")
                        break
            
            return developer_id, dilution_id
    
    return None, None


def parse_push_pull(push_pull_str: str) -> int:
    """Parse push/pull string to integer"""
    if not push_pull_str.strip():
        return 0
    
    # Remove + and spaces, handle negative
    clean_str = push_pull_str.strip().replace('+', '')
    
    try:
        return int(float(clean_str))
    except ValueError:
        return 0


def check_for_duplicates(new_item: Dict[str, Any], existing_items: List[Dict[str, Any]], item_type: str) -> bool:
    """Check if item already exists in database"""
    if item_type == "film_stock":
        for item in existing_items:
            if (item.get("brand", "").lower() == new_item.get("brand", "").lower() and
                item.get("name", "").lower() == new_item.get("name", "").lower()):
                return True
    
    elif item_type == "developer":
        for item in existing_items:
            if (item.get("manufacturer", "").lower() == new_item.get("manufacturer", "").lower() and
                item.get("name", "").lower() == new_item.get("name", "").lower()):
                return True
    
    elif item_type == "combination":
        for item in existing_items:
            if (item.get("film_stock_id") == new_item.get("film_stock_id") and
                item.get("developer_id") == new_item.get("developer_id") and
                item.get("dilution_id") == new_item.get("dilution_id") and
                item.get("shooting_iso") == new_item.get("shooting_iso") and
                item.get("push_pull") == new_item.get("push_pull")):
                return True
    
    return False


def main():
    parser = argparse.ArgumentParser(description='Process GitHub issue to database entry')
    parser.add_argument('--issue-body', required=True, help='GitHub issue body text')
    parser.add_argument('--issue-type', required=True, choices=['film-stock', 'developer', 'combination'], help='Type of issue')
    parser.add_argument('--output-dir', default='.', help='Output directory for JSON files')
    parser.add_argument('--dry-run', action='store_true', help='Print data without saving')
    
    args = parser.parse_args()
    
    # Parse issue body
    issue_data = parse_issue_body(args.issue_body)
    
    if not issue_data:
        print("Error: Could not parse issue data")
        sys.exit(1)
    
    # Load existing data
    film_stocks = load_json_file(os.path.join(args.output_dir, 'film_stocks.json'))
    developers = load_json_file(os.path.join(args.output_dir, 'developers.json'))
    combinations = load_json_file(os.path.join(args.output_dir, 'development_combinations.json'))
    
    # Process based on issue type
    if args.issue_type == 'film-stock':
        new_item = process_film_stock_issue(issue_data)
        
        if check_for_duplicates(new_item, film_stocks, 'film_stock'):
            print(f"Error: Film stock '{new_item['brand']} {new_item['name']}' already exists")
            sys.exit(1)
        
        if args.dry_run:
            print("Film Stock Data:")
            print(json.dumps(new_item, indent=2))
        else:
            film_stocks.append(new_item)
            save_json_file(os.path.join(args.output_dir, 'film_stocks.json'), film_stocks)
            print(f"Added film stock: {new_item['brand']} {new_item['name']}")
    
    elif args.issue_type == 'developer':
        new_item = process_developer_issue(issue_data)
        
        if check_for_duplicates(new_item, developers, 'developer'):
            print(f"Error: Developer '{new_item['manufacturer']} {new_item['name']}' already exists")
            sys.exit(1)
        
        if args.dry_run:
            print("Developer Data:")
            print(json.dumps(new_item, indent=2))
        else:
            developers.append(new_item)
            save_json_file(os.path.join(args.output_dir, 'developers.json'), developers)
            print(f"Added developer: {new_item['manufacturer']} {new_item['name']}")
    
    elif args.issue_type == 'combination':
        new_item = process_combination_issue(issue_data, film_stocks, developers)
        
        if not new_item:
            print("Error: Could not create combination (missing film or developer)")
            sys.exit(1)
        
        if check_for_duplicates(new_item, combinations, 'combination'):
            print(f"Error: Combination '{new_item['name']}' already exists")
            sys.exit(1)
        
        if args.dry_run:
            print("Combination Data:")
            print(json.dumps(new_item, indent=2))
        else:
            combinations.append(new_item)
            save_json_file(os.path.join(args.output_dir, 'development_combinations.json'), combinations)
            print(f"Added combination: {new_item['name']}")


if __name__ == "__main__":
    main() 