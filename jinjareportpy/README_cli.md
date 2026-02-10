# CLI Module

## Overview

Command-line interface for JinjaReportPy with **colored output**, multiple
verbosity levels, and commands for managing configuration, generating demo
reports, creating documents (invoices, quotes, receipts, delivery notes), and
listing available formats and templates.

## Installation

The module is included in the project. No additional dependencies required.

For Windows color support without native ANSI codes: `pip install colorama`

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

# Generate demo with corporate format, PDF export, and open in browser
python -m jinjareportpy demo --format corporate --pdf --open

# List available formats
python -m jinjareportpy formats

# Create an invoice
python -m jinjareportpy invoice -n INV-2026-001 --company "Acme Corp"

# Create a receipt
python -m jinjareportpy receipt -n REC-001 --amount 1500.00

# Create a delivery note
python -m jinjareportpy delivery -n DN-001 --pdf
```

## Global Options

Available for all commands:

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-V` | Show version and exit |
| `--verbose` | `-v` | Increase verbosity (`-v` = INFO, `-vv` = DEBUG) |
| `--quiet` | `-q` | Suppress non-error output |
| `--no-color` | | Disable colored output |

## Commands

### config

View and manage JinjaReportPy configuration.

#### config show

Show current configuration with resolved values.

```bash
# Human-readable output (colored)
python -m jinjareportpy config show

# JSON output (for scripting)
python -m jinjareportpy config show --json
```

| Option | Description |
|--------|-------------|
| `--json` | Output configuration as JSON |

#### config set

Set a configuration value (session only — not persisted).

```bash
python -m jinjareportpy config set output_dir ./reports
python -m jinjareportpy config set locale en_US
python -m jinjareportpy config set page_size LETTER
python -m jinjareportpy config set orientation landscape
python -m jinjareportpy config set default_format corporate
python -m jinjareportpy config set pdf_zoom 1.5
python -m jinjareportpy config set pdf_optimize_images true
```

**Available Keys:**

| Key | Description | Example Values |
|-----|-------------|----------------|
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

Create a `jinjareportpy.toml` configuration file in the current directory.

```bash
python -m jinjareportpy config init
python -m jinjareportpy config init --force   # overwrite existing
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Overwrite existing config file |

### demo

Generate a demo sales report (2 pages with KPIs, tables, and notes).

```bash
python -m jinjareportpy demo
python -m jinjareportpy demo --format corporate
python -m jinjareportpy demo --format minimal --output my_report
python -m jinjareportpy demo --pdf --open
python -m jinjareportpy demo -f corporate -o quarterly_report --pdf --open
```

| Option | Short | Description |
|--------|-------|-------------|
| `--format` | `-f` | Report format: `default`, `corporate`, `minimal` |
| `--output` | `-o` | Output filename (without extension) |
| `--pdf` | | Also generate PDF output |
| `--open` | | Open in browser after generation |

After execution a summary with page count, section count, format used, and
elapsed time is printed.

### formats

List available report formats.

```bash
python -m jinjareportpy formats
python -m jinjareportpy formats --details
```

| Option | Description |
|--------|-------------|
| `--details` | Show individual format files with sizes |

Without `--details`, formats are displayed in a table with file counts.

### templates

List available document templates.

```bash
python -m jinjareportpy templates
```

Templates are shown in a table with their file sizes.

### invoice

Generate an invoice document.

```bash
python -m jinjareportpy invoice -n INV-2026-001
python -m jinjareportpy invoice -n INV-2026-001 --company "Acme Corp" --client "Client Ltd."
python -m jinjareportpy invoice -n INV-2026-001 --pdf --open
python -m jinjareportpy invoice -n INV-2026-001 -o my_invoice
```

### quote

Generate a quote document.

```bash
python -m jinjareportpy quote -n QT-2026-001
python -m jinjareportpy quote -n QT-2026-001 --validity 60 --pdf
```

| Extra Option | Description |
|--------------|-------------|
| `--validity` | Validity in days (default: 30) |

### receipt

Generate a receipt document.

```bash
python -m jinjareportpy receipt -n REC-2026-001
python -m jinjareportpy receipt -n REC-2026-001 --amount 1500.00 --concept "Invoice INV-2025-089"
python -m jinjareportpy receipt -n REC-2026-001 --pdf --open
```

| Extra Option | Description |
|--------------|-------------|
| `--amount` | Receipt amount (default: 0.00) |
| `--concept` | Payment concept (default: "Payment received") |

### delivery

Generate a delivery note document.

```bash
python -m jinjareportpy delivery -n DN-2026-001
python -m jinjareportpy delivery -n DN-2026-001 --company "Warehouse Inc." --pdf
```

### Common Document Options

All document commands (`invoice`, `quote`, `receipt`, `delivery`) share:

| Option | Short | Description |
|--------|-------|-------------|
| `--number` | `-n` | Document number (required) |
| `--company` | | Company name (default: "My Company Ltd.") |
| `--client` | | Client name (default: "Client Corp.") |
| `--output` | `-o` | Output filename (without extension) |
| `--pdf` | | Export as PDF (falls back to HTML on error) |
| `--open` | | Open in browser after generation |

## Colored Output Utilities

The CLI includes colored output helpers that can also be used programmatically:

```python
from jinjareportpy.cli import (
    Colors,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    print_table,
    print_summary,
)

