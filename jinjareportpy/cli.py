"""
JinjaReportPy Command Line Interface

Provides CLI commands for:
- Viewing and managing configuration
- Generating demo reports
- Creating documents (invoices, quotes, etc.)
- Listing available formats and templates

Usage:
    python -m jinjareportpy --help
    python -m jinjareportpy config show
    python -m jinjareportpy config set output_dir ./reports
    python -m jinjareportpy demo
    python -m jinjareportpy invoice --number INV-001 --company "My Company"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from . import __version__


def get_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="jinjareportpy",
        description="📄 JinjaReportPy - Generador de Documentos e Informes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s config show              # Show current configuration
  %(prog)s config set locale en_US  # Set locale
  %(prog)s demo                     # Generate demo report
  %(prog)s demo --format corporate  # Demo with corporate format
  %(prog)s formats                  # List available formats
  %(prog)s invoice -n INV-001       # Create an invoice
        """,
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
        metavar="<command>",
    )
    
    # --- config command ---
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
            "templates_dir", "formats_dir", "output_dir", "assets_dir",
            "locale", "page_size", "orientation", "default_format",
            "pdf_zoom", "pdf_optimize_images",
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
        "-f", "--force",
        action="store_true",
        help="Overwrite existing config file",
    )
    
    # --- demo command ---
    demo_parser = subparsers.add_parser(
        "demo",
        help="Generate a demo report",
        description="Generate a demo sales report to test the library",
    )
    demo_parser.add_argument(
        "-f", "--format",
        choices=["default", "corporate", "minimal"],
        default="default",
        help="Report format (default: default)",
    )
    demo_parser.add_argument(
        "-o", "--output",
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
    
    # --- formats command ---
    formats_parser = subparsers.add_parser(
        "formats",
        help="List available formats",
    )
    formats_parser.add_argument(
        "--details",
        action="store_true",
        help="Show format details",
    )
    
    # --- templates command ---
    templates_parser = subparsers.add_parser(
        "templates",
        help="List available templates",
    )
    
    # --- invoice command ---
    invoice_parser = subparsers.add_parser(
        "invoice",
        help="Generate an invoice",
    )
    invoice_parser.add_argument(
        "-n", "--number",
        required=True,
        help="Invoice number",
    )
    invoice_parser.add_argument(
        "--company",
        default="My Company Ltd.",
        help="Company name",
    )
    invoice_parser.add_argument(
        "--client",
        default="Client Corp.",
        help="Client name",
    )
    invoice_parser.add_argument(
        "-o", "--output",
        help="Output filename",
    )
    invoice_parser.add_argument(
        "--pdf",
        action="store_true",
        help="Export as PDF",
    )
    invoice_parser.add_argument(
        "--open",
        action="store_true",
        help="Open after generation",
    )
    
    # --- quote command ---
    quote_parser = subparsers.add_parser(
        "quote",
        help="Generate a quote",
    )
    quote_parser.add_argument(
        "-n", "--number",
        required=True,
        help="Quote number",
    )
    quote_parser.add_argument(
        "--company",
        default="My Company Ltd.",
        help="Company name",
    )
    quote_parser.add_argument(
        "--client",
        default="Client Corp.",
        help="Client name",
    )
    quote_parser.add_argument(
        "-o", "--output",
        help="Output filename",
    )
    quote_parser.add_argument(
        "--pdf",
        action="store_true",
        help="Export as PDF",
    )
    
    return parser


def cmd_config_show(args: argparse.Namespace) -> int:
    """Show current configuration."""
    from .config import JinjaReportConfig
    
    config = JinjaReportConfig.get_all_config()
    
    if args.json:
        print(json.dumps(config, indent=2, default=str))
    else:
        print("=" * 60)
        print("  JinjaReportPy Configuration")
        print("=" * 60)
        print()
        print("📁 Paths:")
        print(f"   templates_dir:  {config['templates_dir']}")
        print(f"   formats_dir:    {config['formats_dir']}")
        print(f"   output_dir:     {config['output_dir']}")
        print(f"   assets_dir:     {config['assets_dir']}")
        print()
        print("⚙️  Settings:")
        print(f"   default_format: {config['default_format']}")
        print(f"   page_size:      {config['page_size']}")
        print(f"   orientation:    {config['orientation']}")
        print(f"   locale:         {config['locale']}")
        print()
        print("📄 PDF Options:")
        print(f"   pdf_zoom:            {config['pdf_zoom']}")
        print(f"   pdf_optimize_images: {config['pdf_optimize_images']}")
        print()
        
        # Show environment overrides
        env_vars = {k: v for k, v in config.items() if k.startswith("env_") and v}
        if env_vars:
            print("🔧 Environment Overrides:")
            for key, value in env_vars.items():
                print(f"   {key}: {value}")
            print()
    
    return 0


def cmd_config_set(args: argparse.Namespace) -> int:
    """Set a configuration value."""
    from .config import JinjaReportConfig
    
    key = args.key
    value = args.value
    
    try:
        if key == "templates_dir":
            JinjaReportConfig.set_templates_dir(value)
        elif key == "formats_dir":
            JinjaReportConfig.set_formats_dir(value)
        elif key == "output_dir":
            JinjaReportConfig.set_output_dir(value)
        elif key == "assets_dir":
            JinjaReportConfig.set_assets_dir(value)
        elif key == "locale":
            JinjaReportConfig.set_locale(value)
        elif key == "page_size":
            JinjaReportConfig.set_page_size(value)
        elif key == "orientation":
            JinjaReportConfig.set_orientation(value)
        elif key == "default_format":
            JinjaReportConfig.set_default_format(value)
        elif key == "pdf_zoom":
            JinjaReportConfig.set_pdf_zoom(float(value))
        elif key == "pdf_optimize_images":
            JinjaReportConfig.set_pdf_optimize_images(value.lower() in ("true", "1", "yes"))
        else:
            print(f"❌ Unknown configuration key: {key}", file=sys.stderr)
            return 1
        
        print(f"✓ Set {key} = {value}")
        print()
        print("Note: This setting is only active for this session.")
        print("To persist, use environment variables or a config file.")
        return 0
        
    except ValueError as e:
        print(f"❌ Invalid value: {e}", file=sys.stderr)
        return 1


def cmd_config_reset(args: argparse.Namespace) -> int:
    """Reset configuration to defaults."""
    from .config import JinjaReportConfig
    
    JinjaReportConfig.reset()
    print("✓ Configuration reset to defaults")
    return 0


def cmd_config_init(args: argparse.Namespace) -> int:
    """Create a config file in current directory."""
    config_path = Path.cwd() / "jinjareportpy.toml"
    
    if config_path.exists() and not args.force:
        print(f"❌ Config file already exists: {config_path}", file=sys.stderr)
        print("   Use --force to overwrite", file=sys.stderr)
        return 1
    
    config_content = '''# JinjaReportPy Configuration
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
'''
    
    config_path.write_text(config_content, encoding="utf-8")
    print(f"✓ Created config file: {config_path}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Generate a demo report."""
    from .report import Report
    from .sections import Section, TableSection, KPISection
    from .formats import set_default_format
    from .viewer import open_in_browser
    
    print("=" * 60)
    print("  JinjaReportPy - Demo Report")
    print("=" * 60)
    print()
    
    # Set format
    if args.format:
        set_default_format(args.format)
        print(f"📋 Using format: {args.format}")
    
    # Create report
    report = Report(title="Demo Sales Report Q4 2025")
    
    # Page 1: Summary
    page1 = report.add_page()
    page1.set_header(title="Sales Report", subtitle="Q4 2025")
    page1.set_footer(left_text="Generated with JinjaReportPy", right_text="Page 1")
    
    page1.add_section(KPISection(
        name="kpis",
        title="Key Metrics",
        kpis=[
            {"label": "Total Sales", "value": "€ 125,430", "change": 15},
            {"label": "New Customers", "value": "48", "change": 8},
            {"label": "Avg Order", "value": "€ 2,613", "change": -3},
        ],
    ))
    
    page1.add_section(TableSection(
        name="products",
        title="Sales by Product",
        headers=["Product", "Units", "Unit Price", "Total"],
        rows=[
            ["Product A", "150", "€ 29.99", "€ 4,498.50"],
            ["Product B", "320", "€ 49.99", "€ 15,996.80"],
            ["Product C", "85", "€ 199.99", "€ 16,999.15"],
        ],
        footer_row=["Total", "555", "", "€ 37,494.45"],
    ))
    
    # Page 2: Regions
    page2 = report.add_page()
    page2.set_header(title="Regional Breakdown", subtitle="Q4 2025")
    page2.set_footer(left_text="Confidential", right_text="Page 2")
    
    page2.add_section(TableSection(
        name="regions",
        title="Sales by Region",
        headers=["Region", "Sales", "% of Total", "Growth"],
        rows=[
            ["North", "€ 45,200", "36%", "+18%"],
            ["South", "€ 32,100", "26%", "+12%"],
            ["East", "€ 28,500", "23%", "+8%"],
            ["West", "€ 19,630", "15%", "+5%"],
        ],
    ))
    
    page2.add_section(Section(
        name="notes",
        template="""
        <div class="info-box">
            <strong>Notes:</strong><br>
            {{ content }}
        </div>
        """,
        data={"content": "All data includes all regions. Pending final audit."},
        css=".info-box { background: var(--bg-light); border-left: 4px solid var(--primary-color); padding: 10px 15px; margin-top: 20px; }",
    ))
    
    # Export
    output_name = args.output or "demo_report"
    
    html_path = report.export_html(filename=f"{output_name}.html")
    print(f"✓ HTML saved: {html_path}")
    
    if args.pdf:
        try:
            pdf_path = report.export_pdf(filename=f"{output_name}.pdf")
            print(f"✓ PDF saved: {pdf_path}")
        except Exception as e:
            print(f"⚠ PDF not available: {e}")
    
    if args.open:
        open_in_browser(str(html_path))
        print("✓ Opened in browser")
    
    print()
    print("Demo completed!")
    return 0


def cmd_formats(args: argparse.Namespace) -> int:
    """List available formats."""
    from .formats import get_available_formats, get_format_templates
    from .config import get_formats_dir
    
    formats = get_available_formats()
    formats_dir = get_formats_dir()
    
    print("=" * 50)
    print("  Available Formats")
    print("=" * 50)
    print()
    print(f"📁 Formats directory: {formats_dir}")
    print()
    
    for fmt in formats:
        print(f"  📋 {fmt}")
        
        if args.details:
            format_path = formats_dir / fmt
            if format_path.exists():
                files = list(format_path.glob("*.html")) + list(format_path.glob("*.css"))
                for f in sorted(files):
                    print(f"      └─ {f.name}")
    
    print()
    return 0


def cmd_templates(args: argparse.Namespace) -> int:
    """List available templates."""
    from .config import get_templates_dir
    
    templates_dir = get_templates_dir()
    
    print("=" * 50)
    print("  Available Templates")
    print("=" * 50)
    print()
    print(f"📁 Templates directory: {templates_dir}")
    print()
    
    if templates_dir.exists():
        templates = list(templates_dir.glob("*.html"))
        for t in sorted(templates):
            print(f"  📄 {t.stem}")
    else:
        print("  (No templates found)")
    
    print()
    return 0


def cmd_invoice(args: argparse.Namespace) -> int:
    """Generate an invoice."""
    from .document import create_invoice
    from .viewer import open_in_browser
    
    print(f"📄 Creating invoice {args.number}...")
    
    invoice = create_invoice(
        invoice_number=args.number,
        company={"name": args.company},
        client={"name": args.client},
        items=[
            {"description": "Service / Product", "quantity": 1, "unit_price": 100},
        ],
    )
    
    output_name = args.output or f"invoice_{args.number.replace('-', '_').replace('/', '_')}"
    
    if args.pdf:
        try:
            path = invoice.export_pdf(filename=f"{output_name}.pdf")
            print(f"✓ PDF saved: {path}")
        except Exception as e:
            print(f"⚠ PDF not available: {e}")
            path = invoice.export_html(filename=f"{output_name}.html")
            print(f"✓ HTML saved: {path}")
    else:
        path = invoice.export_html(filename=f"{output_name}.html")
        print(f"✓ HTML saved: {path}")
    
    if args.open:
        open_in_browser(str(path))
    
    return 0


def cmd_quote(args: argparse.Namespace) -> int:
    """Generate a quote."""
    from .document import create_quote
    
    print(f"📄 Creating quote {args.number}...")
    
    quote = create_quote(
        quote_number=args.number,
        company={"name": args.company},
        client={"name": args.client},
        items=[
            {"description": "Service / Product", "quantity": 1, "unit_price": 100},
        ],
        validity_days=30,
    )
    
    output_name = args.output or f"quote_{args.number.replace('-', '_').replace('/', '_')}"
    
    if args.pdf:
        try:
            path = quote.export_pdf(filename=f"{output_name}.pdf")
            print(f"✓ PDF saved: {path}")
        except Exception as e:
            print(f"⚠ PDF not available: {e}")
            path = quote.export_html(filename=f"{output_name}.html")
            print(f"✓ HTML saved: {path}")
    else:
        path = quote.export_html(filename=f"{output_name}.html")
        print(f"✓ HTML saved: {path}")
    
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    parser = get_parser()
    args = parser.parse_args(argv)
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    if args.command is None:
        parser.print_help()
        return 0
    
    # Dispatch to command handlers
    if args.command == "config":
        if args.config_action == "show":
            return cmd_config_show(args)
        elif args.config_action == "set":
            return cmd_config_set(args)
        elif args.config_action == "reset":
            return cmd_config_reset(args)
        elif args.config_action == "init":
            return cmd_config_init(args)
        else:
            # Default: show config
            args.json = False
            return cmd_config_show(args)
    
    elif args.command == "demo":
        return cmd_demo(args)
    
    elif args.command == "formats":
        return cmd_formats(args)
    
    elif args.command == "templates":
        return cmd_templates(args)
    
    elif args.command == "invoice":
        return cmd_invoice(args)
    
    elif args.command == "quote":
        return cmd_quote(args)
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
