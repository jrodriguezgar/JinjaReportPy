# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `ChartSection`: New section type that renders matplotlib Figures as inline SVG in reports
- `ReportBuilder.add_chart()`: Fluent method to add matplotlib charts to reports
- `pyproject.toml`: New optional dependency group `charts` (`matplotlib>=3.7.0`)
- Chart format templates (`chart.html` + `chart.css`) for default, corporate, and minimal formats
- `FEATURES.md`: Add "Integration with OfficeBridge" section documenting HTML → Word/PDF/Markdown/Text/Excel conversion
- `llms.txt`: Add OfficeBridge integration section with conversion table and quick-reference code snippet
- `README.md`: Add "Integration with OfficeBridge" section with usage examples for DocumentConverter and ExcelClient

---

## [0.2.0] — 2026-04-15

Open-source readiness release — community files, CI/CD, security hardening, lint cleanup, and packaging configuration.

### Added
- `LICENSE` — MIT license file
- `FEATURES.md` — Complete feature inventory cross-referenced to modules and public API
- `CHANGELOG.md` — Keep a Changelog format with full release history
- `CONTRIBUTING.md` — Fork → Branch → Commit → PR contribution guide
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1
- `SECURITY.md` — Vulnerability reporting policy via GitHub Security Advisories
- `.github/workflows/ci.yml` — CI matrix (Python 3.10–3.13) with lint + test
- `.github/workflows/publish.yml` — PyPI trusted publisher on GitHub release
- `.github/ISSUE_TEMPLATE/` — Bug report and feature request templates
- `.github/PULL_REQUEST_TEMPLATE.md` — Pull request template
- `jinjareportpy/viewer.py` — Add `check_winformpy_available()` and `open_in_embedded_browser()` functions
- `pyproject.toml` — Add `[project.urls]` section with Homepage, Repository, and Issues links
- `pyproject.toml` — Configure `force-include` for wheel and sdist: ship `examples/`, exclude `tests/`
- `llms.txt` — Add GUI Viewer (`tkinterweb`) dependency, `report.html` template, `JINJAREPORT_PDF_OPTIMIZE_IMAGES` env var, CLI `jinjareportpy` alias, `config init --force`, and `quote`/`receipt`/`delivery` CLI commands

### Changed
- `README.md` — Update author from DatamanEdge to jrodriguezgar with repository link
- `README.md` — Add global CLI options table, add `receipt` and `delivery` to Available Commands table, add receipt/delivery/quote examples in Document Generation section
- `jinjareportpy/README_cli.md` — Add full CLIBase methods table to API Reference
- `llms.txt` — Expand CLI Utilities section with CLIBase methods table, CLI commands table, and global options table
- `llms.txt` — Update Python version range to 3.10–3.13

### Fixed
- `.gitignore` — Remove `pyproject.toml`, `tests/`, `docs/`, `examples/`, `notebooks/` from ignore list (were blocking essential project files)
- `.gitignore` — Add missing `**/*credential*` and `**/apikey*` security patterns
- `CONTRIBUTING.md` — Fix broken code fences (`` `ash `` → `` ```bash ``)
- `jinjareportpy/assets.py` — Reject Unix-style absolute paths (`/etc/passwd`) on Windows in `find_asset()`
- `jinjareportpy/cli/commands.py` — Add missing imports (`JinjaReportConfig`, `sys`, factory functions, format helpers) — fixes 21 undefined-name errors (F821)
- `jinjareportpy/__init__.py` — Add `get_assets_dir`, `set_assets_dir`, `get_locale`, `set_locale`, `get_page_size`, `set_page_size`, `get_orientation`, `set_orientation` to `__all__`
- `jinjareportpy/builder.py` — Remove unused imports (`HeaderSection`, `FooterSection`) and unused variable `css_content`
- `jinjareportpy/document.py` — Remove unused import `ReportConfig`
- `jinjareportpy/formats/__init__.py` — Remove unused import `Path`
- `jinjareportpy/pdf.py` — Remove unused `TYPE_CHECKING` block (`HTML`, `CSS`)
- `jinjareportpy/cli/base.py` — Remove unused import `cprint`
- All files — Fix 381 blank-line-with-whitespace (W293), 29 unsorted-imports (I001), 6 trailing-whitespace (W291), 5 f-string-missing-placeholders (F541), 15 line-too-long (E501) issues
- `llms.txt` — Add missing `check_weasyprint_available` symbol
- `FEATURES.md` — Expand configuration section with all 15 getter/setter functions and format management functions

