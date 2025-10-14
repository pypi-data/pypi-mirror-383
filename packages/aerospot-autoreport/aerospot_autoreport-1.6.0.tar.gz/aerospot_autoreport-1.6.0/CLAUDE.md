# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoReportV3 is an enterprise-grade automated report generation system for water quality monitoring using UAV aerial data. The project uses a modular architecture with domain-driven design, supporting pluggable business domains.

**Core Features:**
- UAV data processing and analysis
- Water quality modeling and prediction
- Satellite map visualization generation (with Kriging interpolation)
- Professional Word document report generation with watermark support
- Multi-format data support (CSV, KML, ZIP)
- Intelligent boundary detection (KML, Alpha Shape, Convex Hull)

## Development Environment

**Required Tools:**
- Python 3.10+ (Python 3.11 recommended, also supports 3.12)
- uv for dependency management (with Tsinghua mirror configured)
- pytest for testing

**Environment Setup:**
```bash
# Install dependencies (using uv with Tsinghua mirror)
uv pip install -e .

# Run main application
uv run python interface.py [config.json]

# Run with default config
uv run python interface.py  # uses test.json by default

# Run tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/end_to_end/

# Generate test coverage report
uv run pytest --cov=src/autoreport tests/

# Run with HTML coverage report
uv run pytest --cov=src/autoreport --cov-report=html tests/

# Run single test file
uv run pytest tests/unit/test_config_validator.py -v
```

**Installing from PyPI:**
```bash
# Install the published package
pip install aerospot-autoreport

# Install with development dependencies
pip install aerospot-autoreport[dev]
```

## Architecture Overview

The system follows a **layered architecture** with **pluggable domain modules**:

### Core Data Flow
```
Config Loading → Resource Download → Data Extraction → Data Processing → 
Model Training → Visualization → Report Generation
```

### Key Components

**Core Modules (`src/autoreport/core/`):**
- `generator.py`: Report generation engine
- `resource_manager.py`: Resource download and caching
- `error_handler.py`: Unified error handling
- `config_validator.py`: Configuration validation

**Domain System (`src/autoreport/domains/`):**
- Pluggable architecture for different monitoring domains
- `water_quality/`: Water quality monitoring implementation
- Base interfaces for domain extension

**Data Processing (`src/autoreport/processor/`):**
- `data/`: Core data processing pipeline
- `maps.py`: Satellite map generation and visualization
- `extractor.py`: ZIP file extraction
- `downloader.py`: Resource downloading

**Document Generation (`src/autoreport/document/`):**
- `pages.py`: Page layout and formatting
- `paragraphs.py`: Text content generation
- `tables.py`: Table generation
- `images.py`: Image processing and embedding

## Configuration System

**Configuration File Structure:**
```json
{
  "data_root": "./AutoReportResults/",
  "visualization_mode": "quantitative",
  "company_info": {
    "name": "Company Name",
    "logo_path": "OSS_URL or local_path",
    "satellite_img": "OSS_URL or local_path",
    "wayline_img": "OSS_URL or local_path",
    "file_url": "OSS_URL or local_path (ZIP)",
    "measure_data": "OSS_URL or local_path (CSV)",
    "kml_boundary_url": "OSS_URL or local_path (KML, OPTIONAL)",
    "north_east": "lng,lat",
    "south_west": "lng,lat",
    "south_east": "lng,lat",
    "north_west": "lng,lat",
    "watermark_enabled": true,
    "watermark_text": "Your Watermark",
    "watermark_use_spire": true
  },
  "pollution_source": {
    "source1": "description1",
    "source2": "description2"
  }
}
```

**Key Configuration Points:**
- `data_root`: Base output directory for all generated files (timestamped subdirectories auto-created)
- `visualization_mode`: "quantitative" or "qualitative" visualization mode
- `company_info`: Resource URLs (supports both OSS URLs and local file paths) and company details
  - Geographic boundaries defined by four corner coordinates
  - `kml_boundary_url`: Optional KML file for custom boundary definition
  - Watermark configuration (requires spire-doc library)
- `pollution_source`: Optional pollution source information for report

**KML Boundary Feature:**
- If `kml_boundary_url` is provided and valid, the system will use KML-defined boundaries for map generation
- If no KML file is provided or the file is invalid, the system falls back to automatic alpha_shape boundary detection
- KML boundaries are used for interpolation heat maps, clean transparent maps, and level distribution maps
- Supports complex polygonal boundaries defined in standard KML format

