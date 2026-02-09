# 🥷 JinjaReportPy - Project Instructions

Programmatic document and report generator with dynamic sections and PDF export.

## Architecture

```
BaseDocument (ABC)      ← Abstract base class
├── Document            ← Documents (invoices, quotes, receipts, delivery notes)
└── Report              ← Multi-page reports with sections
```

## Project Structure

```
jinjareportpy/                    # Project root
├── jinjareportpy/                # 📦 Main package (portable, self-contained)
│   ├── __init__.py            # Public API exports
│   ├── __main__.py            # CLI entry point
│   ├── cli.py                 # Command line interface
│   ├── config.py              # Configuration management
│   ├── base.py                # BaseDocument abstract class
│   ├── document.py            # Document class + factory functions
│   ├── report.py              # Report class (multi-page)
│   ├── page.py                # Page class
│   ├── sections.py            # Section classes
│   ├── builder.py             # ReportBuilder API
│   ├── assets.py              # Asset management
│   ├── filters.py             # Jinja2 filters
│   ├── pdf.py                 # PDF export
│   ├── viewer.py              # Browser/PDF viewer
│   ├── generator.py           # Legacy API
│   ├── exceptions.py          # Custom exceptions
│   ├── templates/             # Built-in document templates
│   │   ├── invoice.html, quote.html, receipt.html, delivery_note.html
│   ├── formats/               # Predefined formats (default, corporate, minimal)
│   └── output/                # Generated files (auto-created, portable)
│
├── examples/                  # Usage examples (demo.py, test_output_config.py)
├── tests/                     # Unit tests
├── .github/                  # Project documentation
├── pyproject.toml            # Package configuration
└── README.md
```

### Directory Organization

**INSIDE `jinjareportpy/`** (Portable package):
- Source code modules (.py files)
- `templates/` - Built-in HTML templates
- `formats/` - Predefined styling formats
- `output/` - Default output for generated files (auto-created)

**OUTSIDE `jinjareportpy/`** (Project files):
- `examples/` - Demo and usage examples
- `tests/` - Unit tests
- `.github/` - Documentation and CI
- `pyproject.toml` - Package metadata

## Development Guidelines

- Use Python 3.10+
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write unit tests for new features
- Use dataclasses for configuration objects
- Handle errors with custom exceptions from `exceptions.py`

## Key Dependencies

- `jinja2` - Template engine (required)
- `weasyprint` - PDF export (optional: `[pdf]`)
- `pandas` - DataFrame support (optional: `[pandas]`)

## Command Line Interface (CLI)

JinjaReportPy provides a full CLI for managing configuration and generating documents:

```bash
# Show help
python -m jinjareportpy --help

# Configuration commands
python -m jinjareportpy config show              # Show current configuration
python -m jinjareportpy config show --json       # Output as JSON
python -m jinjareportpy config set locale en_US  # Set locale
python -m jinjareportpy config set output_dir ./reports  # Set output directory
python -m jinjareportpy config reset             # Reset to defaults
python -m jinjareportpy config init              # Create config file in current dir

# Generate demo report
python -m jinjareportpy demo                     # Default format
python -m jinjareportpy demo --format corporate  # Corporate format
python -m jinjareportpy demo --pdf --open        # Generate PDF and open in browser

# List available formats and templates
python -m jinjareportpy formats                  # List formats
python -m jinjareportpy formats --details        # Show format files
python -m jinjareportpy templates                # List templates

# Generate documents
python -m jinjareportpy invoice -n INV-001 --company "My Corp"
python -m jinjareportpy quote -n QT-001 --client "Client Ltd" --pdf
```

**Available CLI Commands:**
- `config` - View and manage configuration (show, set, reset, init)
- `demo` - Generate a demo sales report
- `formats` - List available report formats
- `templates` - List available document templates
- `invoice` - Generate an invoice
- `quote` - Generate a quote

### CLI and Config Integration

