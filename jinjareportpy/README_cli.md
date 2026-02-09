# CLI Module

## Overview

Command-line interface for JinjaReportPy for managing configuration, generating demo reports,
creating documents (invoices, quotes), and listing available formats and templates.

## Installation

The module is included in the project. No additional dependencies required.

## Quick Start

```bash
# Show help
python -m jinjareportpy --help

# Show version
python -m jinjareportpy --version

# Show current configuration
python -m jinjareportpy config show

# Generate demo report
python -m jinjareportpy demo

# List available formats
python -m jinjareportpy formats
```

## Commands

### config

View and manage JinjaReportPy configuration.

#### config show

Show current configuration with resolved values.

```bash
# Human-readable output
python -m jinjareportpy config show

# JSON output
python -m jinjareportpy config show --json
```

**Options:**

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON format |

#### config set

Set a configuration value (session only).

```bash
# Set output directory
python -m jinjareportpy config set output_dir ./reports

# Set locale
python -m jinjareportpy config set locale en_US

# Set page size
python -m jinjareportpy config set page_size LETTER

# Set orientation
python -m jinjareportpy config set orientation landscape

# Set default format
python -m jinjareportpy config set default_format corporate
```

**Available Keys:**

| Key | Description | Example |
|-----|-------------|---------|
| `templates_dir` | Templates directory | `./my_templates` |
| `formats_dir` | Formats directory | `./my_formats` |
| `output_dir` | Output directory | `./reports` |
| `assets_dir` | Assets directory | `./assets` |
| `locale` | Locale for formatting | `en_US`, `es_ES` |
| `page_size` | Page size | `A4`, `A3`, `LETTER`, `LEGAL` |
| `orientation` | Page orientation | `portrait`, `landscape` |
| `default_format` | Default report format | `default`, `corporate`, `minimal` |
| `pdf_zoom` | PDF zoom level | `1.0`, `1.5` |
| `pdf_optimize_images` | Optimize PDF images | `true`, `false` |

#### config reset

Reset all configuration to default values.

```bash
python -m jinjareportpy config reset
```

#### config init

Create a configuration file in the current directory.

```bash
# Create config file
python -m jinjareportpy config init

# Overwrite existing file
python -m jinjareportpy config init --force
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Overwrite existing config file |

### demo

Generate a demo sales report to test the library.

```bash
# Default format
python -m jinjareportpy demo

# Corporate format
python -m jinjareportpy demo --format corporate

# Minimal format with custom output
python -m jinjareportpy demo --format minimal --output my_report

# Generate PDF and open in browser
python -m jinjareportpy demo --pdf --open

# All options combined
python -m jinjareportpy demo -f corporate -o quarterly_report --pdf --open
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--format` | `-f` | Report format: `default`, `corporate`, `minimal` |
| `--output` | `-o` | Output filename (without extension) |
| `--pdf` | | Also generate PDF output |
| `--open` | | Open in browser after generation |

### formats

List available report formats.

```bash
# Simple list
python -m jinjareportpy formats

# With file details
python -m jinjareportpy formats --details
```

**Options:**

| Option | Description |
|--------|-------------|
| `--details` | Show format files (HTML, CSS) |

### templates

List available document templates.

```bash
python -m jinjareportpy templates
```

### invoice

Generate an invoice document.

```bash
# Basic invoice
python -m jinjareportpy invoice --number INV-2026-001

# With company and client
python -m jinjareportpy invoice -n INV-2026-001 --company "My Company Ltd." --client "Client Corp."

# Export as PDF
python -m jinjareportpy invoice -n INV-2026-001 --pdf

# Custom output and open
python -m jinjareportpy invoice -n INV-2026-001 -o my_invoice --open
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--number` | `-n` | Invoice number (required) |
| `--company` | | Company name (default: "My Company Ltd.") |
| `--client` | | Client name (default: "Client Corp.") |
| `--output` | `-o` | Output filename |
| `--pdf` | | Export as PDF |
| `--open` | | Open after generation |

### quote

Generate a quote document.

```bash
# Basic quote
python -m jinjareportpy quote --number QT-2026-001