# Colored messages
print_success("Operation completed")   # ✓ Green
print_error("Something failed")        # ✗ Red (stderr)
print_warning("Be careful")            # ⚠ Yellow
print_info("FYI message")              # ℹ Cyan

# Formatted header
print_header("Section Title")

# ASCII table
print_table(
    headers=["Name", "Status", "Count"],
    rows=[["Users", "Active", 150], ["Groups", "Synced", 25]],
)

# Summary statistics
print_summary(
    {"processed": 100, "success": 95, "errors": 5},
    title="RESULTS",
)

# Disable all colors
Colors.disable()
```

### Colors Class

Colors are auto-initialized on import with Windows ANSI support. Falls back to
`colorama` if available, otherwise disables colors automatically.

| Attribute | Description |
|-----------|-------------|
| `Colors.RESET` | Reset terminal formatting |
| `Colors.BOLD` | Bold text |
| `Colors.RED` / `ERROR` | Red (errors) |
| `Colors.GREEN` / `SUCCESS` | Green (success) |
| `Colors.YELLOW` / `WARNING` | Yellow (warnings) |
| `Colors.CYAN` / `INFO` | Cyan (info) |
| `Colors.GRAY` / `MUTED` | Gray (secondary text) |

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

# 5. Create documents
python -m jinjareportpy invoice -n INV-2026-001 --company "Acme" --pdf
python -m jinjareportpy receipt -n REC-2026-001 --amount 5000 --pdf
python -m jinjareportpy delivery -n DN-2026-001 --pdf
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
# Bash
for i in {001..005}; do
    python -m jinjareportpy invoice -n "INV-2026-$i" --pdf
done

# PowerShell
1..5 | ForEach-Object {
    python -m jinjareportpy invoice -n "INV-2026-$($_.ToString('000'))" --pdf
}
```

### Quiet Mode & No Color (CI/CD)

```bash
# Suppress non-error output
python -m jinjareportpy -q demo --pdf

# Disable colors for log files
python -m jinjareportpy --no-color demo --pdf 2>&1 | tee build.log

# Debug verbosity
python -m jinjareportpy -vv demo
```

## CI/CD Pipeline Integration

JinjaReportPy is designed to run headless in CI/CD environments. Key features:

| Feature | Flag / Env Var | Purpose |
|---------|---------------|---------|
| Quiet mode | `--quiet` / `-q` | Suppress non-error output |
| No colors | `--no-color` | Clean log output (no ANSI escapes) |
| Dry run | `--dry-run` | Simulate without writing files |
| Log to file | `--log-file build.log` | Persist logs for archival |
| JSON output | `--output-format json` | Machine-readable output |
| Exit codes | `exit_with_error()` / `exit_success()` | Proper exit codes for CI |
| Env config | `JINJAREPORT_*` | Configure via environment variables |

### Jenkins

A complete Jenkinsfile is provided at `examples/Jenkinsfile` with:

- Parameterized builds (format, page size, orientation, locale, PDF toggle)
- Environment configuration via `JINJAREPORT_*` variables
- Stages: Setup → Lint → Test (JUnit + coverage) → Generate Documents → Verify
- Artifact archival and workspace cleanup

```groovy
// Jenkinsfile excerpt — see examples/Jenkinsfile for the full pipeline
pipeline {
    agent any
    environment {
        JINJAREPORT_OUTPUT_DIR     = "${WORKSPACE}/reports"
        JINJAREPORT_DEFAULT_FORMAT = "${params.REPORT_FORMAT}"
        JINJAREPORT_LOCALE         = "${params.LOCALE}"
    }
    stages {
        stage('Test') {
            steps {
                sh '''
                    uv run pytest tests/ -v --no-color \
                        --junitxml=reports/junit-results.xml
                '''
            }
            post { always { junit 'reports/junit-results.xml' } }
        }
        stage('Generate') {
            steps {
                sh 'uv run python -m jinjareportpy --no-color -q demo --pdf'
            }
        }
    }
    post {
        success {
            archiveArtifacts artifacts: 'reports/**', fingerprint: true
        }
    }
}
```