### Removed
- `.github/copilot-instructions.md` — Remove legacy project instructions file (−531 lines)

---

## [0.1.0] — 2026-02-11

Initial public release of JinjaReportPy — programmatic document and report generator with dynamic sections, custom CSS, Jinja2 templates, and PDF export.

---

### `e1b37d0` — cli module improvement (2026-02-11)

Rewrite CLI module with colored output, verbosity levels, CI/CD integration patterns (Jenkins, GitHub Actions, GitLab CI), `CLIBase` reusable framework, and expanded document commands.

**3 files changed** | +1901 −450 lines

#### Added
- `jinjareportpy/cli.py` — `CLIBase` reusable framework, `CLIConfig`/`Subcommand` dataclasses, `Colors`/`cprint`/`print_success`/`print_error`/`print_warning` output helpers, `receipt` and `delivery` document commands
- `jinjareportpy/__init__.py` — Export new CLI symbols (`Colors`, `cprint`, `print_success`, `print_error`, `print_warning`, `CLIBase`, `CLIConfig`, `Subcommand`, etc.)

#### Changed
- `jinjareportpy/cli.py` — Refactor entire CLI with colored output, `--no-color`/`-q`/`-v`/`-vv` flags, and factory function `create_cli()`
- `jinjareportpy/README_cli.md` — Rewrite documentation with CI/CD pipeline examples, `CLIBase` usage, connection/operation argument groups (+494 −112 lines)

---

### `a40573a` — readme cli and config (2026-02-10)

Add dedicated README documentation for CLI and configuration modules.

**2 files changed** | +754 −0 lines

#### Added
- `jinjareportpy/README_cli.md` — Full CLI reference: commands, options, environment variables, programmatic usage (+357 lines)
- `jinjareportpy/README_config.md` — Configuration module reference: priority resolution, TOML schema, environment variables, API (+397 lines)

---

### `25e6ff4` — files arranged (2026-02-10)

Clean up misplaced files: remove root-level HTML outputs, old TOML example, and Spanish-named output files.

**9 files changed** | +0 −6285 lines

#### Removed
- `demo_report.html` — Move from root (was generated at root level)
- `invoice.html` — Move from root
- `quote.html` — Move from root
- `jinjareportpy.toml.example` — Remove from root (relocated)
- `jinjareportpy/output/albaran.html` — Remove Spanish-named output
- `jinjareportpy/output/factura.html` — Remove Spanish-named output
- `jinjareportpy/output/presupuesto.html` — Remove Spanish-named output
- `jinjareportpy/output/recibo.html` — Remove Spanish-named output
- `jinjareportpy/output/invoice_INV_2026_001.html` — Remove generated test output

---

### `91d7b84` — cli and config implementation (2026-02-09)

Implement full CLI (`cli.py`) and expand centralized configuration with locale, page size, orientation, PDF options, and all getter/setter convenience functions.

**12 files changed** | +2597 −1362 lines

#### Added
- `jinjareportpy/cli.py` — Full CLI with argparse: `config show/set/reset/init`, `demo`, `formats`, `templates`, `invoice`, `quote` commands (+632 lines)
- `llms.txt` — LLM-oriented project documentation with full API surface, configuration, and examples (+331 lines)
- `jinjareportpy/output/invoice_INV_2026_001.html` — Generated invoice sample

#### Changed
- `jinjareportpy/__main__.py` — Replace inline demo with CLI entry point delegating to `cli.main()` (+13 −112 lines)
- `jinjareportpy/__init__.py` — Export new config getters/setters: `get_assets_dir`, `set_assets_dir`, `get_locale`, `set_locale`, `get_page_size`, `set_page_size`, `get_orientation`, `set_orientation`
- `jinjareportpy/config.py` — Add `JinjaReportConfig` methods for locale, page size, orientation, PDF zoom/optimize, default format, and TOML config file discovery (+303 −4 lines)
- `jinjareportpy/document.py` — Use `get_templates_dir()` from centralized config instead of hardcoded path
- `jinjareportpy/generator.py` — Use centralized `get_templates_dir()` for template resolution
- `.github/copilot-instructions.md` — Document CLI commands and centralized configuration
- `README.md` — Add Configuration and CLI sections (+242 lines)
- `jinjareportpy.toml.example` — Update priority resolution documentation and add new settings

