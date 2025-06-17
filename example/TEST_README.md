# Dorkroom Static API Test Script

The test script `test_dorkroom_api.py` demonstrates how to pull and work with data from the [Dorkroom Static API](https://github.com/narrowstacks/dorkroom-static-api) repository.

## Overview

The script fetches JSON data directly from the GitHub repository and provides a Python interface for:

- 📷 Film stocks (150 films from 32+ brands)
- 🧪 Developers (9 different developers with various dilutions)
- ⚗️ Development combinations (film + developer recipes)
- 📐 Film formats (35mm, 120, etc.)

## Installation

1. Install the required dependency:

```bash
pip install requests
```

Or use the requirements file:

```bash
pip install -r test_requirements.txt
```

## Usage

### Basic Usage

Run the script to see a comprehensive demonstration:

```bash
python test_dorkroom_api.py
```

This will:

- Fetch all data from the GitHub repository
- Display sample queries and results
- Show database statistics
- Enter interactive mode for further exploration

### Interactive Mode

After running the script, you can use the `api_client` object to explore the data:

```python
# Search for specific films
kodak_films = api_client.search_films('Kodak')
bw_films = api_client.search_films('HP', color_type='bw')

# Search for developers
d76_developers = api_client.search_developers('D-76')

# Get film by ID
film = api_client.get_film_by_id('097cf2f5-c5f6-45c0-bfb7-28055b829c66')

# Find development combinations for a film
combinations = api_client.get_combinations_for_film(film['id'])

# Display detailed information
api_client.display_film_info(film)
```

## Features

### DorkroomAPI Class

The main class provides the following methods:

#### Data Loading

- `load_all_data()` - Fetch all JSON files from GitHub
- `fetch_json_data(filename)` - Fetch individual JSON file

#### Search Functions

- `search_films(query, color_type=None)` - Search films by name/brand
- `search_developers(query)` - Search developers by name/manufacturer
- `get_film_by_id(film_id)` - Get specific film by UUID
- `get_developer_by_id(developer_id)` - Get specific developer by UUID

#### Relationship Functions

- `get_combinations_for_film(film_id)` - Get development recipes for a film
- `get_combinations_for_developer(developer_id)` - Get recipes using a developer

#### Display Functions

- `display_film_info(film)` - Pretty print film details
- `display_developer_info(developer)` - Pretty print developer details
- `display_combination_info(combo)` - Pretty print development recipe

## Sample Output

```
📷 Kodak Tri-X 400
   ID: 097cf2f5-c5f6-45c0-bfb7-28055b829c66
   ISO Speed: 400.0
   Color Type: BW
   Discontinued: No
   Description: Kodak's Professional Tri-X 400 Black and White...
   Key Features: panchromatic b&w negative film, fine grain and high sharpness...

🧪 Kodak HC-110
   ID: 83a344e1-239f-4899-b747-06390f42b7d1
   Type: Concentrate
   For: Film
   Working Life: 2190 hours (91.2 days)
   Available Dilutions: 7
     • Dilution A: 1:15
     • Dilution B: 1:31
```

## Data Structure

The API provides access to four main data types:

### Film Stocks

- Brand, name, ISO speed
- Color type (b&w, color, slide)
- Grain structure, reciprocity failure
- Manufacturer notes and descriptions

### Developers

- Name, manufacturer, type
- Working and stock solution lifespans
- Multiple dilution ratios
- Safety notes and datasheets

### Development Combinations

- Film + developer pairing
- Temperature, time, agitation
- Push/pull processing information
- Custom dilutions and notes

### Formats

- Film format specifications
- Size and description information

## Error Handling

The script includes robust error handling for:

- Network connectivity issues
- JSON parsing errors
- Missing data references
- Invalid UUIDs

## Repository Information

- **Source**: [narrowstacks/dorkroom-static-api](https://github.com/narrowstacks/dorkroom-static-api)
- **Data Files**: Fetched directly from GitHub's raw content URLs
- **Update Frequency**: Data is fetched fresh each time the script runs
- **License**: Check the source repository for licensing information

## Contributing

To contribute to the underlying data, visit the [source repository](https://github.com/narrowstacks/dorkroom-static-api) which provides:

- GitHub issue forms for easy data submission
- Python scripts for advanced contributions
- Automated workflows for data validation
- Community review processes
