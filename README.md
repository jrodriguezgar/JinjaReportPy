# 🥷 NinjaReportPy

> Programmatic document and report generator with dynamic sections and PDF export.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 📄 **Documents**: Invoices, quotes, receipts, delivery notes with factory functions
- 📊 **Reports**: Multi-page reports with headers, footers, and dynamic sections
- 🎨 **Predefined Formats**: `default`, `corporate`, `minimal`
- 📧 **Email-Ready HTML**: Inline styles for email compatibility
- 📤 **PDF Export**: Via WeasyPrint (optional)
- �️ **Embedded Viewer**: Display reports in WinFormPy desktop apps (optional)
- 🀽� **Custom Templates**: Add templates via directory or inline code
- 🐼 **Pandas Support**: Direct DataFrame integration (optional)

## 📦 Installation

```bash
# Basic installation
pip install ninjareportpy

# With PDF support
pip install ninjareportpy[pdf]

# With Pandas support
pip install ninjareportpy[pandas]

# With GUI/Embedded browser support
pip install ninjareportpy[gui]

# Full installation
pip install ninjareportpy[all]
```

## 🏗️ Architecture

```
BaseDocument (ABC)      ← Abstract base class
├── Document            ← Documents (invoices, quotes, receipts, delivery notes)
└── Report              ← Multi-page reports with sections
```

### Class Hierarchy

- **BaseDocument**: Abstract base class with `render()`, `export_html()`, `export_pdf()`, `preview()` methods
- **Document**: Template-based documents for invoices, quotes, receipts, delivery notes
- **Report**: Multi-page reports with headers, footers, and dynamic sections

---

## 📄 Documents

### Factory Functions

The library provides convenient factory functions for common document types:

#### `create_invoice()` - Generate Invoices

Creates a professional invoice with automatic calculations (subtotals, taxes, totals).

```python
from reportpy import create_invoice

invoice = create_invoice(
    # Required parameters
    invoice_number="INV-2026-001",
    company={
        "name": "My Company Ltd.",
        "tax_id": "GB123456789",
        "address": "123 Business Street",
        "city": "London",
        "postal_code": "EC1A 1BB",
        "country": "United Kingdom",
        "phone": "+44 20 1234 5678",
        "email": "billing@mycompany.com",
        "logo": "logo.png",  # Optional: path to logo image
    },
    client={
        "name": "Client Corporation",
        "tax_id": "GB987654321",
        "address": "456 Client Avenue",
        "city": "Manchester",
        "postal_code": "M1 1AA",
    },
    items=[
        {"description": "Consulting services", "quantity": 10, "unit_price": 150.00},
        {"description": "Software license", "quantity": 1, "unit_price": 500.00},
        {"description": "Technical support", "quantity": 5, "unit_price": 75.00},
    ],
  
    # Optional parameters
    issue_date=None,           # Default: today
    due_date=None,             # Default: 30 days from issue
    tax_rate=20.0,             # VAT percentage (default: 21.0)
    currency="£",              # Currency symbol (default: "€")
    payment_info={
        "method": "Bank Transfer",
        "bank": "National Bank",
        "iban": "GB82WEST12345698765432",
        "swift": "WESTGB2L",
    },
    notes="Thank you for your business!",
    css="",                    # Additional custom CSS
)

# Export options
invoice.export_pdf("invoice.pdf")
invoice.export_html("invoice.html")
invoice.preview()  # Open in browser
```

**Automatic Calculations:**

- Line totals: `quantity × unit_price`
- Subtotal: Sum of all line totals
- Tax amount: `subtotal × tax_rate / 100`
- Total: `subtotal + tax_amount`

---

#### `create_quote()` - Generate Quotes/Estimates

Creates a quote with validity period and optional discount.

