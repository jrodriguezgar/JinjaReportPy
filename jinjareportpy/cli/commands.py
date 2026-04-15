"""JinjaReportPy CLI command handlers, parser, and entry point.

Contains the argument parser (split into per-subcommand helpers),
all ``cmd_*`` handler functions, and the ``main()`` entry point.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

from ..config import JinjaReportConfig, get_formats_dir, get_templates_dir
from ..document import create_delivery_note, create_invoice, create_quote, create_receipt
from ..formats import get_available_formats, set_default_format
from ..report import Report
from ..sections import KPISection, Section, TableSection
from ..viewer import open_in_browser
from .output import (
    Colors,
    cprint,
    print_error,
    print_header,
    print_info,
    print_success,
    print_summary,
    print_table,
    print_warning,
)

__all__ = [
    "get_parser",
    "main",
]

logger = logging.getLogger(__name__)


# ============================================================================
# FILENAME HELPER
# ============================================================================


def _sanitize_filename(name: str) -> str:
    """Sanitize a document number for use as filename."""
    return name.replace("-", "_").replace("/", "_").replace(" ", "_")


# ============================================================================
# ARGUMENT PARSER — HELPERS
# ============================================================================


def _add_document_args(parser: argparse.ArgumentParser) -> None:
    """Add common document arguments to a subparser."""
    parser.add_argument(
        "-n",
        "--number",
        required=True,
        help="Document number (e.g. INV-2026-001)",
    )
    parser.add_argument(
        "--company",
        default="My Company Ltd.",
        help="Company name (default: My Company Ltd.)",
    )
    parser.add_argument(
        "--client",
        default="Client Corp.",
        help="Client name (default: Client Corp.)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output filename (without extension)",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Export as PDF instead of HTML",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open in browser after generation",
    )


def _add_config_subcommand(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register the ``config`` subcommand and its nested actions."""
    config_parser = subparsers.add_parser(
        "config",
        help="View and manage configuration",
        description="View and manage JinjaReportPy configuration",
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_action",
        title="Actions",
        metavar="<action>",
    )

    # config show
    config_show = config_subparsers.add_parser(
        "show",
        help="Show current configuration",
    )
    config_show.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # config set
    config_set = config_subparsers.add_parser(
        "set",
        help="Set a configuration value",
    )
    config_set.add_argument(
        "key",
        choices=[
            "templates_dir",
            "formats_dir",
            "output_dir",
            "assets_dir",
            "locale",
            "page_size",
            "orientation",
            "default_format",
            "pdf_zoom",
            "pdf_optimize_images",
        ],
        help="Configuration key to set",
    )
    config_set.add_argument(
        "value",
        help="Value to set",
    )

    # config reset
    config_subparsers.add_parser(
        "reset",
        help="Reset configuration to defaults",
    )

    # config init
    config_init = config_subparsers.add_parser(
        "init",
        help="Create a config file in current directory",
    )
    config_init.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing config file",
    )