**Visualization Modes:**
- `quantitative`: Continuous color mapping for numeric values (default)
- `qualitative`: Categorical color mapping for water quality levels (GB 3838-2002 standards)

## Development Workflow

**Main Entry Points:**
- `interface.py`: CLI entry with hardcoded cache control (modify `CACHE_ENABLED` variable)
- `src/autoreport/main.py`: Core application logic with complete data flow orchestration

**Execution Flow:**
1. Config loading and validation (`config_validator.py`)
2. Resource download with caching (`resource_manager.py`)
3. ZIP extraction and data file discovery (`extractor.py`)
4. UAV data processing and standardization (`processor/data/`)
5. Optional: Measure data processing and matching with UAV data
6. Kriging interpolation and map generation (`processor/maps.py`)
7. Report structure generation (`processor/config.py`)
8. Word document generation with watermark (`core/generator.py`)
9. Model coefficient encryption and export (optional)

**Data Processing Pipeline (src/autoreport/processor/data/):**
- `processor.py`: Main `DataProcessor` class orchestrating all data operations
- `standardizer.py`: Column name and indicator name standardization
- `analyzer.py`: Statistical analysis and error calculation
- `matcher.py`: Spatial matching between UAV and measurement data
- `utils.py`: Helper functions for indicator units and data utilities

**Testing Strategy:**
- `tests/unit/`: Individual component tests (config_validator, kml_parser, resource_manager)
- `tests/integration/`: Data processing workflow tests
- `tests/end_to_end/`: Complete report generation tests
- Use `pytest.fixtures` defined in `conftest.py` for test data setup

## Key Dependencies

**Core Dependencies:**
- `pandas`, `numpy`: Data processing and numerical operations
- `python-docx`: Word document manipulation
- `spire-doc`: Advanced watermark functionality (evaluation version with warning removal logic)
- `matplotlib`, `seaborn`: Visualization and plotting
- `pykrige`: Kriging interpolation (Universal Kriging and Ordinary Kriging)
- `autowaterqualitymodeler`: Water quality model training and encryption
- `scikit-learn`: Machine learning and RBF interpolation
- `scipy`: Scientific computing (convex hull, Delaunay triangulation, interpolation)
- `opencv-python`: Image processing
- `pillow`: Image manipulation
- `requests`, `oss2`: Resource downloading from OSS/HTTP

**Platform-Specific:**
- `pywin32`: Windows-specific functionality (auto-installed on Windows only via conditional dependencies)

**Interpolation Methods (src/autoreport/processor/maps.py):**
- **Primary**: Universal Kriging (gaussian variogram, regional_linear drift)
- **Fallback 1**: Ordinary Kriging (spherical/exponential variogram)
- **Fallback 2**: Linear interpolation (griddata)
- Configure via `GLOBAL_KRIGING_METHOD` and `KRIGING_CONFIG` in maps.py

## Cache and Resource Management

**Cache Control:**
- Modify `CACHE_ENABLED` in `interface.py` to enable/disable caching
- Resources cached for 15 minutes by default
- Cache location: `global_cache/` directory

**Resource Types:**
- Logo images
- Satellite imagery
- Wayline images
- Data files (ZIP format)
- Measurement data (CSV format)

## Important Implementation Notes

**Watermark Handling:**
- Spire.Doc is used for watermark functionality but includes evaluation warnings
- The code automatically removes "Evaluation Warning" text from generated documents
- See `src/autoreport/core/generator.py:145-150` for warning removal implementation
- Watermark is added via temporary file processing to avoid XML manipulation issues

**Data Processing Specifics:**
- INDEXS.CSV files may contain "Unnamed" columns which are automatically handled
- Zero-value rows in indicator data are automatically filtered out for quality
- When UAV data and measurement data indicator counts mismatch, intersection is taken
- Indicator name standardization supports multiple aliases (e.g., "氨氮", "NH3-N", "nh3n")

**Map Generation:**
- Kriging interpolation handles negative values via transform methods (log, clip, none)
- Four boundary detection algorithms with intelligent fallback:
  1. KML boundary (if provided)
  2. Alpha shape (concave hull for complex shapes)
  3. Convex hull (simple geometric boundary)
  4. Density-based (point cloud clustering)
- SVG output supports transparent backgrounds for clean embedding
- Colorbar ranges are unified between SVG and PNG outputs for consistency

