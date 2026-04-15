# Features

Complete feature list for JinjaReportPy v0.1.0.

## Document Generation

| Feature | Module | Function / Class |
|---------|--------|------------------|
| Invoice generation | `document.py` | `create_invoice()` |
| Quote generation | `document.py` | `create_quote()` |
| Receipt generation | `document.py` | `create_receipt()` |
| Delivery note generation | `document.py` | `create_delivery_note()` |
| Custom documents (inline template) | `document.py` | `Document(template=...)` |
| Custom documents (template file) | `document.py` | `Document(template_file=...)` |
| Automatic calculations (subtotal, tax, total) | `document.py` | `InvoiceData`, `QuoteData` |
| Data classes for structured input | `document.py` | `PartyInfo`, `InvoiceData`, `QuoteData`, `ReceiptData`, `DeliveryNoteData` |

## Multi-Page Reports

| Feature | Module | Function / Class |
|---------|--------|------------------|
| Multi-page report creation | `report.py` | `Report` |
| Page management | `page.py` | `Page` |
| Header sections | `sections.py` | `HeaderSection` |
| Footer sections | `sections.py` | `FooterSection` |
| Table sections | `sections.py` | `TableSection` |
| KPI sections | `sections.py` | `KPISection` |
| Text sections | `sections.py` | `TextSection` |
| Custom sections (template + data + CSS) | `sections.py` | `Section` |

## Builder API (Fluent Interface)

| Feature | Module | Function / Class |
|---------|--------|------------------|
| Fluent report builder | `builder.py` | `ReportBuilder` |
| Quick report from data + layout | `builder.py` | `quick_report()` |
| Header/footer configuration | `builder.py` | `HeaderConfig`, `FooterConfig` |
| Table/KPI/text configuration | `builder.py` | `TableConfig`, `KPIConfig`, `TextConfig` |
| Page/report layout definitions | `builder.py` | `PageLayout`, `ReportLayout` |

## Export & Preview

| Feature | Module | Function / Class |
|---------|--------|------------------|
| HTML export | `base.py` | `BaseDocument.export_html()` |
| PDF export (via WeasyPrint) | `pdf.py` | `html_to_pdf()` |
| Email-ready inline HTML | `builder.py` | `ReportBuilder.render_inline()` |
| Body-only HTML for email | `builder.py` | `ReportBuilder.to_clipboard_html()` |
| Browser preview | `viewer.py` | `open_in_browser()` |
| PDF viewer | `viewer.py` | `open_pdf_viewer()` |
| Embedded GUI viewer (tkinterweb) | `viewer.py` | `open_in_embedded_browser()` |

## Predefined Formats

| Format | Directory | Description |
|--------|-----------|-------------|
| `default` | `formats/default/` | Clean, professional look with subtle colors |
| `corporate` | `formats/corporate/` | Bold headers, structured layout for business reports |
| `minimal` | `formats/minimal/` | Lightweight, minimal styling for simple reports |

Each format includes templates and CSS for: header, footer, section, table, kpi, text.

## Configuration

| Feature | Module | Function / Class |
|---------|--------|------------------|
| Centralized config management | `config.py` | `JinjaReportConfig` |
| TOML config file support | `config.py` | `jinjareportpy.toml` |
| Environment variable overrides (`JINJAREPORT_*`) | `config.py` | `JinjaReportConfig` |
| Per-export `ReportConfig` | `config.py` | `ReportConfig` |
| Page size (A4, A3, LETTER, LEGAL) | `config.py` | `PageSize` |
| Orientation (portrait, landscape) | `config.py` | `Orientation` |
| Templates directory | `config.py` | `get_templates_dir()`, `set_templates_dir()` |
| Formats directory | `config.py` | `get_formats_dir()`, `set_formats_dir()` |
| Output directory | `config.py` | `get_output_dir()`, `set_output_dir()` |
| Assets directory | `config.py` | `get_assets_dir()`, `set_assets_dir()` |
| Locale-based formatting | `config.py` | `get_locale()`, `set_locale()` |
| Page size configuration | `config.py` | `get_page_size()`, `set_page_size()` |
| Orientation configuration | `config.py` | `get_orientation()`, `set_orientation()` |

## Format Management

| Feature | Module | Function / Class |
|---------|--------|------------------|
| Set default format | `formats/__init__.py` | `set_default_format()` |
| Get current default format | `formats/__init__.py` | `get_default_format()` |
| List available formats | `formats/__init__.py` | `get_available_formats()` |

## CLI Interface

| Command | Module | Description |
|---------|--------|-------------|
| `config show` | `cli/commands.py` | Show current configuration |
| `config set <key> <value>` | `cli/commands.py` | Set configuration value |
| `config reset` | `cli/commands.py` | Reset to defaults |
| `config init` | `cli/commands.py` | Create `jinjareportpy.toml` |
| `demo` | `cli/commands.py` | Generate demo report |
| `formats` | `cli/commands.py` | List available formats |
| `templates` | `cli/commands.py` | List available templates |
| `invoice` | `cli/commands.py` | Generate invoice |
| `quote` | `cli/commands.py` | Generate quote |
| `receipt` | `cli/commands.py` | Generate receipt |
| `delivery` | `cli/commands.py` | Generate delivery note |

### CLI Framework

| Feature | Module | Function / Class |
|---------|--------|------------------|
| Reusable CLI base class | `cli/base.py` | `CLIBase` |
| CLI configuration dataclass | `cli/base.py` | `CLIConfig` |
| Subcommand registration | `cli/base.py` | `Subcommand` |
| Factory function | `cli/base.py` | `create_cli()` |
| Colored terminal output | `cli/output.py` | `Colors`, `cprint`, `print_success`, `print_error`, `print_warning` |
| Table formatting | `cli/output.py` | `print_table()` |
| Summary display | `cli/output.py` | `print_summary()` |
| Progress indicator | `cli/output.py` | `print_progress()` |
| `--no-color`, `-q`, `-v`, `-vv` flags | `cli/commands.py` | Global options |

## Utilities

| Feature | Module | Function / Class |
|---------|--------|------------------|
| Asset management (Base64 conversion) | `assets.py` | `AssetManager` |
| CSS reading and embedding | `assets.py` | `AssetManager.read_css()`, `AssetManager.embed_css()` |
| Jinja2 custom filters (currency, dates, numbers) | `filters.py` | `register_default_filters()` |
| WeasyPrint availability check | `pdf.py` | `check_weasyprint_available()` |

## Exceptions

| Exception | Module | Description |
|-----------|--------|-------------|
| `JinjaReportError` | `exceptions.py` | Base exception for all library errors |
| `TemplateNotFoundError` | `exceptions.py` | Template file not found |
| `AssetNotFoundError` | `exceptions.py` | Asset file not found |
| `ExportError` | `exceptions.py` | Export operation failed |

## Optional Dependencies

| Extra | Package | Feature |
|-------|---------|---------|
| `pdf` | WeasyPrint ≥60.0 | PDF export |
| `pandas` | Pandas ≥2.0.0 | DataFrame integration |
| `gui` | tkinterweb ≥3.0.0 | Embedded GUI viewer |
| `all` | All of the above | Full installation |