---

### `62ff416` — main and configurable paths (2026-02-09)

Introduce `JinjaReportConfig` centralized configuration class, `ReportViewer` browser integration, TOML config file support, and `main.py` entry point.

**13 files changed** | +3215 −43 lines

#### Added
- `jinjareportpy/config.py` — `JinjaReportConfig` class with multi-source resolution (env > programmatic > file > defaults), TOML loading, and path getters/setters (+271 −11 lines)
- `jinjareportpy/viewer.py` — `ReportViewer` class: first report → new window, subsequent reports → new tabs, `open_in_browser()`, `open_in_new_window()`, `reset_viewer()` (+183 −21 lines)
- `main.py` — Standalone entry point with demo report generation (+497 lines)
- `jinjareportpy.toml.example` — Example TOML configuration file (+34 lines)
- `demo_report.html` — Generated demo report sample (+498 lines)
- `invoice.html` — Generated invoice sample (+827 lines)
- `quote.html` — Generated quote sample (+814 lines)

#### Changed
- `jinjareportpy/__init__.py` — Export `JinjaReportConfig`, path getters/setters (`get_templates_dir`, `set_templates_dir`, `get_formats_dir`, `set_formats_dir`, `get_output_dir`, `set_output_dir`)
- `jinjareportpy/formats/__init__.py` — Use configurable `get_formats_dir()` instead of hardcoded `FORMATS_DIR`
- `jinjareportpy/generator.py` — Use centralized `get_templates_dir()` for built-in templates
- `.github/copilot-instructions.md` — Add ReportViewer browser integration docs
- `.python-version` — Update from 3.10 to 3.13
- `pyproject.toml` — Add Python 3.13 classifier

---

### `7a2c37b` — Merge branch 'main' (2026-02-08)

Merge remote `.gitignore` update with local test deletion.

**1 file changed** | +201 −5 lines

#### Changed
- `.gitignore` — Expand with comprehensive Python `.gitignore` template (byte-compiled files, distribution, testing, environments, IDE exclusions, project-specific exclusions)

---

### `ccec7c5` — test deleted (2026-02-08)

Remove test output configuration example that was promoted to proper test infrastructure.

**1 file changed** | +0 −82 lines

#### Removed
- `examples/test_output_config.py` — Remove output directory configuration test script

---

### `a4858d3` — new ignore (2026-02-05)

Replace basic `.gitignore` with comprehensive Python template covering all common tools and IDEs.

**1 file changed** | +201 −5 lines

#### Changed
- `.gitignore` — Full Python `.gitignore`: byte-compiled, C extensions, distribution, installer logs, test coverage, translations, environments, Jupyter, pipenv, UV, poetry, pdm, Celery, JetBrains, VS Code, Ruff, Cursor (+201 −5 lines)

---

### `7b0f2f8` — ignore more files (2026-01-29)

Add project-specific exclusions to `.gitignore`.

**1 file changed** | +11 −0 lines

#### Added
- `.gitignore` — Exclude `.github/`, `.vscode/`, `project_structure.txt`, `pyproject.toml`, `tests/`, `docs/`, `notebooks/`, `ToDo/`, and `**/secrets.*` from Copilot context

---

### `0c56b27` — renamed (2026-01-27)

Delete old `ninjareportpy/` package directory (cleanup after rename to `jinjareportpy`).

**10 files changed** | +0 −2126 lines

#### Removed
- `ninjareportpy/__init__.py` — Delete old package public API
- `ninjareportpy/__main__.py` — Delete old entry point
- `ninjareportpy/assets.py` — Delete old asset management
- `ninjareportpy/base.py` — Delete old base document class
- `ninjareportpy/config.py` — Delete old configuration
- `ninjareportpy/exceptions.py` — Delete old exceptions
- `ninjareportpy/filters.py` — Delete old Jinja2 filters
- `ninjareportpy/formats/__init__.py` — Delete old formats package
- `ninjareportpy/generator.py` — Delete old report generator
- `ninjareportpy/viewer.py` — Delete old viewer module