**Error Handling:**
- All major operations wrapped with `@safe_operation` decorator
- Errors logged to session-specific log files in output directory
- Graceful degradation: missing measurement data doesn't halt UAV processing
- Resource download failures are logged but don't stop the pipeline

## Common Commands

```bash
# Run with specific configuration
uv run python interface.py path/to/config.json

# Run with default test config
uv run python interface.py test.json
uv run python interface.py  # same as above

# Toggle cache (edit interface.py)
# Set CACHE_ENABLED = True or False at line 14

# Development commands
uv pip install -e .  # Install in editable mode
uv pip install -e .[dev]  # Install with dev dependencies

# Testing
uv run pytest  # Run all tests
uv run pytest tests/unit/  # Unit tests only
uv run pytest tests/integration/  # Integration tests only
uv run pytest tests/end_to_end/  # End-to-end tests only
uv run pytest tests/unit/test_config_validator.py -v  # Single file with verbose
uv run pytest --cov=src/autoreport --cov-report=html tests/  # Coverage report

# Code quality
uv run black src/ tests/  # Format code
uv run ruff check src/ tests/  # Lint code
uv run mypy src/  # Type checking

# Release (CI/CD handles this automatically on tag push)
git tag -a v0.5.3 -m "Release v0.5.3"
git push origin v0.5.3  # Triggers GitHub Actions workflow
```

## Output Structure

Generated reports are organized in timestamped directories:
```
AutoReportResults/
├── README.md              # Auto-generated report history log
└── report_YYYYMMDD_HHMMSS/
    ├── downloads/          # Downloaded resources (logo, satellite image, data files)
    ├── extracted/          # Extracted ZIP contents (INDEXS.CSV, POS.TXT, REFL files)
    ├── maps/              # Generated visualizations (PNG, SVG formats)
    │   ├── *_distribution.png      # Scatter distribution maps
    │   ├── *_interpolation.png     # Decorated interpolation heatmaps
    │   ├── *_clean_interpolation_svg.svg  # Clean SVG heatmaps
    │   └── *_level.png            # Water quality level maps (GB standards)
    ├── reports/           # Final Word documents
    │   ├── AeroSpotReport自动报告.docx
    │   ├── report_structure.json
    │   └── processed_config.json
    ├── models/            # Encrypted model files (.bin format)
    ├── predict/           # Model prediction results
    │   └── predict_result.csv
    ├── logs/              # Application logs (with timestamps)
    │   └── autoreport_YYYYMMDD_HHMMSS.log
    └── uav_data/          # Processed UAV data
        ├── uav.csv        # Processed UAV inversion data
        └── ref_data.csv   # Spectral reflectance data
```

**Key Output Files:**
- `reports/AeroSpotReport自动报告.docx`: Final professional report with watermark
- `models/*.bin`: Encrypted model coefficients (AES encryption with autowaterqualitymodeler)
- `predict/predict_result.csv`: Optimized model prediction results
- `logs/*.log`: Detailed execution logs for debugging

## Error Handling

- All operations use `@safe_operation` decorator for unified error handling
- Logging configured per-session in output directory (`logs/autoreport_YYYYMMDD_HHMMSS.log`)
- Custom exceptions defined in `src/autoreport/exceptions.py`:
  - `AeroSpotError`: Base exception class
  - `DataProcessingError`: Data-related errors
  - `ReportGenerationError`: Report generation failures
  - `ResourceError`: Resource download/access errors
- Graceful degradation for optional features (like manual sampling data)
- README.md in AutoReportResults/ auto-updates with generation history

## CI/CD and Publishing

**GitHub Actions Workflow (`.github/workflows/release.yml`):**
- Triggers on git tag push (`v*`)
- Builds wheel and source distribution
- Runs local installation test
- Publishes to PyPI using API token
- Creates GitHub release with auto-generated notes
- Includes distribution files as release assets

**Publishing Process:**
```bash
# 1. Update version (handled by setuptools_scm from git tags)
# 2. Create and push tag
git tag -a v0.5.3 -m "Release v0.5.3"
git push origin v0.5.3

# 3. GitHub Actions automatically:
#    - Builds package
#    - Tests installation
#    - Publishes to PyPI
#    - Creates GitHub release
```

**Package Info:**
- PyPI name: `aerospot-autoreport`
- Version scheme: Simplified semantic versioning from git tags
- Entry point: `autoreport` command-line tool