```python
from reportpy import create_quote

quote = create_quote(
    # Required parameters
    quote_number="QT-2026-015",
    company={"name": "My Company Ltd.", "tax_id": "GB123456789"},
    client={"name": "Potential Client", "email": "client@example.com"},
    items=[
        {"description": "Web Development Project", "quantity": 1, "unit_price": 5000.00},
        {"description": "Hosting (1 year)", "quantity": 12, "unit_price": 50.00},
    ],
  
    # Optional parameters
    issue_date=None,           # Default: today
    validity_days=30,          # Quote valid for N days (default: 30)
    tax_rate=20.0,             # VAT percentage
    currency="£",              # Currency symbol
    discount=0.0,              # Discount percentage (e.g., 10.0 for 10%)
    notes="This quote is valid for 30 days.",
    terms="50% upfront, 50% on completion.",
    css="",                    # Additional custom CSS
)

quote.export_pdf("quote.pdf")
```

**Features:**

- Automatic validity date calculation
- Optional discount percentage
- Terms and conditions section
- Professional formatting

---

#### `create_receipt()` - Generate Payment Receipts

Creates a receipt for payment confirmation.

```python
from reportpy import create_receipt

receipt = create_receipt(
    # Required parameters
    receipt_number="REC-2026-042",
    company={"name": "My Company Ltd."},
    client={"name": "Client Name"},
    amount=1500.00,
    concept="Payment for invoice INV-2025-089",
  
    # Optional parameters
    payment_date=None,         # Default: today
    payment_method="Bank Transfer",
    currency="£",              # Currency symbol
    notes="",                  # Additional notes
    css="",                    # Additional custom CSS
)

receipt.export_html("receipt.html")
receipt.export_pdf("receipt.pdf")
```

**Use Cases:**

- Payment confirmations
- Cash receipts
- Refund documentation
- Donation receipts

---

#### `create_delivery_note()` - Generate Delivery Notes

Creates a delivery/shipping note for goods dispatch.

```python
from reportpy import create_delivery_note

delivery = create_delivery_note(
    # Required parameters
    delivery_number="DN-2026-007",
    company={
        "name": "My Company Ltd.",
        "address": "123 Warehouse Lane",
    },
    client={
        "name": "Client Corp",
        "address": "789 Delivery Street",
        "city": "Birmingham",
    },
    items=[
        {"code": "HW-001", "description": "Server Unit", "quantity": 2},
        {"code": "HW-002", "description": "Network Switch", "quantity": 5},
        {"code": "ACC-010", "description": "Power Cables", "quantity": 10},
    ],
  
    # Optional parameters
    delivery_date=None,        # Default: today
    shipping_address=None,     # If different from client address
    carrier="Express Logistics",
    tracking_number="TRK-123456789",
    notes="Handle with care. Fragile equipment.",
    css="",                    # Additional custom CSS
)

delivery.export_html("delivery_note.html")
```

**Features:**

- Product codes and descriptions
- Quantity tracking
- Carrier and tracking information
- Shipping address (if different from billing)
- Notes for special handling

---

### Custom Documents

Create any document type with custom templates:

```python
from reportpy import Document

# Option 1: Inline template
doc = Document(
    title="Service Contract",
    template="""
    <div class="contract">
        <h1>{{ title }}</h1>
        <p>This contract is between <strong>{{ company }}</strong> 
           and <strong>{{ client }}</strong>.</p>
        <p>Date: {{ now().strftime('%Y-%m-%d') }}</p>
        <div class="terms">{{ terms | safe }}</div>
    </div>
    """,
    data={
        "title": "Service Agreement",
        "company": "My Company Ltd.",
        "client": "Client Corp",
        "terms": "<ol><li>Term 1</li><li>Term 2</li></ol>",
    },
    css="""
    .contract { font-family: Georgia, serif; }
    .contract h1 { color: #2c3e50; }
    .terms { margin-top: 20px; }
    """,
)

doc.export_pdf("contract.pdf")

# Option 2: Template file (saved in templates/ directory)
doc = Document(
    title="Custom Report",
    template_file="my_custom_template.html",  # From templates/ directory
    data={"key": "value"},
)
```

### Adding Custom Templates

You can add custom templates in two ways:

1. **Via Directory**: Place `.html` files in the `templates/` directory
2. **Via Code**: Pass inline template string to the `template` parameter

---

## 📊 Reports

### Simplified API (Recommended)

