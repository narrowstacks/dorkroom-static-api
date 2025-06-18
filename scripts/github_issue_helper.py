#!/usr/bin/env python3
"""
GitHub Issue Helper for Dorkroom Static API
Creates GitHub issues based on the YAML templates for film stocks, developers, and development combinations.
"""

import json
import os
import webbrowser
import urllib.parse
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

@dataclass
class GitHubIssueData:
    """Container for GitHub issue data"""
    title: str
    body: str
    labels: List[str]

class GitHubIssueHelper:
    """Helper class for creating GitHub issues from collected data"""
    
    REPO_URL = "https://github.com/narrowstacks/dorkroom-static-api"
    
    def __init__(self):
        self.repo_url = self.REPO_URL
    
    def create_film_stock_issue(self, film_data: Dict[str, Any], sources: str = "") -> GitHubIssueData:
        """Create GitHub issue data for a film stock"""
        
        # Create title
        brand = film_data.get('brand', '')
        name = film_data.get('name', '')
        title = f"[FILM] Add: {brand} {name}".strip()
        
        # Map colorType to GitHub form values
        color_type_map = {
            'bw': 'Black & White (bw)',
            'color': 'Color Negative (color)',
            'slide': 'Color Slide/Transparency (slide)'
        }
        colorType = color_type_map.get(film_data.get('colorType', ''), film_data.get('colorType', ''))
        
        # Map discontinued status
        discontinued = "Discontinued" if film_data.get('discontinued') else "Currently in production"
        
        # Format manufacturer notes
        manufacturerNotes = film_data.get('manufacturerNotes', [])
        if isinstance(manufacturerNotes, list):
            notes_text = '\n'.join(manufacturerNotes) if manufacturerNotes else ""
        else:
            notes_text = str(manufacturerNotes) if manufacturerNotes else ""
        
        # Create body using GitHub issue form format
        body_parts = [
            "### Brand/Manufacturer",
            "",
            brand,
            "",
            "### Film Name", 
            "",
            name,
            "",
            "### ISO Speed",
            "",
            str(film_data.get('isoSpeed', '')),
            "",
            "### Film Type",
            "",
            colorType,
            "",
            "### Grain Structure",
            "",
            film_data.get('grainStructure', '') or "",
            "",
            "### Reciprocity Failure Characteristics",
            "",
            film_data.get('reciprocityFailure', '') or "",
            "",
            "### Current Production Status",
            "",
            discontinued,
            "",
            "### Description",
            "",
            film_data.get('description', '') or "",
            "",
            "### Manufacturer Notes",
            "",
            notes_text,
            "",
            "### Static Image URL",
            "",
            film_data.get('staticImageURL', '') or "",
            "",
            "### Sources",
            "",
            sources,
            "",
            "### Submission Guidelines",
            "",
            "- [x] I have verified this film is not already in the database",
            "- [x] I have reliable sources for this information", 
            "- [x] I understand this data will be publicly available under the project's license"
        ]
        
        return GitHubIssueData(
            title=title,
            body='\n'.join(body_parts),
            labels=['data-submission', 'film-stock']
        )
    
    def create_developer_issue(self, developer_data: Dict[str, Any], sources: str = "") -> GitHubIssueData:
        """Create GitHub issue data for a developer"""
        
        # Create title
        name = developer_data.get('name', '')
        manufacturer = developer_data.get('manufacturer', '')
        title = f"[DEVELOPER] Add: {manufacturer} {name}".strip()
        
        # Map filmOrPaper values
        filmOrPaper = developer_data.get('filmOrPaper', 'film')
        if filmOrPaper == 'film':
            intended_use = 'film'
        elif filmOrPaper == 'paper':
            intended_use = 'paper'
        else:
            intended_use = 'both'
        
        # Map discontinued status
        discontinued = "Discontinued" if developer_data.get('discontinued') else "Currently in production"
        
        # Format dilutions
        dilutions = developer_data.get('dilutions', [])
        dilution_text = ""
        if dilutions:
            dilution_lines = []
            for dilution in dilutions:
                dilution_lines.append(f"{dilution.get('name', '')}:{dilution.get('dilution', '')}")
            dilution_text = '\n'.join(dilution_lines)
        
        # Format datasheet URLs
        datasheet_urls = developer_data.get('datasheetUrl', [])  # Note: developer script uses 'datasheet_url'
        if isinstance(datasheet_urls, list):
            urls_text = '\n'.join(datasheet_urls) if datasheet_urls else ""
        else:
            urls_text = str(datasheet_urls) if datasheet_urls else ""
        
        # Create body using GitHub issue form format
        body_parts = [
            "### Developer Name",
            "",
            name,
            "",
            "### Manufacturer",
            "",
            manufacturer,
            "",
            "### Developer Type",
            "",
            developer_data.get('type', ''),
            "",
            "### Intended Use",
            "",
            intended_use,
            "",
            "### Working Life (hours)",
            "",
            str(developer_data.get('workingLifeHours', '') or ''),
            "",
            "### Stock Life (months)",
            "",
            str(developer_data.get('stockLifeMonths', '') or ''),
            "",
            "### Current Production Status",
            "",
            discontinued,
            "",
            "### Notes",
            "",
            developer_data.get('notes', '') or "",
            "",
            "### Mixing Instructions",
            "",
            developer_data.get('mixingInstructions', '') or "",
            "",
            "### Safety Notes",
            "",
            developer_data.get('safetyNotes', '') or "",
            "",
            "### Datasheet URLs",
            "",
            urls_text,
            "",
            "### Common Dilutions",
            "",
            dilution_text,
            "",
            "### Sources",
            "",
            sources,
            "",
            "### Submission Guidelines",
            "",
            "- [x] I have verified this developer is not already in the database",
            "- [x] I have reliable sources for this information",
            "- [x] I understand this data will be publicly available under the project's license"
        ]
        
        return GitHubIssueData(
            title=title,
            body='\n'.join(body_parts),
            labels=['data-submission', 'developer']
        )
    
    def create_combination_issue(self, combination_data: Dict[str, Any], 
                                film_stocks: List[Dict[str, Any]], 
                                developers: List[Dict[str, Any]], 
                                sources: str = "") -> GitHubIssueData:
        """Create GitHub issue data for a development combination"""
        
        # Find film and developer details
        filmStockId = combination_data.get('filmStockId')
        developerId = combination_data.get('developerId')
        
        film = next((f for f in film_stocks if f.get('id') == filmStockId), {})
        developer = next((d for d in developers if d.get('id') == developerId), {})
        
        # Create title
        film_name = f"{film.get('brand', '')} {film.get('name', '')}".strip()
        dev_name = f"{developer.get('manufacturer', '')} {developer.get('name', '')}".strip()
        # Get dilution info first
        dilutionId = combination_data.get('dilutionId')
        dilution = next((d for d in developer.get('dilutions', []) if d.get('id') == dilutionId), {})
        dilution_name = dilution.get('name', '') or dilution.get('dilution', '')
        
        title = f"[COMBO] Add: {film_name} in {dev_name} {dilution_name}".strip()
        
        # Create body using GitHub issue form format
        body_parts = [
            "### Combination Name",
            "",
            combination_data.get('name', ''),
            "",
            "### Film Brand",
            "",
            film.get('brand', ''),
            "",
            "### Film Name",
            "",
            film.get('name', ''),
            "",
            "### Developer Manufacturer",
            "",
            developer.get('manufacturer', ''),
            "",
            "### Developer Name",
            "",
            developer.get('name', ''),
            "",
            "### Dilution Name/Ratio",
            "",
            dilution_name,
            "",
            "### Temperature (°F)",
            "",
            str(combination_data.get('temperatureF', '')),
            "",
            "### Time (minutes)",
            "",
            str(combination_data.get('timeMinutes', '')),
            "",
            "### Shooting ISO",
            "",
            str(combination_data.get('shootingIso', '')),
            "",
            "### Push/Pull Stops",
            "",
            str(combination_data.get('pushPull', 0)),
            "",
            "### Agitation Schedule",
            "",
            combination_data.get('agitationSchedule', '') or "",
            "",
            "### Notes",
            "",
            combination_data.get('notes', '') or "",
            "",
            "### Sources",
            "",
            sources,
            "",
            "### Submission Guidelines",
            "",
            "- [x] I have verified this combination is not already in the database",
            "- [x] I have confirmed both the film and developer exist in our database (or submitted them separately)",
            "- [x] I have reliable sources for this development data",
            "- [x] I understand this data will be publicly available under the project's license"
        ]
        
        return GitHubIssueData(
            title=title,
            body='\n'.join(body_parts),
            labels=['data-submission', 'development-combination']
        )
    
    def create_issue_url(self, issue_data: GitHubIssueData) -> str:
        """Create a GitHub issue URL with pre-filled data"""
        base_url = f"{self.repo_url}/issues/new"
        
        params = {
            'title': issue_data.title,
            'body': issue_data.body,
            'labels': ','.join(issue_data.labels)
        }
        
        # URL encode the parameters
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"
    
    def open_issue_in_browser(self, issue_data: GitHubIssueData) -> None:
        """Open GitHub issue creation page in browser"""
        url = self.create_issue_url(issue_data)
        
        print(f"\n🌐 Opening GitHub issue in browser...")
        print(f"📋 Title: {issue_data.title}")
        print(f"🏷️  Labels: {', '.join(issue_data.labels)}")
        
        try:
            webbrowser.open(url)
            print("✅ Browser opened successfully!")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            print(f"\n📋 Manual URL:\n{url}")
    
    def print_issue_details(self, issue_data: GitHubIssueData) -> None:
        """Print issue details to console"""
        print("\n" + "="*60)
        print("📋 GITHUB ISSUE DETAILS")
        print("="*60)
        print(f"Title: {issue_data.title}")
        print(f"Labels: {', '.join(issue_data.labels)}")
        print("\nBody:")
        print("-" * 40)
        print(issue_data.body)
        print("-" * 40)

