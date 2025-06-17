# Dorkroom Static API

A comprehensive static API for analog film photography data, including film stocks, developers, development combinations, and formats.

## Data Structure

This repository contains four main JSON files that provide structured data for analog photography applications:

> **Important:** The database uses UUID-based identifiers. All references between files (e.g., film_stock_id, developer_id) use UUIDs.

### `film_stocks.json`

Contains detailed information about film stocks from various manufacturers.

**Structure:**

```json
{
  "id": "3141645e-5007-4be6-9327-c9fb5e4ad6f6",
  "brand": "Ilford",
  "name": "HP5 Plus",
  "iso_speed": 400.0,
  "color_type": "bw",
  "grain_structure": null,
  "reciprocity_failure": 1.31,
  "discontinued": 0,
  "description": "Ilford's HP5 Plus Black and White Negative Film is a traditional and versatile panchromatic film designed for general use in a wide variety of shooting conditions. Exhibiting notably wide exposure latitude, this film responds well to use in mixed and difficult lighting and provides medium contrast for greater overall control. It has a nominal sensitivity of ISO 400/27° when developed in standard black and white chemistry, and responds well to push processing. HP5 Plus is a flexible film type that is ideally suited for use in general photographic applications in an array of different lighting conditions.",
  "manufacturer_notes": [
    "panchromatic b&w negative film",
    "responds well to push processing",
    "iso 400/27° in standard process",
    "wide exposure latitude",
    "medium contrast",
    "ideal for mixed lighting and general use"
  ]
}
```

**Fields:**

- `id`: Unique UUID identifier for the film stock
- `brand`: Manufacturer/brand name
- `name`: Film stock name
- `iso_speed`: Film's ISO/ASA rating
- `color_type`: Film type (`"bw"`, `"color"`, `"slide"`)
- `grain_structure`: Grain characteristics (optional)
- `reciprocity_failure`: Reciprocity failure information (optional)
- `discontinued`: Boolean flag (0 = active, 1 = discontinued)
- `description`: Detailed description of the film
- `manufacturer_notes`: Array of key characteristics from manufacturer

### `developers.json`

Contains information about film and paper developers, including dilution options.

**Structure:**

```json
{
  "id": "83a344e1-239f-4899-b747-06390f42b7d1",
  "name": "HC-110",
  "manufacturer": "Kodak",
  "type": "concentrate",
  "film_or_paper": "film",
  "working_life_hours": 2190,
  "stock_life_months": 6,
  "discontinued": 0,
  "notes": "Common dilutions: Dilution A (1:15), Dilution B (1:31), Dilution C (1:19), Dilution D (1:39), Dilution E (1:47), Dilution F (1:79), Dilution H (1:63)",
  "mixing_instructions": null,
  "safety_notes": null,
  "datasheet_url": [
    "https://business.kodakmoments.com/sites/default/files/wysiwyg/pro/chemistry/j24.pdf"
  ],
  "dilutions": [
    {
      "id": 1,
      "name": "Dilution A",
      "dilution": "1:15"
    },
    {
      "id": 2,
      "name": "Dilution B",
      "dilution": "1:31"
    }
  ]
}
```

**Fields:**

- `id`: Unique UUID identifier for the developer
- `name`: Developer name
- `manufacturer`: Manufacturer name
- `type`: Developer type (e.g., "concentrate", "powder")
- `film_or_paper`: Intended use (`"film"`, `"paper"`)
- `working_life_hours`: Working solution lifespan in hours (optional)
- `stock_life_months`: Stock solution lifespan in months (optional)
- `discontinued`: Boolean flag (0 = active, 1 = discontinued)
- `notes`: General notes about the developer
- `mixing_instructions`: How to mix the developer (optional)
- `safety_notes`: Safety information (optional)
- `datasheet_url`: Array of URLs to manufacturer datasheets (optional)
- `dilutions`: Array of available dilutions with their ratios

### `development_combinations.json`

Contains specific film and developer combinations with development times and procedures.

**Structure:**

```json
{
  "id": "56776f0e-563e-4428-94a5-2110c9579612",
  "name": "Tri-X 400 @ 400 in HC-110 1:31",
  "film_stock_id": "097cf2f5-c5f6-45c0-bfb7-28055b829c66",
  "temperature_f": 68,
  "time_minutes": 11.0,
  "agitation_schedule": "30s initial, then 10s every 60s",
  "push_pull": 0,
  "notes": "Dilution B, agitate 30s every 60s",
  "developer_id": "83a344e1-239f-4899-b747-06390f42b7d1",
  "dilution_id": 2,
  "custom_dilution": null,
  "shooting_iso": 400.0
}
```

