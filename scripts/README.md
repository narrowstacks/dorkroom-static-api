# Dorkroom Static API - Data Addition Scripts

This directory contains interactive Python scripts for adding data to the Dorkroom Static API database. Each script provides a user-friendly interface for collecting and validating data, with the option to save locally and/or create GitHub issues for community review.

## Available Scripts

### 1. `add_film_stock.py`

Add new film stocks to the database with guided input for:

- Brand/manufacturer and film name
- ISO speed and color type (B&W, color, slide)
- Grain structure and reciprocity characteristics
- Production status and descriptions
- Manufacturer notes

### 2. `add_developer.py`

Add new developers with comprehensive data collection:

- Developer name and manufacturer
- Type (concentrate, powder) and intended use (film/paper)
- Working and stock solution lifespans
- Dilution ratios and custom dilutions
- Safety notes and datasheet URLs

### 3. `add_development_combination.py`

Add development combinations with smart search capabilities:

- Fuzzy search for films and developers
- Automatic push/pull calculation
- Temperature, time, and agitation specifications
- Custom dilution support

## New GitHub Integration Features

All scripts now support **flexible data submission options**:

### Submission Options

When you complete data entry, you'll be prompted to choose:

1. **Save to local repository only** - Adds data directly to your local JSON files
2. **Create GitHub issue only** - Opens a pre-filled GitHub issue for community review
3. **Save locally AND create GitHub issue** - Does both (recommended for contributors)
4. **Cancel** - Discard the data without saving

### GitHub Issue Templates

The scripts automatically format your data according to the official GitHub issue templates:

- **Film Stock**: Uses `add-film-stock.yml` template
- **Developer**: Uses `add-developer.yml` template
- **Development Combination**: Uses `add-combination.yml` template

### How It Works

1. **Complete data entry** using the interactive script interface
2. **Review your data** in the final preview screen
3. **Choose submission method** from the 4 options above
4. **Provide sources** (required for GitHub issues to help maintainers verify data)
5. **Browser opens automatically** with pre-filled GitHub issue (if selected)

### Benefits of GitHub Issues

- **Community review** - Other photographers can validate your data
- **Source verification** - Maintainers can verify accuracy before merging
- **Discussion** - Ask questions or provide additional context
- **Attribution** - Your contributions are tracked and credited
- **Quality control** - Prevents duplicate or incorrect data

## Usage Examples

### Basic Usage

```bash
# Add a new film stock
python add_film_stock.py

# Add a new developer
python add_developer.py

# Add a development combination
python add_development_combination.py
```

### Enhanced Features (Development Combination)

The combination script includes advanced features:

- **Fuzzy search**: Type partial names to find films/developers quickly
- **Automatic filtering**: Color/slide films are filtered out (they use standardized C-41/E-6 processes)
- **Push/pull calculation**: Automatically calculates stops based on shooting vs. film ISO
- **Smart defaults**: Temperature defaults to 68°F, common agitation patterns suggested

## Installation

### Basic Installation (All Scripts)

No additional dependencies required for basic functionality:

```bash
python add_film_stock.py
python add_developer.py
```

### Enhanced Installation (Development Combination)

For fuzzy search and color output, install optional dependencies:

```bash
pip install rapidfuzz colorama
```

## Data Quality Guidelines

### Sources Required for GitHub Issues

Always provide reliable sources such as:

- Official manufacturer datasheets
- Reputable photography publications
- Personal testing results (clearly marked)
- Community databases (non-Massive Dev Chart)

### Accuracy Standards

- Use consistent naming conventions
- Include manufacturer specifications when available
- Mark discontinued products appropriately
- Cite sources for all technical data

## Architecture

### GitHub Issue Helper (`github_issue_helper.py`)

Shared module that handles:

- **Data formatting** according to GitHub issue templates
- **URL generation** with pre-filled form data
- **Browser integration** for seamless issue creation
- **User interaction** for submission choices and source collection

### Integration Pattern

Each script imports and uses the helper:

```python
from github_issue_helper import handle_film_stock_submission

# After data collection and validation
handle_film_stock_submission(film_data, local_save_function)
```

## Contributing

### Local Development

1. **Test your data** locally first using option 1 (save locally only)
2. **Verify JSON validity** by loading files in your application
3. **Create GitHub issue** using option 2 or 3 for community review

### Best Practices

- **Start small** - Test with one entry before bulk additions
- **Double-check data** - Review the final preview carefully
- **Cite sources** - Always provide verification sources for GitHub issues
- **Follow templates** - The scripts ensure proper formatting automatically

## Repository Integration

These scripts work with the [Dorkroom Static API](https://github.com/narrowstacks/dorkroom-static-api) repository structure:

- **Local files**: `film_stocks.json`, `developers.json`, `development_combinations.json`
- **GitHub issues**: Automatically formatted using `.github/ISSUE_TEMPLATE/` forms
- **Community workflow**: Issues → Review → Automated processing → Pull requests

The GitHub integration makes it easy for both technical and non-technical users to contribute high-quality data to the community database.