def get_action_choice() -> str:
    """Get user's choice for what to do with the data"""
    print("\n🎯 What would you like to do with this data?")
    print("1. Save to local repository only")
    print("2. Create GitHub issue only")
    print("3. Save locally AND create GitHub issue")
    print("4. Cancel (don't save anywhere)")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("Invalid choice. Please enter 1, 2, 3, or 4.")

def get_sources_input() -> str:
    """Get sources information from user"""
    print("\n📚 Please provide sources for this information:")
    print("(This helps maintainers verify the data)")
    
    sources_lines = []
    print("Enter sources (one per line, press Enter twice to finish):")
    
    while True:
        line = input().strip()
        if not line:
            if sources_lines:  # If we have at least one line, break
                break
            else:
                print("Please provide at least one source:")
                continue
        sources_lines.append(line)
    
    return '\n'.join(sources_lines)

# Example usage functions for each script type
def handle_film_stock_submission(film_data: Dict[str, Any], save_function=None) -> None:
    """Handle film stock data submission with user choice"""
    helper = GitHubIssueHelper()
    
    choice = get_action_choice()
    
    if choice == '4':  # Cancel
        print("\n❌ Cancelled. No data saved.")
        return
    
    # Get sources if creating GitHub issue
    sources = ""
    if choice in ['2', '3']:
        sources = get_sources_input()
    
    # Save locally if requested
    if choice in ['1', '3'] and save_function:
        try:
            save_function()
            print("\n✅ Data saved to local repository!")
        except Exception as e:
            print(f"\n❌ Failed to save locally: {e}")
            return
    
    # Create GitHub issue if requested
    if choice in ['2', '3']:
        issue_data = helper.create_film_stock_issue(film_data, sources)
        helper.print_issue_details(issue_data)
        
        create_issue = input("\n❓ Open GitHub issue creation page in browser? (y/n): ").strip().lower()
        if create_issue in ['y', 'yes']:
            helper.open_issue_in_browser(issue_data)
        else:
            print(f"\n📋 You can manually create the issue at: {helper.repo_url}/issues/new")