**Fields:**

- `id`: Unique UUID identifier for the combination
- `name`: Descriptive name of the combination
- `film_stock_id`: UUID reference to film stock in `film_stocks.json`
- `developer_id`: UUID reference to developer in `developers.json`
- `dilution_id`: Reference to specific dilution in developer's dilutions array
- `custom_dilution`: Custom dilution ratio if not using predefined dilution (optional)
- `temperature_f`: Development temperature in Fahrenheit
- `time_minutes`: Development time in minutes
- `agitation_schedule`: Agitation pattern description
- `push_pull`: Push/pull stops (0 = normal, positive = push, negative = pull)
- `shooting_iso`: ISO rating the film was shot at
- `notes`: Additional development notes

### `formats.json`

Contains information about film formats.

**Structure:**

```json
{
  "id": 1,
  "name": "35mm",
  "description": "Standard 35mm roll film"
}
```

**Fields:**

- `id`: Unique identifier for the format
- `name`: Format name (e.g., "35mm", "120", "4x5")
- `description`: Format description

## Python Tools

This repository includes several Python tools to help users interact with the database and contribute new data.

### Data Addition Scripts

These command-line tools make it easy for users to submit new data to the database:

#### `add_film_stock.py`

Interactive script for adding new film stocks to the database.

**Features:**

- User-friendly guided input with progress tracking
- Data validation and back navigation
- Automatic UUID generation
- Comprehensive field collection including manufacturer notes

**Usage:**

```bash
python add_film_stock.py
```

The script will guide you through entering:

- Brand/manufacturer name
- Film name and ISO speed
- Color type (b&w, color, slide)
- Grain structure and reciprocity characteristics
- Discontinuation status
- Description and manufacturer notes

#### `add_developer.py`

Interactive script for adding new developers to the database.

**Features:**

- Guided input with validation
- Support for multiple dilutions
- Option to copy dilutions from existing developers
- Developer type selection (concentrate, powder)
- Datasheet URL collection

**Usage:**

```bash
python add_developer.py
```

The script collects:

- Developer name and manufacturer
- Type and intended use (film/paper)
- Working and stock solution lifespans
- Notes and safety information
- Multiple dilution ratios
- Manufacturer datasheet URLs

#### `add_development_combination.py`

Advanced script for adding development combinations with fuzzy search capabilities.

**Features:**

- Smart fuzzy search for films and developers
- Automatic push/pull calculation based on shooting ISO
- Support for custom dilutions
- Temperature and time specification
- Agitation schedule input

**Dependencies:**

```bash
pip install fuzzywuzzy python-Levenshtein colorama
```

**Usage:**

```bash
python add_development_combination.py
```

The script helps you:

- Search and select film stocks (filters out color/slide films automatically)
- Choose developers and dilutions
- Specify development parameters
- Calculate push/pull processing automatically

### Example Application

#### `example/darkroom_search.py`

A comprehensive command-line search tool demonstrating how to use the database.

**Features:**

- Advanced fuzzy search across all data types
- Interactive menu system
- Custom combination management
- Multiple search algorithms with scoring
- Tabular data display with color coding

**Dependencies:**

```bash
cd example
pip install -r requirements.txt
```

**Usage:**

```bash
cd example
python darkroom_search.py
```

**Capabilities:**

- Search films, developers, and combinations
- Create and save custom development combinations
- Interactive browsing of all database items
- Command-line arguments for direct searches
- Comprehensive help system

**Command-line options:**

```bash
python darkroom_search.py --search "tri-x"      # Direct search
python darkroom_search.py --films               # List all films
python darkroom_search.py --developers          # List all developers
python darkroom_search.py --combinations        # List all combinations
```

### Installation

For the data addition scripts (no additional dependencies required):

```bash
python add_film_stock.py
python add_developer.py
python add_development_combination.py  # Basic functionality
```

Recommended: For enhanced features (fuzzy search, colors), install the required packages:

```bash
pip install -r requirements.txt
```

## Contributing

We welcome contributions to improve and expand this analog photography database! Here's how you can help:

### 🌟 Easy Data Contribution (Recommended)

**Use GitHub Issue Forms!** The easiest way to contribute data is through our automated submission system:

