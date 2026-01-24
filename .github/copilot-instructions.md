# 🥷 NinjaReportPy - Project Instructions

Programmatic document and report generator with dynamic sections and PDF export.

## Architecture

```
BaseDocument (ABC)      ← Abstract base class
├── Document            ← Documents (invoices, quotes, receipts, delivery notes)
└── Report              ← Multi-page reports with sections
```

## Project Structure

```
NinjaReportPy/                    # Project root
├── ninjareportpy/                # 📦 Main package (portable, self-contained)
│   ├── __init__.py            # Public API exports
│   ├── __main__.py            # CLI entry point
│   ├── base.py                # BaseDocument abstract class
│   ├── document.py            # Document class + factory functions
│   ├── report.py              # Report class (multi-page)
│   ├── page.py                # Page class
│   ├── sections.py            # Section classes
│   ├── builder.py             # ReportBuilder API
│   ├── config.py              # Configuration classes
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

**INSIDE `ninjareportpy/`** (Portable package):
- Source code modules (.py files)
- `templates/` - Built-in HTML templates
- `formats/` - Predefined styling formats
- `output/` - Default output for generated files (auto-created)

**OUTSIDE `ninjareportpy/`** (Project files):
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
- `winformpy` + `tkinterweb` - Embedded browser GUI (optional: `[gui]`)

## Running the Project

```bash
# Demo (requires setting PYTHONPATH)
# Windows PowerShell:
$env:PYTHONPATH="."; python examples/demo.py

# Linux/macOS:
PYTHONPATH=. python examples/demo.py

# With PDF support
uv add ninjareportpy[pdf]
```

## Testing

```bash
uv run pytest
uv run pytest --cov=ninjareportpy
```

## Code Patterns

### Documents (Invoices, Quotes, Receipts, Delivery Notes)

```python
from ninjareportpy import create_invoice, create_quote, create_receipt, create_delivery_note

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
from ninjareportpy import Document

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
from ninjareportpy import ReportBuilder

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
from ninjareportpy import Report, Section, TableSection, KPISection, set_default_format

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
from ninjareportpy import set_default_format, get_available_formats

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

### Embedded Browser (WinFormPy Integration)

For desktop applications, you can embed reports in a WinFormPy window:

```bash
# Install with GUI support
uv add ninjareportpy[gui]
# or: pip install ninjareportpy[gui]
```

```python
from ninjareportpy import Report, check_winformpy_available

# Check if WinFormPy is available
if check_winformpy_available():
    from winformpy import Application
    
    report = Report(title="Sales Report")
    page = report.add_page()
    page.set_header(title="Q4 Report")
    page.add_section(TextSection(name="intro", content="<p>Summary...</p>"))
    
    # Create a standalone viewer form
    viewer = report.create_viewer_form(
        title="Report Viewer",
        width=900,
        height=700,
        with_navigation=True,  # Include navigation bar
    )
    Application.Run(viewer)
```

Or embed in your own forms:

```python
from winformpy import Form, Panel, DockStyle, Application
from ninjareportpy import Document, create_invoice

class InvoiceViewer(Form):
    def __init__(self):
        super().__init__()
        self.Text = "Invoice Viewer"
        self.Width = 800
        self.Height = 600
        
        invoice = create_invoice(
            invoice_number="INV-001",
            company={"name": "My Company"},
            client={"name": "Client"},
            items=[{"description": "Service", "quantity": 1, "unit_price": 100}],
        )
        
        # Embed in this form
        invoice.preview_embedded(self, {'Dock': DockStyle.Fill})

app = InvoiceViewer()
Application.Run(app)
```

Available viewer functions:

```python
from ninjareportpy import (
    check_winformpy_available,   # Check if WinFormPy is installed
    create_embedded_browser,     # Create basic WebBrowser control
    create_browser_panel,        # Create WebBrowserPanel with navigation
    open_in_embedded_browser,    # Create and display HTML in one call
)
```

### Output Directory Configuration

By default, generated files are saved to `output/` inside the `ninjareportpy` package directory, so it is portable regardless of the current working directory. Customize with `ReportConfig`:

```python
from ninjareportpy import Report, Document, ReportConfig
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