def handle_developer_submission(developer_data: Dict[str, Any], save_function=None) -> None:
    """Handle developer data submission with user choice"""
    helper = GitHubIssueHelper()
    
    choice = get_action_choice()
    
    if choice == '4':  # Cancel
        print("\n❌ Cancelled. No data saved.")
        return
    
    # Get sources if creating GitHub issue
    sources = ""
    if choice in ['2', '3']:
        sources = get_sources_input()
    
    # Save locally if requested
    if choice in ['1', '3'] and save_function:
        try:
            save_function()
            print("\n✅ Data saved to local repository!")
        except Exception as e:
            print(f"\n❌ Failed to save locally: {e}")
            return
    
    # Create GitHub issue if requested
    if choice in ['2', '3']:
        issue_data = helper.create_developer_issue(developer_data, sources)
        helper.print_issue_details(issue_data)
        
        create_issue = input("\n❓ Open GitHub issue creation page in browser? (y/n): ").strip().lower()
        if create_issue in ['y', 'yes']:
            helper.open_issue_in_browser(issue_data)
        else:
            print(f"\n📋 You can manually create the issue at: {helper.repo_url}/issues/new")

def handle_combination_submission(combination_data: Dict[str, Any], 
                                 film_stocks: List[Dict[str, Any]], 
                                 developers: List[Dict[str, Any]], 
                                 save_function=None) -> None:
    """Handle development combination data submission with user choice"""
    helper = GitHubIssueHelper()
    
    choice = get_action_choice()
    
    if choice == '4':  # Cancel
        print("\n❌ Cancelled. No data saved.")
        return
    
    # Get sources if creating GitHub issue
    sources = ""
    if choice in ['2', '3']:
        sources = get_sources_input()
    
    # Save locally if requested
    if choice in ['1', '3'] and save_function:
        try:
            save_function()
            print("\n✅ Data saved to local repository!")
        except Exception as e:
            print(f"\n❌ Failed to save locally: {e}")
            return
    
    # Create GitHub issue if requested
    if choice in ['2', '3']:
        issue_data = helper.create_combination_issue(combination_data, film_stocks, developers, sources)
        helper.print_issue_details(issue_data)
        
        create_issue = input("\n❓ Open GitHub issue creation page in browser? (y/n): ").strip().lower()
        if create_issue in ['y', 'yes']:
            helper.open_issue_in_browser(issue_data)
        else:
            print(f"\n📋 You can manually create the issue at: {helper.repo_url}/issues/new")

if __name__ == "__main__":
    print("GitHub Issue Helper for Dorkroom Static API")
    print("This module is meant to be imported by other scripts.")
    print("Use it in your data addition scripts to create GitHub issues.") 