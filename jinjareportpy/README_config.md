# Configuration Module

## Overview

Centralized configuration management for JinjaReportPy with multi-source priority resolution.

## Installation

The module is included in the project. No additional dependencies required for basic usage.
For TOML support (Python < 3.11): `pip install tomli`

## Quick Start

```python
from jinjareportpy import JinjaReportConfig, get_output_dir, set_output_dir

# Get current configuration
config = JinjaReportConfig.get_all_config()

# Access specific values
output_dir = get_output_dir()
locale = JinjaReportConfig.get_locale()

# Set values programmatically
set_output_dir("./my_reports")
JinjaReportConfig.set_locale("en_US")
```

## Priority Resolution

Values are resolved in order (first match wins):

1. **Environment** - Variables with prefix `JINJAREPORT_`
2. **Programmatic** - `JinjaReportConfig.set_*()` methods
3. **File** - TOML configuration file (`jinjareportpy.toml`)
4. **Defaults** - Built-in default values

## Configuration File Format

### TOML (jinjareportpy.toml)

```toml
# JinjaReportPy Configuration
# ============================
# Priority: Environment variables > Programmatic > This file > Defaults

[paths]
templates_dir = "./templates"
formats_dir = "./formats"
output_dir = "./reports"
assets_dir = "./assets"

[report]
default_format = "corporate"
page_size = "A4"
orientation = "portrait"
locale = "es_ES"

[pdf]
zoom = 1.0
optimize_images = true
```

## Environment Variables

Prefix: `JINJAREPORT_`

| Variable | Description | Default |
|----------|-------------|---------|
| `JINJAREPORT_TEMPLATES_DIR` | Path to templates directory | `<package>/templates` |
| `JINJAREPORT_FORMATS_DIR` | Path to formats directory | `<package>/formats` |
| `JINJAREPORT_OUTPUT_DIR` | Path to output directory | `<package>/output` |
| `JINJAREPORT_ASSETS_DIR` | Path to assets directory | `<package>/assets` |
| `JINJAREPORT_CONFIG_FILE` | Path to TOML config file | `./jinjareportpy.toml` |
| `JINJAREPORT_DEFAULT_FORMAT` | Default format name | `default` |
| `JINJAREPORT_PAGE_SIZE` | Page size | `A4` |
| `JINJAREPORT_ORIENTATION` | Page orientation | `portrait` |
| `JINJAREPORT_LOCALE` | Locale for formatting | `es_ES` |
| `JINJAREPORT_PDF_ZOOM` | PDF zoom level | `1.0` |
| `JINJAREPORT_PDF_OPTIMIZE_IMAGES` | Optimize PDF images | `true` |

## API Reference

### JinjaReportConfig Class

Central configuration class with all class methods (no instantiation needed).

#### Path Methods

| Method | Description |
|--------|-------------|
| `get_templates_dir()` | Get templates directory (Path) |
| `set_templates_dir(path)` | Set templates directory |
| `get_formats_dir()` | Get formats directory (Path) |
| `set_formats_dir(path)` | Set formats directory |
| `get_output_dir()` | Get output directory (Path) |
| `set_output_dir(path)` | Set output directory |
| `get_assets_dir()` | Get assets directory (Path) |
| `set_assets_dir(path)` | Set assets directory |

#### Setting Methods

| Method | Description |
|--------|-------------|
| `get_default_format()` | Get default format name (str) |
| `set_default_format(name)` | Set default format |
| `get_locale()` | Get locale (str) |
| `set_locale(locale)` | Set locale |
| `get_page_size()` | Get page size (str) |
| `set_page_size(size)` | Set page size (A4, A3, LETTER, LEGAL) |
| `get_orientation()` | Get orientation (str) |
| `set_orientation(orient)` | Set orientation (portrait, landscape) |

#### PDF Methods

| Method | Description |
|--------|-------------|
| `get_pdf_zoom()` | Get PDF zoom level (float) |
| `set_pdf_zoom(zoom)` | Set PDF zoom level |
| `get_pdf_optimize_images()` | Get image optimization flag (bool) |
| `set_pdf_optimize_images(flag)` | Set image optimization |

#### Utility Methods

| Method | Description |
|--------|-------------|
| `get_all_config()` | Get all resolved values as dict |
| `load_from_file(path)` | Load configuration from TOML file |
| `reset()` | Reset all configuration to defaults |

### Convenience Functions

| Function | Description |
|----------|-------------|
| `get_templates_dir()` | Get templates directory |
| `set_templates_dir(path)` | Set templates directory |
| `get_formats_dir()` | Get formats directory |
| `set_formats_dir(path)` | Set formats directory |
| `get_output_dir()` | Get output directory |
| `set_output_dir(path)` | Set output directory |
| `get_assets_dir()` | Get assets directory |
| `set_assets_dir(path)` | Set assets directory |
| `get_locale()` | Get locale |
| `set_locale(locale)` | Set locale |
| `get_page_size()` | Get page size |
| `set_page_size(size)` | Set page size |
| `get_orientation()` | Get orientation |
| `set_orientation(orient)` | Set orientation |

### ReportConfig Dataclass

Configuration object for individual reports/documents.

```python
from jinjareportpy import ReportConfig, PageSize, Orientation

config = ReportConfig(
    output_dir=Path("./reports"),
    page_size=PageSize.A4,
    orientation=Orientation.PORTRAIT,
    locale="es_ES",
)
```