```python
from reportpy import ReportBuilder

builder = (
    ReportBuilder("Weekly Sales Report", format_name="corporate")
    .header(title="Sales Report", subtitle="Week 48, 2026")
    .footer(
        left="My Company Ltd.",
        center="Confidential",  # Center section supported!
        right="Page 1"
    )
    .add_kpis("metrics", [
        {"label": "Revenue", "value": "£125K", "change": "+15%"},
        {"label": "Orders", "value": "1,234", "change": "+8%"},
        {"label": "Customers", "value": "892", "change": "+12%"},
    ])
    .add_table("sales_data",
        headers=["Product", "Units", "Revenue"],
        rows=[
            ["Product A", "150", "£15,000"],
            ["Product B", "230", "£23,000"],
            ["Product C", "180", "£18,000"],
        ],
        title="Sales by Product",
        footer_row=["Total", "560", "£56,000"],
    )
    .add_text("notes", """
        <p>Key observations:</p>
        <ul>
            <li>Product B shows strongest growth</li>
            <li>Customer acquisition up 12%</li>
        </ul>
    """)
)

# Export options
builder.export_html("report.html")
builder.export_pdf("report.pdf")
builder.preview()  # Open in browser

# Email-ready HTML
html_inline = builder.render_inline()  # Full HTML with inline styles
body_only = builder.to_clipboard_html()  # Returns body HTML as string (for email)
```

**Note**: The `to_clipboard_html()` method returns the HTML content as a string variable - it does not copy to clipboard.

---

### Full Control API

For complete control over multi-page reports:

```python
from reportpy import (
    Report, 
    Section, 
    TableSection, 
    KPISection, 
    TextSection,
    set_default_format
)

# Set global format
set_default_format("corporate")

# Create report
report = Report(title="Annual Report 2026")

# Page 1: Summary
page1 = report.add_page()
page1.set_header(title="Executive Summary", subtitle="Q1-Q4 2026")
page1.set_footer(left_text="Company Ltd.", center_text="Draft", right_text="Page 1")

page1.add_section(KPISection(
    name="annual_kpis",
    kpis=[
        {"label": "Total Revenue", "value": "£2.5M", "change": 18},
        {"label": "Net Profit", "value": "£450K", "change": 22},
        {"label": "Employees", "value": "125", "change": 15},
    ],
    title="Key Metrics",
))

# Page 2: Detailed Data
page2 = report.add_page()
page2.set_header(title="Financial Details")
page2.set_footer(left_text="Company Ltd.", right_text="Page 2")

page2.add_section(TableSection(
    name="quarterly_results",
    headers=["Quarter", "Revenue", "Expenses", "Profit"],
    rows=[
        ["Q1", "£580K", "£420K", "£160K"],
        ["Q2", "£620K", "£450K", "£170K"],
        ["Q3", "£650K", "£480K", "£170K"],
        ["Q4", "£700K", "£510K", "£190K"],
    ],
    title="Quarterly Results",
    footer_row=["Total", "£2.55M", "£1.86M", "£690K"],
))

# Page 3: Custom Section
page3 = report.add_page()
page3.set_header(title="Custom Analysis")

page3.add_section(Section(
    name="custom_chart",
    template="""
    <div class="chart-container">
        <h3>{{ chart_title }}</h3>
        <div class="chart">{{ chart_html | safe }}</div>
    </div>
    """,
    data={
        "chart_title": "Revenue Trend",
        "chart_html": "<img src='chart.png' alt='Chart'>",
    },
    css="""
    .chart-container { text-align: center; }
    .chart { margin: 20px auto; }
    """,
))

# Export
report.export_html("annual_report.html")
report.export_pdf("annual_report.pdf")
```

---

### Section Types

#### TableSection

```python
TableSection(
    name="my_table",
    headers=["Column 1", "Column 2", "Column 3"],
    rows=[
        ["Row 1, Col 1", "Row 1, Col 2", "Row 1, Col 3"],
        ["Row 2, Col 1", "Row 2, Col 2", "Row 2, Col 3"],
    ],
    title="Optional Table Title",
    footer_row=["Footer 1", "Footer 2", "Footer 3"],  # Optional
)
```

#### KPISection