### GitHub Actions

```yaml
# .github/workflows/reports.yml
name: Generate Reports
on: [push, workflow_dispatch]

jobs:
  reports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run tests
        run: uv run pytest tests/ -v --no-color --junitxml=reports/junit.xml

      - name: Generate documents
        env:
          JINJAREPORT_OUTPUT_DIR: ./reports
          JINJAREPORT_DEFAULT_FORMAT: corporate
          JINJAREPORT_LOCALE: en_US
        run: |
          uv run python -m jinjareportpy --no-color -q demo --pdf
          uv run python -m jinjareportpy --no-color -q invoice -n INV-001 --pdf
          uv run python -m jinjareportpy --no-color -q receipt -n REC-001 --amount 5000 --pdf

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: generated-reports
          path: reports/
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - generate

variables:
  JINJAREPORT_OUTPUT_DIR: ./reports
  JINJAREPORT_DEFAULT_FORMAT: corporate

test:
  stage: test
  image: python:3.13
  script:
    - pip install uv && uv sync
    - uv run pytest tests/ -v --no-color --junitxml=reports/junit.xml
  artifacts:
    reports:
      junit: reports/junit.xml

generate:
  stage: generate
  image: python:3.13
  script:
    - pip install uv && uv sync
    - uv run python -m jinjareportpy --no-color -q demo --pdf
    - uv run python -m jinjareportpy --no-color -q invoice -n INV-001 --pdf
  artifacts:
    paths:
      - reports/
```

## Integration with Config Module

### Priority Resolution

Values are resolved in order (first match wins):

1. **CLI arguments** — Explicit flags always win
2. **Environment variables** — `JINJAREPORT_*` variables
3. **Configuration file** — `jinjareportpy.toml`
4. **Built-in defaults** — Hard-coded fallback values

### Configuration Persistence

| Method | Persistence | Use Case |
|--------|-------------|----------|
| CLI `config set` | Session only | Quick testing |
| Config file | Permanent | Project-level settings |
| Environment | Shell session | CI/CD, system-wide |

## Programmatic Usage

```python
from jinjareportpy.cli import main, get_parser

# Run CLI programmatically
exit_code = main(["demo", "--format", "corporate", "--pdf"])

# Get parser for custom extensions
parser = get_parser()
args = parser.parse_args(["config", "show", "--json"])
```

## Reusable CLI Base Class

`CLIBase` is a generic, reusable class for building CLI applications. It
provides subcommand support, argument groups for common patterns (database,
LDAP, API connections; export, import, sync operations), statistics tracking,
and colored output — all independent of JinjaReportPy.

### Basic Usage (No Subcommands)

```python
from jinjareportpy.cli import CLIBase

cli = CLIBase(prog="mytool", description="My data tool", version="2.0.0")
cli.add_export_group(formats=["csv", "json", "parquet"])
args = cli.parse_args()

# ... your logic ...
cli.increment_stat("processed", 100)
cli.increment_stat("errors", 3)
cli.print_final_summary()
```

### Subcommand Pattern

```python
from jinjareportpy.cli import CLIBase, print_success

def handle_fetch(args, cli):
    print_success(f"Fetching from {args.source}...")
    cli.increment_stat("fetched", 42)

def handle_push(args, cli):
    print_success(f"Pushing to {args.target}...")
    cli.increment_stat("pushed", 42)

cli = CLIBase(prog="sync", description="Data synchronizer", version="1.0.0")
cli.init_subcommands()

fetch_cmd = cli.add_subcommand("fetch", "Fetch data", handler=handle_fetch, aliases=["f"])
fetch_cmd.add_argument("--source", "-s", required=True, help="Source URL")

push_cmd = cli.add_subcommand("push", "Push data", handler=handle_push, aliases=["p"])
push_cmd.add_argument("--target", "-t", required=True, help="Target URL")

args = cli.parse_args()
cli.run()
cli.print_final_summary()
```

### Factory Function

`create_cli()` is a shortcut that creates a `CLIBase` with connection and
operation argument groups pre-configured:

```python
from jinjareportpy.cli import create_cli

# Database export tool
cli = create_cli(
    prog="dbexport",
    description="Export database tables",
    version="1.0.0",
    connection_type="database",
    operation_type="export",
)
args = cli.parse_args()
```

### Connection Groups