---

### `30bb088` — project renamed and winformpy viewer erased (2026-01-25)

Rename project from NinjaReportPy to JinjaReportPy. Copy all source to `jinjareportpy/` package. Remove WinFormPy embedded browser integration.

**89 files changed** | +2129 −540 lines

#### Added
- `jinjareportpy/` — New package directory with all source modules copied from `ninjareportpy/`

#### Changed
- `.github/copilot-instructions.md` — Rename all references from NinjaReportPy/ninjareportpy to JinjaReportPy/jinjareportpy
- `README.md` — Update project name, imports, and examples (+34 −112 lines)
- `examples/demo.py` — Update imports from `ninjareportpy` to `jinjareportpy`
- `examples/test_output_config.py` — Update imports

#### Removed
- WinFormPy embedded browser integration (removed from copilot-instructions.md and viewer.py)

---

### `695e058` — new output parameter and folders reordered (2026-01-24)

Add configurable output directory via `ReportConfig`, reorganize project folders, and add output config test example.

**77 files changed** | +572 −98 lines

#### Added
- `examples/test_output_config.py` — Test script for output directory configuration (+82 lines)
- `jinjareportpy/output/` — Dedicated output directory for generated files

#### Changed
- `.github/copilot-instructions.md` — Document new project structure with `output/` directory, `ReportConfig` class, and configurable paths (+92 −27 lines)
- `README.md` — Update project structure and add output configuration docs (+202 −41 lines)
- `examples/demo.py` — Update imports from `reportpy` to `ninjareportpy`

---

### `fcc4df0` — first commit (2026-01-22)

Initial project creation with core document generation engine, multi-page reports, Jinja2 templates, predefined formats, PDF export, and browser viewer.

**80 files changed** | +20184 −0 lines

#### Added
- `ninjareportpy/__init__.py` — Public API exports
- `ninjareportpy/__main__.py` — CLI entry point with demo report generation
- `ninjareportpy/base.py` — `BaseDocument` abstract base class
- `ninjareportpy/document.py` — `Document` class with factory functions (`create_invoice`, `create_quote`, `create_receipt`, `create_delivery_note`)
- `ninjareportpy/report.py` — `Report` class for multi-page reports
- `ninjareportpy/page.py` — `Page` class (header + footer + sections)
- `ninjareportpy/sections.py` — `Section`, `TableSection`, `KPISection`, `TextSection`, `HeaderSection`, `FooterSection`
- `ninjareportpy/builder.py` — `ReportBuilder` fluent API and `quick_report()` helper
- `ninjareportpy/config.py` — `ReportConfig`, `PageSize`, `Orientation` configuration
- `ninjareportpy/assets.py` — Asset management with Base64 encoding
- `ninjareportpy/filters.py` — Custom Jinja2 filters (currency, date, number formatting)
- `ninjareportpy/generator.py` — `ReportGenerator` legacy API
- `ninjareportpy/pdf.py` — PDF export via WeasyPrint
- `ninjareportpy/viewer.py` — Browser/PDF viewer with WinFormPy integration
- `ninjareportpy/exceptions.py` — Custom exceptions (`TemplateNotFoundError`, `ViewerError`, etc.)
- `ninjareportpy/templates/` — Built-in HTML templates (`base.html`, `invoice.html`, `quote.html`, `receipt.html`, `delivery_note.html`)
- `ninjareportpy/formats/` — Predefined formats (`default/`, `corporate/`, `minimal/`) with CSS + HTML for header, footer, section, table, kpi, text
- `examples/demo.py` — Complete demo showcasing all features
- `.github/copilot-instructions.md` — Project instructions and architecture docs
- `README.md` — Project documentation
- `.gitignore` — Python gitignore
- `.python-version` — Python 3.10
- `.vscode/settings.json` — VS Code Python configuration
- `pyproject.toml` — Project metadata with Hatchling build system
- `tests/` — Unit test infrastructure

---

[Unreleased]: https://github.com/jrodriguezgar/JinjaReportPy/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jrodriguezgar/JinjaReportPy/releases/tag/v0.1.0