**Attributes:**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `template_dirs` | list[Path] | [] | Template search paths |
| `assets_dir` | Path | None | Assets directory |
| `output_dir` | Path | `<package>/output` | Output directory |
| `page_size` | PageSize | A4 | Page size |
| `orientation` | Orientation | PORTRAIT | Page orientation |
| `encoding` | str | "utf-8" | Character encoding |
| `auto_reload` | bool | False | Template auto-reload |
| `locale` | str | "es_ES" | Locale for formatting |
| `browser_command` | str | None | Custom browser command |
| `pdf_viewer_command` | str | None | Custom PDF viewer |
| `pdf_options` | dict | {} | PDF-specific options |

### Enums

#### PageSize

| Value | Dimensions |
|-------|------------|
| `A4` | 210mm × 297mm |
| `A3` | 297mm × 420mm |
| `LETTER` | 8.5in × 11in |
| `LEGAL` | 8.5in × 14in |

#### Orientation

| Value | Description |
|-------|-------------|
| `PORTRAIT` | Vertical orientation |
| `LANDSCAPE` | Horizontal orientation |

## Usage Examples

### Basic Usage

```python
from jinjareportpy import JinjaReportConfig, get_output_dir

# Access configuration
output = get_output_dir()
print(f"Output directory: {output}")

# Get all configuration
config = JinjaReportConfig.get_all_config()
print(f"Locale: {config['locale']}")
print(f"Page size: {config['page_size']}")
```

### Programmatic Configuration

```python
from jinjareportpy import (
    set_output_dir,
    set_locale,
    set_page_size,
    set_orientation,
)

# Configure for US Letter format
set_output_dir("./reports")
set_locale("en_US")
set_page_size("LETTER")
set_orientation("portrait")
```

### Environment Variables

```bash
# Set configuration via environment (Linux/macOS)
export JINJAREPORT_OUTPUT_DIR="./my_reports"
export JINJAREPORT_LOCALE="en_US"
export JINJAREPORT_DEFAULT_FORMAT="corporate"
export JINJAREPORT_PAGE_SIZE="LETTER"

# Windows PowerShell
$env:JINJAREPORT_OUTPUT_DIR = "./my_reports"
$env:JINJAREPORT_LOCALE = "en_US"
```

```python
# Python uses environment automatically
from jinjareportpy import get_output_dir, get_locale

print(get_output_dir())  # ./my_reports
print(get_locale())       # en_US
```

### Configuration File

```python
from jinjareportpy import JinjaReportConfig

# Load from specific file
JinjaReportConfig.load_from_file("./config/jinjareportpy.toml")

# Get resolved values
config = JinjaReportConfig.get_all_config()
```

### With Documents

```python
from jinjareportpy import create_invoice, ReportConfig, PageSize, Orientation
from pathlib import Path

# Option 1: Use global configuration
set_output_dir("./invoices")
set_locale("en_US")

invoice = create_invoice(
    invoice_number="INV-2026-001",
    company={"name": "My Company"},
    client={"name": "Client Corp"},
    items=[{"description": "Service", "quantity": 1, "unit_price": 100}],
)
invoice.export_pdf("invoice.pdf")  # Saves to ./invoices/invoice.pdf

# Option 2: Use ReportConfig per document
config = ReportConfig(
    output_dir=Path("./custom_output"),
    page_size=PageSize.LETTER,
    orientation=Orientation.PORTRAIT,
    locale="en_US",
)

invoice = create_invoice(
    invoice_number="INV-2026-002",
    company={"name": "My Company"},
    client={"name": "Client Corp"},
    items=[{"description": "Service", "quantity": 1, "unit_price": 100}],
    config=config,
)
```

### With Reports

```python
from jinjareportpy import ReportBuilder, set_default_format

# Set global format
set_default_format("corporate")

builder = (
    ReportBuilder("Quarterly Report")
    .header(title="Q4 2025 Report")
    .add_kpis("metrics", [
        {"label": "Revenue", "value": "€125K", "change": 15},
    ])
    .add_text("summary", "Executive summary...")
)

builder.export_pdf("report.pdf")
```

### Reset Configuration

```python
from jinjareportpy import JinjaReportConfig

# Reset all programmatic settings to defaults
JinjaReportConfig.reset()
```

## Integration with CLI Module

The configuration module integrates with the CLI for command-line management.

### CLI Commands

```bash
# Show current configuration
python -m jinjareportpy config show

# Show as JSON
python -m jinjareportpy config show --json

# Set values (session only)
python -m jinjareportpy config set output_dir ./reports
python -m jinjareportpy config set locale en_US

# Reset to defaults
python -m jinjareportpy config reset

# Create config file
python -m jinjareportpy config init
```

### Priority with CLI

When using CLI commands, global configuration is used automatically:

```bash
# Config file has: default_format = "corporate"
# Environment has: JINJAREPORT_DEFAULT_FORMAT = "minimal"
# CLI uses environment value (higher priority):
python -m jinjareportpy demo  # Uses "minimal" format
```

### Combined Usage

```python
from jinjareportpy import JinjaReportConfig, ReportBuilder
from jinjareportpy.cli import main

# Load configuration
config = JinjaReportConfig.get_all_config()

# Use in code
builder = ReportBuilder("Report", format_name=config['default_format'])

# Use via CLI
main(['demo', '--format', config['default_format']])
```

For full CLI documentation, see [README_cli.md](README_cli.md).

## Default Values

| Setting | Default Value |
|---------|---------------|
| `templates_dir` | `<package>/templates` |
| `formats_dir` | `<package>/formats` |
| `output_dir` | `<package>/output` |
| `assets_dir` | `<package>/assets` |
| `default_format` | `default` |
| `page_size` | `A4` |
| `orientation` | `portrait` |
| `locale` | `es_ES` |
| `pdf_zoom` | `1.0` |
| `pdf_optimize_images` | `true` |