```python
KPISection(
    name="my_kpis",
    kpis=[
        {"label": "Metric 1", "value": "100", "change": 10},    # +10%
        {"label": "Metric 2", "value": "£50K", "change": -5},   # -5%
        {"label": "Metric 3", "value": "99.9%", "change": "+2%"},  # String format
    ],
    title="Key Performance Indicators",
)
```

#### TextSection

```python
TextSection(
    name="my_text",
    content="<p>HTML content goes here.</p><ul><li>Item 1</li></ul>",
    title="Optional Title",
)
```

#### Section (Custom)

```python
Section(
    name="my_custom",
    template="<div class='custom'>{{ variable }}</div>",
    data={"variable": "Dynamic content"},
    css=".custom { color: blue; border: 1px solid #ccc; }",
)
```

---

## 🎨 Formats

Three predefined formats are available:

```python
from reportpy import set_default_format, get_available_formats

print(get_available_formats())  # ['corporate', 'default', 'minimal']

# Set globally
set_default_format("corporate")

# Or per-report
builder = ReportBuilder("Report", format_name="minimal")
```

| Format        | Description                                          |
| ------------- | ---------------------------------------------------- |
| `default`   | Clean, professional look with subtle colors          |
| `corporate` | Bold headers, structured layout for business reports |
| `minimal`   | Lightweight, minimal styling for simple reports      |

---

## 🔧 Advanced Features

### Corporate Branding (Logo & Colors)

Customize documents and reports with your corporate identity:

#### Adding Logo

For documents (invoices, quotes, etc.), include the logo in the company data:

```python
from reportpy import create_invoice

invoice = create_invoice(
    invoice_number="INV-2026-001",
    company={
        "name": "My Company Ltd.",
        "logo": "assets/logo.png",  # Path to your logo image
        # ... other company data
    },
    # ... rest of parameters
)
```

For reports, add the logo in the header:

```python
from reportpy import ReportBuilder

builder = ReportBuilder("Annual Report")
builder.header(
    title="Annual Report 2026",
    logo="assets/company-logo.png"
)
```

#### Custom Colors (CSS Variables)

Override CSS variables to change colors throughout the document:

```python
from reportpy import create_invoice, ReportBuilder

# Custom CSS to override default colors
corporate_css = """
:root {
    --primary-color: #e11d48;      /* Rose red - used for headers, accents */
    --secondary-color: #0ea5e9;    /* Sky blue */
    --text-color: #0f172a;         /* Dark slate - main text */
    --text-muted: #94a3b8;         /* Gray - secondary text */
    --border-color: #cbd5e1;       /* Light gray borders */
    --bg-light: #f1f5f9;           /* Light background for cards */
    --success-color: #22c55e;      /* Green for positive values */
    --warning-color: #eab308;      /* Yellow for warnings */
    --danger-color: #ef4444;       /* Red for negative values */
}
"""

# For documents
invoice = create_invoice(
    invoice_number="INV-2026-001",
    company={"name": "Brand Corp", "logo": "logo.png"},
    client={"name": "Client Inc"},
    items=[{"description": "Service", "quantity": 1, "unit_price": 100}],
    css=corporate_css,  # Apply custom styles
)

# For reports
builder = ReportBuilder("Branded Report")
builder.report.global_css = corporate_css
builder.header(title="Q4 Report", logo="brand-logo.png")
# ... add sections
builder.export_pdf("branded_report.pdf")
```

#### Available CSS Variables

| Variable              | Default     | Description                        |
| --------------------- | ----------- | ---------------------------------- |
| `--primary-color`   | `#2563eb` | Headers, titles, accents, borders  |
| `--secondary-color` | `#64748b` | Secondary elements                 |
| `--text-color`      | `#1e293b` | Main text color                    |
| `--text-muted`      | `#64748b` | Muted/secondary text               |
| `--border-color`    | `#e2e8f0` | Table borders, dividers            |
| `--bg-light`        | `#f8fafc` | Card backgrounds, alternating rows |
| `--success-color`   | `#16a34a` | Positive KPIs, success messages    |
| `--warning-color`   | `#ca8a04` | Warnings, pending status           |
| `--danger-color`    | `#dc2626` | Negative KPIs, errors              |

#### Complete Branding Example

