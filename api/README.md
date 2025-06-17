# Dorkroom Static API Client

A Python client for accessing the Dorkroom Static API data from GitHub with enhanced fuzzy search capabilities.

## Features

- 🔍 **Basic Search**: Simple text-based searching for films and developers
- 🎯 **Fuzzy Search**: Advanced search with improved matching using multiple scoring algorithms
- 📊 **Smart Results**: Search results ranked by relevance with confidence scores
- ⏰ **Improved Time Display**: Working life hours displayed as "x days y hours" format
- 🎨 **Filtered Search**: Search with color type filters (bw, color, slide)
- 📷 **Rich Display**: Detailed information display for films, developers, and combinations

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from api.dorkroom_client import DorkroomAPI

# Initialize the client
api = DorkroomAPI()

# Load all data from GitHub
api.load_all_data()

# Basic search
films = api.search_films("Tri-X")
developers = api.search_developers("HC-110")
```

### Fuzzy Search

The fuzzy search provides more intelligent matching with scoring:

```python
# Fuzzy search for films
results = api.fuzzy_search_films("kodak", limit=5)
api.display_search_results(results)

# Fuzzy search with color type filter
bw_films = api.fuzzy_search_films("tri-x", limit=3, color_type="bw")

# Fuzzy search for developers
dev_results = api.fuzzy_search_developers("d76", limit=5)
```

### Search Results

Fuzzy search returns `SearchResult` objects with:

- `item`: The matched film/developer data
- `score`: Relevance score (0-100+)
- `type`: "film" or "developer"

```python
for result in results:
    print(f"Score: {result.score}%, Type: {result.type}")
    if result.type == "film":
        api.display_film_info(result.item)
```

### Working Life Display

Developer working life is displayed in a more readable format:

- `6 hours` → "6 hours"
- `24 hours` → "1 day"
- `25 hours` → "1 day 1 hour"
- `48 hours` → "2 days"
- `72 hours` → "3 days"

## Fuzzy Search Algorithm

The fuzzy search uses multiple scoring methods:

1. **Token Sort Ratio** (30% weight) - Handles word order differences
2. **Partial Ratio** (25% weight) - Good for substring matches
3. **Ratio** (20% weight) - Overall similarity
4. **Token Set Ratio** (15% weight) - Handles extra words
5. **Secondary Partial** (10% weight) - Matches in descriptions/attributes

### Scoring Bonuses

- **Exact word matches**: +10 points per match
- **Prefix matches**: +10-15 points for words starting with query
- **Minimum threshold**: 40 points required for inclusion

### Search Indicators

- 🔥 Score > 80% (Excellent match)
- ✨ Score > 60% (Good match)
- 💫 Score ≤ 60% (Fair match)

## Examples

See the `example/` directory for complete examples:

- `test_fuzzy_search.py` - Demonstrates fuzzy search features
- `test_dorkroom_api.py` - Full API testing with interactive mode

## Requirements

- `requests>=2.25.0`
- `fuzzywuzzy>=0.18.0`
- `python-Levenshtein>=0.12.0`

## Repository

Data comes from: https://github.com/narrowstacks/dorkroom-static-api