def _add_demo_subcommand(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register the ``demo`` subcommand."""
    demo_parser = subparsers.add_parser(
        "demo",
        help="Generate a demo report",
        description="Generate a demo sales report to test the library",
    )
    demo_parser.add_argument(
        "-f",
        "--format",
        choices=["default", "corporate", "minimal"],
        default="default",
        help="Report format (default: default)",
    )
    demo_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output filename (without extension)",
    )
    demo_parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also generate PDF output",
    )
    demo_parser.add_argument(
        "--open",
        action="store_true",
        help="Open in browser after generation",
    )


def _add_listing_subcommands(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register the ``formats`` and ``templates`` subcommands."""
    formats_parser = subparsers.add_parser(
        "formats",
        help="List available formats",
    )
    formats_parser.add_argument(
        "--details",
        action="store_true",
        help="Show format file details",
    )

    subparsers.add_parser(
        "templates",
        help="List available document templates",
    )


def _add_document_subcommands(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register document-generation subcommands (invoice, quote, receipt, delivery)."""
    # invoice
    invoice_parser = subparsers.add_parser(
        "invoice",
        help="Generate an invoice",
    )
    _add_document_args(invoice_parser)

    # quote
    quote_parser = subparsers.add_parser(
        "quote",
        help="Generate a quote",
    )
    _add_document_args(quote_parser)
    quote_parser.add_argument(
        "--validity",
        type=int,
        default=30,
        help="Validity in days (default: 30)",
    )

    # receipt
    receipt_parser = subparsers.add_parser(
        "receipt",
        help="Generate a receipt",
    )
    _add_document_args(receipt_parser)
    receipt_parser.add_argument(
        "--amount",
        type=float,
        default=0.0,
        help="Payment amount (default: 0.00)",
    )
    receipt_parser.add_argument(
        "--concept",
        default="Payment received",
        help="Payment concept (default: Payment received)",
    )

    # delivery
    delivery_parser = subparsers.add_parser(
        "delivery",
        help="Generate a delivery note",
    )
    _add_document_args(delivery_parser)


# ============================================================================
# ARGUMENT PARSER — TOP-LEVEL
# ============================================================================


def get_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ``ArgumentParser`` with all subcommands.
    """
    from .. import __version__

    parser = argparse.ArgumentParser(
        prog="jinjareportpy",
        description=(
            f"{Colors.BOLD}JinjaReportPy{Colors.RESET} "
            "- Document & Report Generator"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""{Colors.CYAN}Examples:{Colors.RESET}
  %(prog)s config show              Show current configuration
  %(prog)s config set locale en_US  Set locale
  %(prog)s demo                     Generate demo report
  %(prog)s demo --format corporate  Demo with corporate format
  %(prog)s demo --pdf --open        Demo with PDF, open in browser
  %(prog)s formats                  List available formats
  %(prog)s invoice -n INV-001       Create an invoice
  %(prog)s receipt -n REC-001       Create a receipt
  %(prog)s delivery -n DN-001       Create a delivery note
        """,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v=INFO, -vv=DEBUG)",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    # NOTE: These flags intentionally mirror CLIBase._add_common_global_arguments
    # in cli/base.py.  The two parsers serve different roles: this one powers
    # the ``jinjareportpy`` entry-point, while CLIBase is a generic toolkit
    # for building arbitrary CLIs.  Kept separate to avoid coupling them.

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
        metavar="<command>",
    )

    _add_config_subcommand(subparsers)
    _add_demo_subcommand(subparsers)
    _add_listing_subcommands(subparsers)
    _add_document_subcommands(subparsers)

    return parser


# ============================================================================
# COMMAND HANDLERS
# ============================================================================


def cmd_config_show(args: argparse.Namespace) -> int:
    """Show current configuration."""

    config = JinjaReportConfig.get_all_config()

    if getattr(args, "json", False):
        print(json.dumps(config, indent=2, default=str))
        return 0

    print_header("JinjaReportPy Configuration")

    # Paths
    cprint("  Paths:", Colors.BOLD)
    for key in ("templates_dir", "formats_dir", "output_dir", "assets_dir"):
        value = config.get(key, "\u2014")
        print(f"    {key:<18} {value}")
    print()

    # Settings
    cprint("  Settings:", Colors.BOLD)
    for key in ("default_format", "page_size", "orientation", "locale"):
        value = config.get(key, "\u2014")
        print(f"    {key:<18} {value}")
    print()

    # PDF
    cprint("  PDF Options:", Colors.BOLD)
    for key in ("pdf_zoom", "pdf_optimize_images"):
        value = config.get(key, "\u2014")
        print(f"    {key:<22} {value}")
    print()

    # Environment overrides
    env_vars = {k: v for k, v in config.items() if k.startswith("env_") and v}
    if env_vars:
        cprint("  Environment Overrides:", Colors.BOLD)
        for key, value in env_vars.items():
            cprint(f"    {key:<22} {value}", Colors.YELLOW)
        print()

    return 0


def cmd_config_set(args: argparse.Namespace) -> int:
    """Set a configuration value."""

    key = args.key
    value = args.value

    setters: dict[str, Any] = {
        "templates_dir": JinjaReportConfig.set_templates_dir,
        "formats_dir": JinjaReportConfig.set_formats_dir,
        "output_dir": JinjaReportConfig.set_output_dir,
        "assets_dir": JinjaReportConfig.set_assets_dir,
        "locale": JinjaReportConfig.set_locale,
        "page_size": JinjaReportConfig.set_page_size,
        "orientation": JinjaReportConfig.set_orientation,
        "default_format": JinjaReportConfig.set_default_format,
    }

    try:
        if key in setters:
            setters[key](value)
        elif key == "pdf_zoom":
            JinjaReportConfig.set_pdf_zoom(float(value))
        elif key == "pdf_optimize_images":
            JinjaReportConfig.set_pdf_optimize_images(
                value.lower() in ("true", "1", "yes")
            )
        else:
            print_error(f"Unknown configuration key: {key}")
            return 1

        print_success(f"Set {key} = {value}")
        print()
        print_info(
            "This setting is session-only. "
            "Use a config file or env vars to persist."
        )
        return 0

    except (ValueError, TypeError) as e:
        print_error(f"Invalid value for '{key}': {e}")
        return 1


def cmd_config_reset(args: argparse.Namespace) -> int:
    """Reset configuration to defaults."""

    JinjaReportConfig.reset()
    print_success("Configuration reset to defaults")
    return 0


def cmd_config_init(args: argparse.Namespace) -> int:
    """Create a config file in current directory."""
    config_path = Path.cwd() / "jinjareportpy.toml"

    if config_path.exists() and not args.force:
        print_error(f"Config file already exists: {config_path}")
        print_info("Use --force to overwrite")
        return 1

    config_content = """\
# JinjaReportPy Configuration
# ============================
# Priority: Environment variables > This file > Defaults

[paths]
# templates_dir = "./templates"
# formats_dir = "./formats"
# output_dir = "./reports"
# assets_dir = "./assets"

[report]
default_format = "default"
page_size = "A4"
orientation = "portrait"
locale = "es_ES"

[pdf]
zoom = 1.0
optimize_images = true
"""

    config_path.write_text(config_content, encoding="utf-8")
    print_success(f"Created config file: {config_path}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Generate a demo report."""

    print_header("JinjaReportPy - Demo Report")

    # Set format
    if args.format:
        set_default_format(args.format)
        print_info(f"Using format: {args.format}")

    start = time.monotonic()

    # Create report
    report = Report(title="Demo Sales Report Q4 2025")

    # Page 1: Summary
    page1 = report.add_page()
    page1.set_header(title="Sales Report", subtitle="Q4 2025")
    page1.set_footer(
        left_text="Generated with JinjaReportPy", right_text="Page 1"
    )

    page1.add_section(
        KPISection(
            name="kpis",
            title="Key Metrics",
            kpis=[
                {"label": "Total Sales", "value": "\u20ac 125,430", "change": 15},
                {"label": "New Customers", "value": "48", "change": 8},
                {"label": "Avg Order", "value": "\u20ac 2,613", "change": -3},
            ],
        )
    )

    page1.add_section(
        TableSection(
            name="products",
            title="Sales by Product",
            headers=["Product", "Units", "Unit Price", "Total"],
            rows=[
                ["Product A", "150", "\u20ac 29.99", "\u20ac 4,498.50"],
                ["Product B", "320", "\u20ac 49.99", "\u20ac 15,996.80"],
                ["Product C", "85", "\u20ac 199.99", "\u20ac 16,999.15"],
            ],
            footer_row=["Total", "555", "", "\u20ac 37,494.45"],
        )
    )

    # Page 2: Regions
    page2 = report.add_page()
    page2.set_header(title="Regional Breakdown", subtitle="Q4 2025")
    page2.set_footer(left_text="Confidential", right_text="Page 2")

    page2.add_section(
        TableSection(
            name="regions",
            title="Sales by Region",
            headers=["Region", "Sales", "% of Total", "Growth"],
            rows=[
                ["North", "\u20ac 45,200", "36%", "+18%"],
                ["South", "\u20ac 32,100", "26%", "+12%"],
                ["East", "\u20ac 28,500", "23%", "+8%"],
                ["West", "\u20ac 19,630", "15%", "+5%"],
            ],
        )
    )

    page2.add_section(
        Section(
            name="notes",
            template=(
                '<div class="info-box">'
                "<strong>Notes:</strong><br>"
                "{{ content }}"
                "</div>"
            ),
            data={"content": "All data includes all regions. Pending final audit."},
            css=(
                ".info-box { background: var(--bg-light); "
                "border-left: 4px solid var(--primary-color); "
                "padding: 10px 15px; margin-top: 20px; }"
            ),
        )
    )

    # Export
    output_name = args.output or "demo_report"

    html_path = report.export_html(filename=f"{output_name}.html")
    print_success(f"HTML saved: {html_path}")

    if args.pdf:
        try:
            pdf_path = report.export_pdf(filename=f"{output_name}.pdf")
            print_success(f"PDF saved: {pdf_path}")
        except Exception as e:
            print_warning(f"PDF not available: {e}")

    elapsed = time.monotonic() - start

    if args.open:
        open_in_browser(str(html_path))
        print_success("Opened in browser")

    print()
    print_summary(
        {
            "pages": 2,
            "sections": 4,
            "format": args.format or "default",
            "elapsed": f"{elapsed:.2f}s",
        },
        title="Demo Results",
    )

    return 0


def cmd_formats(args: argparse.Namespace) -> int:
    """List available formats."""

    formats = get_available_formats()
    formats_dir = get_formats_dir()

    print_header("Available Formats")
    print_info(f"Directory: {formats_dir}")
    print()

    if args.details:
        # Show as detailed table per format
        for fmt in formats:
            cprint(f"  {fmt}", Colors.BOLD)
            format_path = formats_dir / fmt
            if format_path.exists():
                files = sorted(
                    list(format_path.glob("*.html")) + list(format_path.glob("*.css"))
                )
                for f in files:
                    size = f.stat().st_size
                    cprint(f"    {f.name:<20} {size:>6} bytes", Colors.MUTED)
            print()
    else:
        headers = ["Format", "Status"]
        rows = []
        for fmt in formats:
            format_path = formats_dir / fmt
            file_count = len(list(format_path.glob("*"))) if format_path.exists() else 0
            status = f"{file_count} files"
            rows.append([fmt, status])
        print_table(headers, rows)
        print()

    return 0


def cmd_templates(args: argparse.Namespace) -> int:
    """List available templates."""

    templates_dir = get_templates_dir()

    print_header("Available Templates")
    print_info(f"Directory: {templates_dir}")
    print()

    if templates_dir.exists():
        templates = sorted(templates_dir.glob("*.html"))
        if templates:
            headers = ["Template", "Size"]
            rows = []
            for t in templates:
                size = t.stat().st_size
                rows.append([t.stem, f"{size:,} bytes"])
            print_table(headers, rows)
        else:
            print_warning("No templates found")
    else:
        print_warning(f"Templates directory does not exist: {templates_dir}")

    print()
    return 0


def _export_document(
    doc: Any,
    doc_type: str,
    args: argparse.Namespace,
) -> int:
    """Export a document to HTML or PDF and optionally open it.

    Shared logic for invoice, quote, receipt, and delivery note commands.

    Args:
        doc: The document instance (has ``export_html`` / ``export_pdf``).
        doc_type: Short label like ``"invoice"``, ``"quote"``.
        args: Parsed CLI args (expects ``number``, ``output``, ``pdf``, ``open``).

    Returns:
        Exit code (0 = success).
    """
    output_name = getattr(args, "output", None) or (
        f"{doc_type}_{_sanitize_filename(args.number)}"
    )

    path: Path | str | None = None

    if args.pdf:
        try:
            path = doc.export_pdf(filename=f"{output_name}.pdf")
            print_success(f"PDF saved: {path}")
        except Exception as e:
            print_warning(f"PDF not available ({e}), falling back to HTML")
            path = doc.export_html(filename=f"{output_name}.html")
            print_success(f"HTML saved: {path}")
    else:
        path = doc.export_html(filename=f"{output_name}.html")
        print_success(f"HTML saved: {path}")

    if getattr(args, "open", False) and path:
        open_in_browser(str(path))
        print_success("Opened in browser")

    return 0


def cmd_invoice(args: argparse.Namespace) -> int:
    """Generate an invoice."""

    print_info(f"Creating invoice {args.number}...")

    invoice = create_invoice(
        invoice_number=args.number,
        company={"name": args.company},
        client={"name": args.client},
        items=[
            {"description": "Service / Product", "quantity": 1, "unit_price": 100},
        ],
    )

    return _export_document(invoice, "invoice", args)


def cmd_quote(args: argparse.Namespace) -> int:
    """Generate a quote."""

    validity = getattr(args, "validity", 30)
    print_info(f"Creating quote {args.number} (valid {validity} days)...")

    quote = create_quote(
        quote_number=args.number,
        company={"name": args.company},
        client={"name": args.client},
        items=[
            {"description": "Service / Product", "quantity": 1, "unit_price": 100},
        ],
        validity_days=validity,
    )

    return _export_document(quote, "quote", args)


def cmd_receipt(args: argparse.Namespace) -> int:
    """Generate a receipt."""

    amount = getattr(args, "amount", 0.0)
    concept = getattr(args, "concept", "Payment received")
    print_info(f"Creating receipt {args.number} ({amount:.2f})...")

    receipt = create_receipt(
        receipt_number=args.number,
        company={"name": args.company},
        client={"name": args.client},
        amount=amount,
        concept=concept,
    )

    return _export_document(receipt, "receipt", args)


def cmd_delivery(args: argparse.Namespace) -> int:
    """Generate a delivery note."""

    print_info(f"Creating delivery note {args.number}...")

    delivery = create_delivery_note(
        delivery_number=args.number,
        company={"name": args.company},
        client={"name": args.client},
        items=[
            {"code": "ITEM-001", "description": "Sample item", "quantity": 1},
        ],
    )

    return _export_document(delivery, "delivery_note", args)


# ============================================================================
# COMMAND DISPATCH
# ============================================================================

_COMMANDS: dict[str, Any] = {
    "demo": cmd_demo,
    "formats": cmd_formats,
    "templates": cmd_templates,
    "invoice": cmd_invoice,
    "quote": cmd_quote,
    "receipt": cmd_receipt,
    "delivery": cmd_delivery,
}

_CONFIG_ACTIONS: dict[str, Any] = {
    "show": cmd_config_show,
    "set": cmd_config_set,
    "reset": cmd_config_reset,
    "init": cmd_config_init,
}


def _configure_logging(verbose: int, quiet: bool) -> None:
    """Configure logging based on verbosity flags."""
    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose >= 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Exit code (0 = success, non-zero = error).
    """
    parser = get_parser()
    args = parser.parse_args(argv)

    # Handle --no-color before any output
    if getattr(args, "no_color", False):
        Colors.disable()

    # Configure logging from verbosity
    _configure_logging(
        getattr(args, "verbose", 0),
        getattr(args, "quiet", False),
    )

    if args.command is None:
        parser.print_help()
        return 0

    # Config subcommand dispatch
    if args.command == "config":
        action = getattr(args, "config_action", None)
        if action and action in _CONFIG_ACTIONS:
            try:
                return _CONFIG_ACTIONS[action](args)
            except Exception as e:
                print_error(str(e))
                logger.debug("Config error", exc_info=True)
                return 1
        # Default: show config
        args.json = False
        return cmd_config_show(args)

    # Regular command dispatch
    handler = _COMMANDS.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print()
            print_warning("Interrupted by user")
            return 130
        except Exception as e:
            print_error(str(e))
            logger.debug("Command error", exc_info=True)
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
