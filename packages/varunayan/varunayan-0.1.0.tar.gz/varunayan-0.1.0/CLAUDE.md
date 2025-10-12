# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Varunayan is a Python package for downloading and processing ERA5 climate data. It provides a command-line interface and Python API for extracting analysis-ready climate data for custom geographical regions using GeoJSON files, bounding boxes, or point coordinates.

## Key Architecture

### Core Components

- **CLI Interface** (`varunayan/cli.py`): Entry point with argparse-based command line interface supporting three modes:
  - `geojson`: Process using GeoJSON/JSON file 
  - `bbox`: Process using bounding box coordinates
  - `point`: Process using single point (lat, lon)

- **Core Processing** (`varunayan/core.py`): Main processing engine with three public functions:
  - `era5ify_geojson()`: Process with GeoJSON file
  - `era5ify_bbox()`: Process with bounding box
  - `era5ify_point()`: Process with point coordinates

- **Download Module** (`varunayan/download/`): ERA5 data downloading from CDS API
- **Processing Module** (`varunayan/processing/`): Data aggregation, filtering, and file handling
- **Search Module** (`varunayan/search_and_desc/`): Variable lists and search functions
- **Utilities** (`varunayan/util/`): GeoJSON utilities and logging

### Data Flow

1. Input validation and parameter parsing
2. GeoJSON loading/creation and bounding box calculation
3. Time-based chunking for large requests (>14 days or >100 months)
4. ERA5 data download with retry logic
5. NetCDF processing and spatial filtering
6. Temporal aggregation by frequency
7. Output generation (CSV files in `{request_id}_output/` directory)

## Development Commands

### Testing
```bash
pytest                    # Run all tests
pytest tests/test_cli.py  # Run specific test file
pytest --cov=varunayan    # Run with coverage
```

### Code Quality
```bash
black .                   # Format code
isort .                   # Sort imports
flake8                    # Lint code
mypy varunayan/           # Type checking
```

### Installation
```bash
pip install -e .          # Development installation
pip install -e .[dev]     # Install with dev dependencies
```

### Building
```bash
python -m build          # Build distribution packages
```

## Important Implementation Details

### Dataset Types
- `single`: Single-level variables (default)
- `pressure`: Pressure-level variables (requires `--pressure-levels`)

### Time Chunking Strategy
- Daily/hourly data: 14-day chunks maximum
- Monthly/yearly data: 100-month chunks maximum  
- Automatic retry with exponential backoff for downloads

### Variable Handling
- Sum variables (precipitation, radiation, etc.) are adjusted for temporal aggregation
- Monthly aggregation multiplies by days in month
- Yearly aggregation multiplies by 30.4375 (average days per month)

### Output Files
Each request generates three CSV files in `{request_id}_output/`:
- `{request_id}_{frequency}_data.csv`: Aggregated data
- `{request_id}_unique_latlongs.csv`: Unique coordinate pairs
- `{request_id}_raw_data.csv`: Raw downloaded data

### Configuration
- Requires CDS API configuration in `~/.cdsapirc`
- Automatically validates configuration on startup
- Uses temporary files for processing, cleaned up after completion

## Testing Strategy

The test suite covers:
- CLI argument parsing and validation
- Core processing functions
- Download functionality
- Data processing and aggregation
- Utility functions
- Error handling and edge cases

Tests use pytest with coverage reporting and are configured in `pyproject.toml`.