The CLI (`cli.py`) and configuration (`config.py`) work together:

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI (cli.py)                        │
│  python -m jinjareportpy config set output_dir ./reports    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    JinjaReportConfig                        │
│  (centralized configuration in config.py)                   │
│                                                             │
│  Priority resolution:                                       │
│  1. Environment variables  (JINJAREPORT_OUTPUT_DIR)         │
│  2. Programmatic           (set_output_dir("./reports"))    │
│  3. Config file            (jinjareportpy.toml)             │
│  4. Default values         (jinjareportpy/output/)          │
└─────────────────────────────────────────────────────────────┘
```

**CLI Command → Config Function Mapping:**

| CLI Command | Config Function |
|-------------|-----------------|
| `config show` | `JinjaReportConfig.get_all_config()` |
| `config set output_dir ./x` | `JinjaReportConfig.set_output_dir()` |
| `config set locale en_US` | `JinjaReportConfig.set_locale()` |
| `config reset` | `JinjaReportConfig.reset()` |
| `config init` | Creates TOML file that `config.py` reads |

**Persistence Options:**
- **Session only**: `python -m jinjareportpy config set locale en_US` (not persisted)
- **Config file**: `python -m jinjareportpy config init` → edit `jinjareportpy.toml`
- **Environment**: `export JINJAREPORT_LOCALE="en_US"` (always active)

The CLI is the **user interface**, while `config.py` is the **configuration engine** that all modules use internally (`document.py`, `report.py`, `generator.py`, `formats/__init__.py`).

## Running the Project

```bash
# Demo (requires setting PYTHONPATH)
# Windows PowerShell:
$env:PYTHONPATH="."; python examples/demo.py

# Linux/macOS:
PYTHONPATH=. python examples/demo.py

# With PDF support
uv add jinjareportpy[pdf]
```

## Testing

```bash
uv run pytest
uv run pytest --cov=JinjaReportPy
```

## Code Patterns

### Documents (Invoices, Quotes, Receipts, Delivery Notes)

```python
from jinjareportpy import create_invoice, create_quote, create_receipt, create_delivery_note

# Invoice
invoice = create_invoice(
    invoice_number="INV-2026-001",
    company={"name": "My Company Ltd.", "tax_id": "GB123456789"},
    client={"name": "Client Corp", "tax_id": "GB987654321"},
    items=[
        {"description": "Service", "quantity": 10, "unit_price": 100},
    ],
    payment_info={"method": "Bank Transfer", "iban": "GB82..."},
)
invoice.export_pdf("invoice.pdf")

# Quote
quote = create_quote(
    quote_number="QT-2026-015",
    company={"name": "My Company Ltd."},
    client={"name": "Client Corp"},
    items=[{"description": "Project", "quantity": 1, "unit_price": 5000}],
    validity_days=30,
)
quote.export_pdf("quote.pdf")

# Receipt
receipt = create_receipt(
    receipt_number="REC-2026-042",
    company={"name": "My Company Ltd."},
    client={"name": "Client Corp"},
    amount=1500.00,
    concept="Payment for invoice INV-2025-089",
)
receipt.export_html("receipt.html")

# Delivery Note
delivery = create_delivery_note(
    delivery_number="DN-2026-007",
    company={"name": "My Company Ltd."},
    client={"name": "Client Corp"},
    items=[{"code": "HW-001", "description": "Server", "quantity": 2}],
)
delivery.export_html("delivery_note.html")
```

### Custom Documents

Custom templates can be added in two ways:
1. **Via directory**: Place `.html` files in `templates/` directory
2. **Via code**: Pass inline template string to `template` parameter

```python
from jinjareportpy import Document

doc = Document(
    title="Contract",
    template="""
    <h1>{{ title }}</h1>
    <p>Between {{ company }} and {{ client }}...</p>
    """,
    data={"title": "Contract", "company": "A", "client": "B"},
    css=".custom { color: blue; }",
)
doc.export_pdf("contract.pdf")
```

### Reports (Simplified API - Recommended)

```python
from jinjareportpy import ReportBuilder

builder = (
    ReportBuilder("My Report", format_name="corporate")
    .header(title="Title", subtitle="Subtitle")
    .footer(left="Company", center="Confidential", right="Page 1")
    .add_kpis("metrics", [
        {"label": "Sales", "value": "£50K", "change": "+12%"},
    ])
    .add_table("data", 
        headers=["Col1", "Col2"],
        rows=[["A", "B"], ["C", "D"]],
        title="Table"
    )
    .add_text("notes", "Text content")
)