# With company and client
python -m jinjareportpy quote -n QT-2026-001 --company "My Company" --client "Client Inc."

# Export as PDF
python -m jinjareportpy quote -n QT-2026-001 --pdf
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--number` | `-n` | Quote number (required) |
| `--company` | | Company name (default: "My Company Ltd.") |
| `--client` | | Client name (default: "Client Corp.") |
| `--output` | `-o` | Output filename |
| `--pdf` | | Export as PDF |

## Global Options

Available for all commands:

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-V` | Show version |
| `--verbose` | `-v` | Enable verbose output |

## Examples

### Complete Workflow

```bash
# 1. Initialize configuration
python -m jinjareportpy config init

# 2. Customize settings
python -m jinjareportpy config set output_dir ./reports
python -m jinjareportpy config set locale en_US
python -m jinjareportpy config set default_format corporate

# 3. Verify configuration
python -m jinjareportpy config show

# 4. Generate demo report
python -m jinjareportpy demo --pdf --open

# 5. Create an invoice
python -m jinjareportpy invoice -n INV-2026-001 --company "Acme Corp" --client "Client Ltd" --pdf
```

### Using Environment Variables

```bash
# Set configuration via environment
export JINJAREPORT_OUTPUT_DIR="./my_reports"
export JINJAREPORT_LOCALE="en_US"
export JINJAREPORT_DEFAULT_FORMAT="corporate"

# CLI uses these values automatically
python -m jinjareportpy demo
python -m jinjareportpy invoice -n INV-001
```

### Batch Document Generation

```bash
# Generate multiple invoices
for i in {001..005}; do
    python -m jinjareportpy invoice -n "INV-2026-$i" --pdf
done

# Or with PowerShell
1..5 | ForEach-Object { 
    python -m jinjareportpy invoice -n "INV-2026-$($_.ToString('000'))" --pdf 
}
```

## Integration with Config Module

The CLI integrates with the configuration module for centralized settings management.

### Priority Resolution

Values are resolved in order (first match wins):

1. **CLI arguments** - Explicit flags always win
2. **Environment variables** - `JINJAREPORT_*` variables
3. **Configuration file** - `jinjareportpy.toml`
4. **Built-in defaults** - Hard-coded fallback values

### Configuration Persistence

| Method | Persistence | Use Case |
|--------|-------------|----------|
| CLI `config set` | Session only | Quick testing |
| Config file | Permanent | Project-level settings |
| Environment | Shell session | CI/CD, system-wide |

### Config + CLI Example

```python
from jinjareportpy import JinjaReportConfig, ReportBuilder

# Load configuration (auto-discovers jinjareportpy.toml)
config = JinjaReportConfig.get_all_config()

# Use resolved settings
builder = (
    ReportBuilder("My Report", format_name=config['default_format'])
    .header(title="Report")
    .add_text("content", "Generated with CLI configuration")
)

# Export to configured output directory
builder.export_html("report.html")
```

For full configuration documentation, see [README_config.md](README_config.md).

## Programmatic Usage

```python
from jinjareportpy.cli import main, get_parser

# Run CLI programmatically
exit_code = main(['demo', '--format', 'corporate', '--pdf'])

# Get parser for custom extensions
parser = get_parser()
args = parser.parse_args(['config', 'show', '--json'])
```

## API Reference

### Functions

| Function | Description |
|----------|-------------|
| `main(argv)` | Main CLI entry point, returns exit code |
| `get_parser()` | Get configured ArgumentParser |
| `cmd_config_show(args)` | Show configuration |
| `cmd_config_set(args)` | Set configuration value |
| `cmd_config_reset(args)` | Reset configuration |
| `cmd_config_init(args)` | Create config file |
| `cmd_demo(args)` | Generate demo report |
| `cmd_formats(args)` | List formats |
| `cmd_templates(args)` | List templates |
| `cmd_invoice(args)` | Generate invoice |
| `cmd_quote(args)` | Generate quote |