```python
from reportpy import ReportBuilder, KPISection, TableSection

# Define brand colors
brand_css = """
:root {
    --primary-color: #7c3aed;   /* Purple brand */
    --text-color: #18181b;
    --bg-light: #faf5ff;
}

/* Additional custom styles */
.document-header h1 { letter-spacing: -0.5px; }
.kpi-value { font-weight: 800; }
"""

builder = (
    ReportBuilder("Brand Report")
    .header(title="Quarterly Results", subtitle="Q4 2026", logo="logo.png")
    .footer(left="© Brand Corp", center="Confidential", right="Page 1")
    .add_kpis("metrics", [
        {"label": "Revenue", "value": "£250K", "change": "+15%"},
        {"label": "Customers", "value": "1,240", "change": "+8%"},
    ])
)

builder.report.global_css = brand_css
builder.export_pdf("branded_report.pdf")
```

### Asset Management

Images are automatically converted to Base64 for portable HTML:

```python
# In templates
{{ asset('logo.png') }}  # Converts to data:image/png;base64,...
```

### Custom Jinja2 Filters

Available filters in templates:

```python
{{ amount | currency }}           # £1,234.56
{{ date | format_date }}          # 15 January 2026
{{ text | nl2br }}                # Converts \n to <br>
{{ now() }}                       # Current datetime
{{ now().strftime('%Y-%m-%d') }}  # Formatted date
```

### Pandas Integration

```python
import pandas as pd
from reportpy import ReportBuilder

df = pd.DataFrame({
    "Product": ["A", "B", "C"],
    "Sales": [100, 200, 150],
})

builder = ReportBuilder("Sales Report")
builder.add_table_from_dataframe("sales", df, title="Product Sales")
builder.export_pdf("report.pdf")
```

### Embedded Browser (WinFormPy Integration)

For desktop applications, you can embed reports in a WinFormPy window:

```bash
# Install with GUI support
pip install ninjareportpy[gui]
```

```python
from reportpy import Report, check_winformpy_available

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
from winformpy import Form, DockStyle, Application
from reportpy import create_invoice

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

viewer = InvoiceViewer()
Application.Run(viewer)
```

Available viewer functions:

| Function                                                           | Description                                 |
| ------------------------------------------------------------------ | ------------------------------------------- |
| `check_winformpy_available()`                                    | Check if WinFormPy is installed             |
| `create_embedded_browser(parent, props)`                         | Create basic WebBrowser control             |
| `create_browser_panel(parent, props)`                            | Create WebBrowserPanel with navigation bar  |
| `open_in_embedded_browser(parent, html, props, with_navigation)` | Create browser and display HTML in one call |

**BaseDocument methods:**

| Method                                                        | Description                          |
| ------------------------------------------------------------- | ------------------------------------ |
| `preview_embedded(parent, props, with_navigation)`          | Display document in embedded browser |
| `create_viewer_form(title, width, height, with_navigation)` | Create standalone viewer Form        |

---

## 🧪 Testing

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=reportpy

# Specific test file
uv run pytest tests/test_report.py -v
```

---

## 📁 Project Structure

```
ninjareportpy/
└── reportpy/
    ├── __init__.py      # Public API exports
    ├── base.py          # BaseDocument abstract class
    ├── document.py      # Document class + factory functions
    ├── report.py        # Report class (multi-page)
    ├── page.py          # Page class (header + footer + sections)
    ├── sections.py      # Section classes
    ├── builder.py       # ReportBuilder simplified API
    ├── config.py        # Configuration (PageSize, Orientation)
    ├── assets.py        # Asset management (Base64)
    ├── filters.py       # Custom Jinja2 filters
    ├── pdf.py           # PDF export via WeasyPrint
    ├── viewer.py        # Browser preview + WinFormPy integration
    ├── exceptions.py    # Custom exceptions
    ├── templates/       # HTML templates
    │   ├── base.html
    │   ├── invoice.html
    │   ├── quote.html
    │   ├── receipt.html
    │   └── delivery_note.html
    └── formats/         # Predefined formats
        ├── default/
        ├── corporate/
        └── minimal/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**DatamanEdge**

- GitHub: [@DatamanEdge](https://github.com/DatamanEdge)