builder.export_html("output.html")
builder.export_pdf("output.pdf")

# HTML for email (returns string, does not copy to clipboard)
html_email = builder.render_inline()
body_only = builder.to_clipboard_html()  # Returns body HTML as string
```

### Reports (Full Control API)

```python
from jinjareportpy import Report, Section, TableSection, KPISection, set_default_format

set_default_format("corporate")

report = Report(title="My Report")

page = report.add_page()
page.set_header(title="Title", subtitle="Subtitle")
page.set_footer(left_text="Company", center_text="Draft", right_text="Page 1")

page.add_section(KPISection(
    name="kpis",
    kpis=[{"label": "Sales", "value": "£50K", "change": 12}],
))

page.add_section(TableSection(
    name="table",
    headers=["Col1", "Col2"],
    rows=[["A", "B"]],
    footer_row=["Total", "100"],
))

page.add_section(Section(
    name="custom",
    template="<p>{{ text }}</p>",
    data={"text": "Custom content"},
    css=".section-custom { color: blue; }",
))

report.export_html("output.html")
report.export_pdf("output.pdf")
```

### Predefined Sections

```python
# Table section
TableSection(name, headers=[], rows=[[]], title="", footer_row=[])

# KPI section  
KPISection(name, kpis=[{"label": "X", "value": "Y", "change": 10}], title="")

# Text section
TextSection(name, content="<p>HTML</p>", title="")

# Custom section
Section(name, template="<p>{{ var }}</p>", data={}, css="")
```

### Using Formats

```python
from jinjareportpy import set_default_format, get_available_formats

print(get_available_formats())  # ['corporate', 'default', 'minimal']
set_default_format("corporate")
```

### Asset Management

```python
# In templates: {{ asset('logo.png') }}
# Converts images to Base64 automatically
```

### Corporate Branding (Logo & Colors)

```python
# Override CSS variables for custom colors
corporate_css = """
:root {
    --primary-color: #e11d48;   /* Headers, accents */
    --text-color: #0f172a;      /* Main text */
    --bg-light: #f1f5f9;        /* Card backgrounds */
}
"""

# For documents
invoice = create_invoice(
    invoice_number="INV-001",
    company={"name": "Corp", "logo": "logo.png"},
    client={"name": "Client"},
    items=[{"description": "Service", "quantity": 1, "unit_price": 100}],
    css=corporate_css,
)

# For reports
builder = ReportBuilder("Report")
builder.report.global_css = corporate_css
builder.header(title="Title", logo="logo.png")
```

**Available CSS Variables:**
- `--primary-color` - Headers, titles, accents (default: `#2563eb`)
- `--text-color` - Main text (default: `#1e293b`)
- `--text-muted` - Secondary text (default: `#64748b`)
- `--border-color` - Borders (default: `#e2e8f0`)
- `--bg-light` - Light backgrounds (default: `#f8fafc`)
- `--success-color` - Positive values (default: `#16a34a`)
- `--warning-color` - Warnings (default: `#ca8a04`)
- `--danger-color` - Negative values (default: `#dc2626`)

### Output Directory Configuration

By default, generated files are saved to `output/` inside the `JinjaReportPy` package directory, so it is portable regardless of the current working directory. Customize with `ReportConfig`:

```python
from jinjareportpy import Report, Document, ReportConfig
from pathlib import Path

# Custom output directory
config = ReportConfig(
    output_dir=Path("./my_reports"),
    page_size=PageSize.A4,
    orientation=Orientation.PORTRAIT,
    locale="es_ES",
)

# Use with documents and reports
doc = Document(title="Doc", template="<h1>Test</h1>", config=config)
report = Report(title="Report", config=config)

# Or specify path per export
invoice.export_html("C:/reports/invoice.html")
invoice.export_pdf(Path("./archives"), filename="invoice.pdf")
```

**ReportConfig parameters:**
- `output_dir` (Path): Default output directory (default: `./output`)
- `template_dirs` (list[Path]): Custom template directories
- `assets_dir` (Path): Assets directory for images/logos
- `page_size` (PageSize): A4, A3, LETTER, LEGAL
- `orientation` (Orientation): PORTRAIT, LANDSCAPE
- `locale` (str): Locale for formatting (es_ES, en_US, etc.)

