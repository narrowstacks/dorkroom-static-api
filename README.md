# Dorkroom Static API

A comprehensive static API for analog film photography data, including film stocks, developers, development combinations, and formats.

## 📁 Data Structure

This repository contains four main JSON files that provide structured data for analog photography applications:

### 🎞️ `film_stocks.json`

Contains detailed information about film stocks from various manufacturers.

**Structure:**

```json
{
  "id": 39,
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

- `id`: Unique identifier for the film stock
- `brand`: Manufacturer/brand name
- `name`: Film stock name
- `iso_speed`: Film's ISO/ASA rating
- `color_type`: Film type (`"bw"`, `"color"`, `"slide"`)
- `grain_structure`: Grain characteristics (optional)
- `reciprocity_failure`: Reciprocity failure information (optional)
- `discontinued`: Boolean flag (0 = active, 1 = discontinued)
- `description`: Detailed description of the film
- `manufacturer_notes`: Array of key characteristics from manufacturer

### 🧪 `developers.json`

Contains information about film and paper developers, including dilution options.

**Structure:**

```json
{
  "id": 1,
  "name": "HC-110",
  "manufacturer": "Kodak",
  "type": "concentrate",
  "film_or_paper": "film",
  "chemistry": null,
  "working_life_hours": null,
  "stock_life_months": null,
  "discontinued": 0,
  "notes": "Common dilutions: Dilution A (1:15), Dilution B (1:31)...",
  "mixing_instructions": null,
  "safety_notes": null,
  "dilutions": [
    {
      "id": 1,
      "name": "Dilution A",
      "dilution": "1:15"
    }
  ]
}
```

**Fields:**

- `id`: Unique identifier for the developer
- `name`: Developer name
- `manufacturer`: Manufacturer name
- `type`: Developer type (e.g., "concentrate")
- `film_or_paper`: Intended use (`"film"`, `"paper"`)
- `chemistry`: Chemical composition (optional)
- `working_life_hours`: Working solution lifespan (optional)
- `stock_life_months`: Stock solution lifespan (optional)
- `discontinued`: Boolean flag (0 = active, 1 = discontinued)
- `notes`: General notes about the developer
- `mixing_instructions`: How to mix the developer (optional)
- `safety_notes`: Safety information (optional)
- `dilutions`: Array of available dilutions with their ratios

### 🎯 `development_combinations.json`

Contains specific film and developer combinations with development times and procedures.

**Structure:**

```json
{
  "id": 1,
  "name": "Tri-X 400 @ 400 in HC-110 1:31",
  "film_stock_id": 59,
  "developer_name": "HC-110",
  "temperature_f": 68,
  "time_minutes": 11.0,
  "agitation_schedule": "30s initial, then 10s every 60s",
  "dilution": "1:31",
  "push_pull": 0,
  "notes": "Dilution B, agitate 30s every 60s"
}
```

**Fields:**

- `id`: Unique identifier for the combination
- `name`: Descriptive name of the combination
- `film_stock_id`: Reference to film stock in `film_stocks.json`
- `developer_name`: Name of the developer used
- `temperature_f`: Development temperature in Fahrenheit
- `time_minutes`: Development time in minutes
- `agitation_schedule`: Agitation pattern description
- `dilution`: Developer dilution ratio
- `push_pull`: Push/pull stops (0 = normal, positive = push, negative = pull)
- `notes`: Additional development notes

### 📏 `formats.json`

Contains information about film formats.

**Structure:**

```json
{
  "id": 1,
  "name": "35mm",
  "description": null
}
```

**Fields:**

- `id`: Unique identifier for the format
- `name`: Format name (e.g., "35mm", "120")
- `description`: Format description (optional)

## 🤝 Contributing

We welcome contributions to improve and expand this analog photography database! Here's how you can help:

### 🐛 Reporting Issues

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

### 🔄 Pull Requests

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

### 📋 Contribution Guidelines

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

### 🔍 Data Sources

When adding new data, please use reliable sources such as:

- Official manufacturer specifications
- Reputable photography publications
- Film photography community databases
- Personal testing results (clearly marked as such)

### 📞 Questions?

Feel free to open an issue for questions about:

- Data structure or formatting
- Contribution process
- Missing information
- General project direction

---

**Note:** This is a community-driven project. All contributions are appreciated and help make analog photography more accessible to everyone!
