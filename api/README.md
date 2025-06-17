# Dorkroom Python Client

A robust, typed, and configurable Python client for the [Dorkroom Static API](https://github.com/narrowstacks/dorkroom-static-api). This client provides easy access to film stocks, developers, and development combinations with advanced features like fuzzy search, caching, and comprehensive error handling.

## Features

- 🚀 **Fast & Reliable**: Built-in retries, timeouts, and O(1) lookups via indexed data structures
- 🔍 **Advanced Search**: Both exact substring and fuzzy search capabilities
- 📊 **Rich Data Models**: Typed dataclasses for Film, Developer, and Combination objects
- 🛡️ **Error Handling**: Comprehensive exception hierarchy for robust error management
- 🧪 **Testing Friendly**: Dependency injection support for HTTP transport

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

The client requires:

- `requests` - HTTP client with retry support
- `rapidfuzz` (optional) - For fuzzy search functionality

## Quick Start

```python
from dorkroom_client import DorkroomClient

# Initialize the client
client = DorkroomClient()

# Load all data (required before using the client)
client.load_all()

# Search for films
films = client.search_films("tri-x")
print(f"Found {len(films)} films matching 'tri-x'")

# Get a specific film by ID
film = client.get_film("kodak-tri-x-400")
if film:
    print(f"{film.brand} {film.name} - ISO {film.iso_speed}")

# Find development combinations for a film
combinations = client.list_combinations_for_film("kodak-tri-x-400")
print(f"Found {len(combinations)} development combinations")
```

## Usage Examples

### Basic Film Search

```python
from dorkroom_client import DorkroomClient, CLIFormatter

client = DorkroomClient()
client.load_all()

# Search by name or brand
films = client.search_films("kodak", color_type="B&W")

# Display results
for film in films:
    lines = CLIFormatter.format_film(film)
    CLIFormatter.print_lines(lines)
    print()  # Add spacing
```

### Fuzzy Search

```python
# Fuzzy search is more forgiving of typos and word order
fuzzy_films = client.fuzzy_search_films("tri x", limit=5)

# Search developers
fuzzy_devs = client.fuzzy_search_devs("d76", limit=3)

for dev in fuzzy_devs:
    lines = CLIFormatter.format_dev(dev)
    CLIFormatter.print_lines(lines)
    print()
```

### Working with Development Combinations

```python
# Get all combinations for a specific film
film_combos = client.list_combinations_for_film("kodak-tri-x-400")

# Get all combinations for a specific developer
dev_combos = client.list_combinations_for_developer("kodak-d-76")

# Display combination details
for combo in film_combos[:3]:  # Show first 3
    film = client.get_film(combo.film_stock_id)
    developer = client.get_developer(combo.developer_id)

    print(f"📷 {film.brand} {film.name}")
    print(f"🧪 {developer.manufacturer} {developer.name}")
    print(f"⏱️  {combo.time_minutes} min @ {combo.temperature_f}°F")
    print(f"📊 ISO {combo.shooting_iso}")
    if combo.push_pull != 0:
        print(f"🔄 Push/Pull: {combo.push_pull:+d} stops")
    print()
```

### Error Handling

```python
from dorkroom_client import DorkroomClient, DataNotLoadedError, DataFetchError

client = DorkroomClient()

try:
    # This will raise DataNotLoadedError
    films = client.search_films("tri-x")
except DataNotLoadedError as e:
    print(f"Error: {e}")
    client.load_all()  # Load data first
    films = client.search_films("tri-x")

try:
    client.load_all()
except DataFetchError as e:
    print(f"Failed to load data: {e}")
```

### Custom Configuration

```python
import logging

# Custom logger
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)

# Custom configuration
client = DorkroomClient(
    base_url="https://my-custom-api.com/",
    timeout=30.0,
    max_retries=5,
    logger=logger
)

client.load_all()
```

### Using with Testing

```python
from unittest.mock import Mock
import requests

# Create a mock transport for testing
mock_transport = Mock()
mock_response = Mock()
mock_response.json.return_value = [{"id": "test", "name": "Test Film", ...}]
mock_transport.get.return_value = mock_response

# Inject the mock transport
client = DorkroomClient(transport=mock_transport)
client.load_all()

# Now the client uses your mock instead of real HTTP requests
```

## API Reference

### DorkroomClient

The main client class for interacting with the Dorkroom Static API.

#### Constructor

```python
DorkroomClient(
    base_url: str = "https://raw.githubusercontent.com/narrowstacks/dorkroom-static-api/main/",
    timeout: float = 10.0,
    max_retries: int = 3,
    transport: HTTPTransport = None,
    logger: Optional[logging.Logger] = None
)
```

**Parameters:**

- `base_url`: Base URL for the API endpoints
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum number of retry attempts for failed requests
- `transport`: Custom HTTP transport (useful for testing)
- `logger`: Custom logger instance

#### Methods

##### `load_all() -> None`

Fetch and parse all JSON data, building internal indexes. **Must be called before using any other client methods.**

**Raises:**

- `DataFetchError`: If any HTTP request fails
- `DataParseError`: If any JSON parsing fails

##### `get_film(film_id: str) -> Optional[Film]`

Get a film by its unique ID.

**Parameters:**

- `film_id`: The unique ID of the film

**Returns:** Film object if found, None otherwise

**Raises:** `DataNotLoadedError` if `load_all()` hasn't been called

##### `get_developer(dev_id: str) -> Optional[Developer]`

Get a developer by its unique ID.

**Parameters:**

- `dev_id`: The unique ID of the developer

**Returns:** Developer object if found, None otherwise

**Raises:** `DataNotLoadedError` if `load_all()` hasn't been called

##### `search_films(query: str, color_type: Optional[str] = None) -> List[Film]`

Search films by name or brand using substring matching.

**Parameters:**

- `query`: Search term to match against film name and brand
- `color_type`: Optional filter by color type (e.g., "Color", "B&W")

**Returns:** List of matching films

##### `fuzzy_search_films(query: str, limit: int = 10) -> List[Film]`

Fuzzy search for films by name, brand, and description.

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of results to return

**Returns:** List of matching films, sorted by relevance

##### `fuzzy_search_devs(query: str, limit: int = 10) -> List[Developer]`

Fuzzy search for developers by manufacturer, name, and notes.

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of results to return

**Returns:** List of matching developers, sorted by relevance

##### `list_combinations_for_film(film_id: str) -> List[Combination]`

Get all development combinations for a specific film.

**Parameters:**

- `film_id`: The unique ID of the film

**Returns:** List of combinations using this film

##### `list_combinations_for_developer(dev_id: str) -> List[Combination]`

Get all development combinations for a specific developer.

**Parameters:**

- `dev_id`: The unique ID of the developer

**Returns:** List of combinations using this developer

### Data Models

#### Film

Represents a film stock with all its properties.

**Attributes:**

- `id`: Unique identifier for the film
- `name`: Display name of the film
- `brand`: Manufacturer/brand name
- `iso_speed`: ISO speed rating
- `color_type`: Type of film (Color, B&W, etc.)
- `description`: Optional detailed description
- `discontinued`: Whether film is discontinued (0=no, 1=yes)
- `manufacturer_notes`: List of notes from manufacturer
- `grain_structure`: Description of grain characteristics
- `reciprocity_failure`: Information about reciprocity failure

#### Developer

Represents a film/paper developer with all its properties.

**Attributes:**

- `id`: Unique identifier for the developer
- `name`: Display name of the developer
- `manufacturer`: Manufacturer/brand name
- `type`: Type of developer (e.g., "Black & White Film")
- `film_or_paper`: Whether for film or paper development
- `dilutions`: List of available dilution ratios
- `working_life_hours`: Working solution lifetime in hours
- `stock_life_months`: Stock solution lifetime in months
- `notes`: Additional notes about the developer
- `discontinued`: Whether developer is discontinued (0=no, 1=yes)
- `mixing_instructions`: How to prepare the developer
- `safety_notes`: Safety information and warnings
- `datasheet_url`: URLs to manufacturer datasheets

#### Combination

Represents a film+developer combination with development parameters.

**Attributes:**

- `id`: Unique identifier for the combination
- `name`: Display name describing the combination
- `film_stock_id`: ID of the film used
- `developer_id`: ID of the developer used
- `temperature_f`: Development temperature in Fahrenheit
- `time_minutes`: Development time in minutes
- `shooting_iso`: ISO at which the film was shot
- `push_pull`: Push/pull processing offset (0=normal, +1=push 1 stop, etc.)
- `agitation_schedule`: Description of agitation pattern
- `notes`: Additional development notes
- `dilution_id`: ID of specific dilution used
- `custom_dilution`: Custom dilution ratio if not standard

### CLIFormatter

Utility class for formatting data objects for CLI display.

#### Methods

##### `format_film(f: Film) -> List[str]`

Format a Film object for CLI display.

**Parameters:**

- `f`: Film object to format

**Returns:** List of formatted lines for display

##### `format_dev(d: Developer) -> List[str]`

Format a Developer object for CLI display.

**Parameters:**

- `d`: Developer object to format

**Returns:** List of formatted lines for display

##### `print_lines(lines: List[str]) -> None`

Print a list of lines to stdout.

**Parameters:**

- `lines`: List of strings to print

### Exceptions

#### `DorkroomAPIError`

Base exception for all Dorkroom API errors.

#### `DataFetchError`

Raised when HTTP requests fail. Inherits from `DorkroomAPIError`.

#### `DataParseError`

Raised when JSON parsing fails. Inherits from `DorkroomAPIError`.

#### `DataNotLoadedError`

Raised when data operations are attempted before calling `load_all()`. Inherits from `DorkroomAPIError`.

## Advanced Usage

### Custom HTTP Transport

For testing or custom HTTP handling:

```python
from dorkroom_client import HTTPTransport
import requests

class CustomTransport:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.session = requests.Session()

    def get(self, url: str, timeout: float) -> requests.Response:
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        return self.session.get(url, timeout=timeout, headers=headers)

# Use custom transport
transport = CustomTransport("your-auth-token")
client = DorkroomClient(transport=transport)
```

### Generic Fuzzy Search

The client includes a generic fuzzy search method for advanced use cases:

```python
# Search films by multiple criteria
results = client.fuzzy_search(
    items=client._films,  # Access internal films list
    key_funcs=[
        lambda f: f.name,
        lambda f: f.brand,
        lambda f: f.description or "",
        lambda f: " ".join(f.manufacturer_notes)
    ],
    query="professional portrait film",
    limit=5,
    threshold=70.0
)
```

## Performance Notes

- The client builds indexes on `load_all()` for O(1) lookups by ID
- `get_film()` and `get_developer()` methods are cached with `@lru_cache`
- Fuzzy search has a configurable threshold to balance accuracy vs. performance
- All data is loaded into memory for fast access (typical dataset is < 10MB)

## Contributing

This client is part of the [Dorkroom Static API](https://github.com/narrowstacks/dorkroom-static-api) project. Please see the main repository for contribution guidelines.

## License

See the main [Dorkroom Static API repository](https://github.com/narrowstacks/dorkroom-static-api) for license information.