The output directory is **auto-created** if it doesn't exist.

### Centralized Configuration (JinjaReportConfig)

The `JinjaReportConfig` class provides centralized configuration with multi-source resolution:

**Priority (highest to lowest):**
1. Environment variables
2. Programmatic: `JinjaReportConfig.set_*()` methods
3. Config file: `jinjareportpy.toml`
4. Default values

```python
from jinjareportpy import (
    JinjaReportConfig,
    get_templates_dir, set_templates_dir,
    get_formats_dir, set_formats_dir,
    get_output_dir, set_output_dir,
    get_assets_dir, set_assets_dir,
    get_locale, set_locale,
    get_page_size, set_page_size,
    get_orientation, set_orientation,
)

# Option 1: Programmatic configuration
set_templates_dir("./my_templates")
set_output_dir("./reports")
set_locale("en_US")
set_page_size("LETTER")
set_orientation("landscape")

# Option 2: Environment variables
import os
os.environ["JINJAREPORT_TEMPLATES_DIR"] = "/path/to/templates"
os.environ["JINJAREPORT_OUTPUT_DIR"] = "/path/to/output"
os.environ["JINJAREPORT_LOCALE"] = "en_US"

# Option 3: Config file (jinjareportpy.toml)
JinjaReportConfig.load_from_file("./jinjareportpy.toml")

# Get all current configuration
config = JinjaReportConfig.get_all_config()

# Reset to defaults
JinjaReportConfig.reset()
```

**Environment Variables:**
- `JINJAREPORT_TEMPLATES_DIR` - Path to templates directory
- `JINJAREPORT_FORMATS_DIR` - Path to formats directory
- `JINJAREPORT_OUTPUT_DIR` - Path to output directory
- `JINJAREPORT_ASSETS_DIR` - Path to assets directory
- `JINJAREPORT_CONFIG_FILE` - Path to TOML config file
- `JINJAREPORT_DEFAULT_FORMAT` - Default format (default, corporate, minimal)
- `JINJAREPORT_PAGE_SIZE` - Page size (A4, A3, LETTER, LEGAL)
- `JINJAREPORT_ORIENTATION` - Orientation (portrait, landscape)
- `JINJAREPORT_LOCALE` - Locale (es_ES, en_US, etc.)
- `JINJAREPORT_PDF_ZOOM` - PDF zoom level (1.0)
- `JINJAREPORT_PDF_OPTIMIZE_IMAGES` - Optimize images (true/false)

**Config File (jinjareportpy.toml):**
```toml
[paths]
templates_dir = "./my_templates"
formats_dir = "./my_formats"
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

### Report Viewer (Browser Integration)

The `ReportViewer` class manages browser windows intelligently:
- First report opens in a **new browser window**
- Subsequent reports open as **new tabs** in the same window

```python
from jinjareportpy import (
    open_in_browser,
    open_in_new_window,
    open_in_new_tab,
    reset_viewer,
    ReportViewer,
)

# Automatic behavior (recommended)
open_in_browser(html_path="report1.html")  # Opens new window
open_in_browser(html_path="report2.html")  # Opens new tab
open_in_browser(html_path="report3.html")  # Opens new tab

# Reset to start fresh (next open = new window)
reset_viewer()
open_in_browser(html_path="report4.html")  # Opens new window again

# Force specific behavior
open_in_new_window("report.html")  # Always new window
open_in_new_tab("report.html")     # Always new tab

# Using ReportViewer directly
viewer = ReportViewer()
viewer.open("report1.html")  # New window
viewer.open("report2.html")  # New tab
viewer.open("report3.html", force_new_window=True)  # Force new window
viewer.reset()  # Next open = new window
```

**Available Functions:**
- `open_in_browser(html_path)` - Smart open (window first, then tabs)
- `open_in_new_window(html_path)` - Always opens new window
- `open_in_new_tab(html_path)` - Always opens new tab
- `reset_viewer()` - Reset state (next open = new window)
- `get_viewer()` - Get the shared ReportViewer instance