1. **[Submit Film Stock](../../issues/new?template=add-film-stock.yml)** - Add new film stocks
2. **[Submit Developer](../../issues/new?template=add-developer.yml)** - Add new developers and dilutions
3. **[Submit Development Combination](../../issues/new?template=add-combination.yml)** - Add development combinations

**How it works:**

- Fill out the form with your data
- A maintainer reviews and approves the submission
- GitHub automatically creates a pull request with your data
- Once merged, your contribution is live in the database!

**Benefits:**

- ✅ No technical knowledge required
- ✅ Automatic data validation and formatting
- ✅ UUID generation handled for you
- ✅ Duplicate detection
- ✅ Community review and discussion

### 🛠️ Advanced Contribution (Python Scripts)

For users comfortable with command-line tools, our interactive Python scripts provide more control:

- **`add_film_stock.py`** - Add new film stocks with guided input
- **`add_developer.py`** - Add new developers and dilutions
- **`add_development_combination.py`** - Add development combinations with smart search

These scripts handle data validation, UUID generation, and proper formatting automatically. Simply run them and follow the prompts!

### Reporting Issues

If you find errors in the data, missing information, or have suggestions for improvements:

1. **Check existing issues** first to avoid duplicates
2. **Create a new issue** with:
   - Clear, descriptive title
   - Detailed description of the problem or suggestion
   - Specific film stock, developer, or combination affected
   - Sources or references for corrections (if applicable)

**Issue Templates:**

- **Data Error**: Report incorrect information
- **Missing Data**: Request addition of new films, developers, or combinations
- **Enhancement**: Suggest new features or improvements

### Pull Requests

To contribute data or improvements:

1. **Fork** this repository
2. **Create a branch** for your changes:

   ```bash
   git checkout -b add-new-film-stocks
   ```

3. **Make your changes** following the existing data structure
4. **Validate your JSON** to ensure it's properly formatted
5. **Test your changes** by loading the JSON files
6. **Commit** with clear, descriptive messages:

   ```bash
   git commit -m "Add Ilford Delta series film stocks"
   ```

7. **Push** your changes and create a pull request

It is recommended you use the provided add\_\* Python scripts to maintain the data standards of the database.

### Contribution Guidelines

**Data Quality:**

- Ensure accuracy by citing reliable sources
- Use consistent formatting and naming conventions
- Include manufacturer specifications when available
- Mark discontinued products appropriately

**JSON Formatting:**

- Use consistent indentation (2 spaces)
- Maintain alphabetical ordering where logical
- Include all required fields
- Use `null` for optional empty fields

**Pull Request Requirements:**

- Clear description of changes made
- Reference any related issues
- Include sources for new data
- Test that JSON files remain valid

### Data Sources

When adding new data, please use reliable sources such as:

- Official manufacturer specifications, such as datasheets.
- Reputable photography publications
- Film photography community databases
- Personal testing results (clearly marked as such)

**Please do NOT add data directly from the Massive Development Chart, as they specifically do not allow reproducing their data.**

If your development time is identical or similar to one on their list, that's okay! Development data isn't inherently theirs. Just don't copy their data/notes/etc verbatim.

### 🔧 For Maintainers: Automated Workflow

The repository includes an automated system for processing data submissions:

1. **Issue Submission**: Users submit data via GitHub issue forms
2. **Review Process**: Maintainers review submissions for accuracy and sources
3. **Approval**: Add the `approved` label to trigger automation
4. **Automatic Processing**: GitHub Actions:
   - Parses issue data
   - Validates format and checks for duplicates
   - Generates UUIDs and proper JSON structure
   - Creates a pull request with the changes
   - Comments on the original issue with status
5. **Final Review**: Review the auto-generated PR and merge when ready

**Key Files:**

- `.github/ISSUE_TEMPLATE/` - Issue form templates
- `.github/workflows/process-data-submission.yml` - Main automation workflow
- `.github/workflows/validate-data.yml` - Data validation on PRs
- `.github/scripts/process_issue.py` - Issue parsing and data generation script

**Safety Features:**

- Duplicate detection prevents overwriting existing data
- Data validation ensures JSON integrity
- Dry-run validation before creating PRs
- All changes go through pull request review
- Automatic linking between issues and PRs

### Issues or Bugs

Feel free to open an issue regarding:

- Bugs in the Python scripts or automation
- Data structure or formatting
- Contribution process
- Missing information
- General project direction

---

**Note:** This is a community-driven project with automated workflows to make contributions easy and safe. All contributions are appreciated and help make analog photography more accessible to everyone!