| Method | Arguments Added |
|--------|----------------|
| `add_database_connection_group()` | `--db-type`, `--db-host`, `--db-port`, `--db-name`, `--db-user`, `--db-password`, `--db-password-file` |
| `add_ldap_connection_group()` | `--host`, `--user`, `--password`, `--password-file`, `--base-dn`, `--no-ssl`, `--auth-method` |
| `add_api_connection_group()` | `--api-url`, `--api-key`, `--api-key-file`, `--client-id`, `--client-secret`, `--token`, `--timeout` |

### Operation Groups

| Method | Arguments Added |
|--------|----------------|
| `add_export_group(formats)` | `--format`, `--output`, `--filter`, `--select-fields`, `--limit` |
| `add_import_group(formats)` | `--source`, `--format`, `--skip-validation`, `--update-existing`, `--batch-size` |
| `add_sync_group()` | `--source`, `--target`, `--mode`, `--conflict-resolution` |

### CLIConfig Dataclass

Override defaults by passing a `CLIConfig` instance:

```python
from jinjareportpy.cli import CLIBase, CLIConfig, OutputFormat, LogLevel

config = CLIConfig(
    prog_name="mytool",
    version="2.0.0",
    description="My advanced tool",
    default_output_format=OutputFormat.JSON,
    default_log_level=LogLevel.DEBUG,
    require_confirmation=True,
    dry_run_by_default=True,
    default_timeout=60,
)

cli = CLIBase(config=config)
```

### Subcommand Dataclass

Each registered subcommand is stored as a `Subcommand` instance:

```python
from jinjareportpy.cli import Subcommand

# Inspect registered subcommands
for name, sub in cli._subcommands.items():
    print(f"{sub.name}: {sub.help} (aliases={sub.aliases})")
```

### Enums

```python
from jinjareportpy.cli import OutputFormat, LogLevel

# OutputFormat: TABLE, JSON, CSV, SUMMARY, QUIET
# LogLevel: DEBUG, INFO, WARNING, ERROR, QUIET
```

## Additional Output Utilities

### print_progress

In-place progress bar for loops:

```python
from jinjareportpy.cli import print_progress

items = range(100)
for i, item in enumerate(items):
    print_progress(i + 1, len(items), prefix="Processing", suffix="done")
```

### confirm_action

Interactive confirmation prompt:

```python
from jinjareportpy.cli import confirm_action

if confirm_action("Delete all records?", default=False):
    print("Deleting...")
else:
    print("Aborted.")
```

### cprint

Public colored print helper (same as internal `_cprint`):

```python
from jinjareportpy.cli import cprint, Colors

cprint("Bold red message", Colors.RED, bold=True)
cprint("Muted text", Colors.MUTED)
```

## API Reference

### Functions

| Function | Description |
|----------|-------------|
| `main(argv)` | Main CLI entry point, returns exit code |
| `get_parser()` | Get configured `ArgumentParser` |
| `create_cli(prog, description, ...)` | Factory for `CLIBase` instances |
| `cmd_config_show(args)` | Show configuration |
| `cmd_config_set(args)` | Set configuration value |
| `cmd_config_reset(args)` | Reset configuration |
| `cmd_config_init(args)` | Create config file |
| `cmd_demo(args)` | Generate demo report |
| `cmd_formats(args)` | List formats |
| `cmd_templates(args)` | List templates |
| `cmd_invoice(args)` | Generate invoice |
| `cmd_quote(args)` | Generate quote |
| `cmd_receipt(args)` | Generate receipt |
| `cmd_delivery(args)` | Generate delivery note |

### Classes

| Class | Description |
|-------|-------------|
| `CLIBase` | Reusable base class for CLI applications |
| `CLIConfig` | Dataclass for CLI configuration |
| `Subcommand` | Dataclass for subcommand definitions |
| `Colors` | ANSI color constants with Windows support |

### Enums

| Enum | Values |
|------|--------|
| `OutputFormat` | `TABLE`, `JSON`, `CSV`, `SUMMARY`, `QUIET` |
| `LogLevel` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `QUIET` |

### Output Utilities

| Function | Description |
|----------|-------------|
| `cprint(msg, color, bold, file)` | Print with color and formatting |
| `print_success(msg)` | Green checkmark message |
| `print_error(msg)` | Red X message (stderr) |
| `print_warning(msg)` | Yellow warning message |
| `print_info(msg)` | Cyan info message |
| `print_header(title)` | Formatted section header |
| `print_table(headers, rows)` | ASCII table output |
| `print_summary(stats, title)` | Key-value summary block |
| `print_progress(cur, total, ...)` | In-place progress bar |
| `confirm_action(msg, default)` | Interactive confirmation |

For full configuration documentation, see [README_config.md](README_config.md).
