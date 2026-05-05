#!/usr/bin/env python3
"""
📄 JinjaReportPy - Interactive Demo

Interactive launcher to explore formats, templates, and generate sample documents.

Run with:
    uv run python examples/interactive_demo.py

Or directly:
    python examples/interactive_demo.py
"""

import sys
from pathlib import Path

# Add project root to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from jinjareportpy import (
    ReportBuilder,
    create_invoice,
    create_quote,
    get_available_formats,
    get_formats_dir,
    # Config
    get_output_dir,
    get_templates_dir,
    # Viewer
    open_in_browser,
    reset_viewer,
)

# =============================================================================
# FEATURE DISPLAY FUNCTIONS
# =============================================================================

def get_templates() -> list[str]:
    """Get list of available document templates."""
    templates_dir = get_templates_dir()
    if templates_dir.exists():
        return sorted([f.stem for f in templates_dir.glob("*.html") if f.stem != "base"])
    return []


def get_outputs() -> list[str]:
    """Get list of generated output files."""
    output_dir = get_output_dir()
    if output_dir.exists():
        return sorted([f.name for f in output_dir.glob("*.html")])
    return []


def show_project_overview() -> None:
    """Display project overview with all features."""
    formats = get_available_formats()
    templates = get_templates()
    outputs = get_outputs()

    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                        📊 PROJECT OVERVIEW                                ║
╠═══════════════════════════════════════════════════════════════════════════╣""")

    # Formats section
    print("║                                                                           ║")
    print("║  🎨 FORMATS (styling themes)                                              ║")
    print("║  ─────────────────────────────────────────────────────────────────────    ║")
    format_list = "  •  ".join(formats) if formats else "(none)"
    print(f"║     {format_list:<66} ║")
    print("║     📁 Location: jinjareportpy/formats/                                  ║")

    # Templates section
    print("║                                                                           ║")
    print("║  📄 TEMPLATES (document types)                                            ║")
    print("║  ─────────────────────────────────────────────────────────────────────    ║")
    template_list = "  •  ".join(templates) if templates else "(none)"
    print(f"║     {template_list:<66} ║")
    print("║     📁 Location: jinjareportpy/templates/                                ║")

    # Outputs section
    print("║                                                                           ║")
    print("║  📂 GENERATED FILES                                                       ║")
    print("║  ─────────────────────────────────────────────────────────────────────    ║")
    if outputs:
        # Show up to 6 files per line
        for i in range(0, len(outputs), 4):
            chunk = outputs[i:i+4]
            line = "  ".join(chunk)
            print(f"║     {line:<66} ║")
    else:
        print("║     (none - run demo to generate)                                        ║")
    print("║     📁 Location: jinjareportpy/output/                                   ║")

    print("║                                                                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")


def show_formats_detail() -> None:
    """Show detailed format information."""
    formats = get_available_formats()
    formats_dir = get_formats_dir()

    print("\n🎨 AVAILABLE FORMATS")
    print("=" * 50)

    for fmt in formats:
        fmt_path = formats_dir / fmt
        if fmt_path.exists():
            components = [f.stem for f in fmt_path.glob("*.html")]
            print(f"\n  📁 {fmt}/")
            for comp in sorted(components):
                print(f"      • {comp}.html + {comp}.css")

    print(f"\n📍 Formats directory: {formats_dir}")


def show_templates_detail() -> None:
    """Show detailed template information."""
    templates = get_templates()
    templates_dir = get_templates_dir()

    print("\n📄 AVAILABLE TEMPLATES")
    print("=" * 50)

    descriptions = {
        "invoice": "Commercial invoice with items, taxes, and payment info",
        "quote": "Price quotation with validity period",
        "receipt": "Payment receipt confirmation",
        "delivery_note": "Delivery/shipping document",
        "report": "Multi-section report with KPIs, tables, text",
    }

    for tmpl in templates:
        desc = descriptions.get(tmpl, "Custom template")
        print(f"\n  📄 {tmpl}.html")
        print(f"      {desc}")

    print(f"\n📍 Templates directory: {templates_dir}")


def show_outputs_detail() -> None:
    """Show generated outputs with option to open."""
    outputs = get_outputs()
    output_dir = get_output_dir()

    if not outputs:
        print("\n❌ No generated files found.")
        print("   Run demo first to generate sample documents.")
        return

    print("\n📂 GENERATED FILES")
    print("=" * 50)

    for i, f in enumerate(outputs, 1):
        file_path = output_dir / f
        size_kb = file_path.stat().st_size / 1024
        print(f"   [{i:2}] {f:<30} ({size_kb:.1f} KB)")

    print("\n   [a] Open ALL  |  [0] Back")
    print(f"\n📍 Output directory: {output_dir}")

    try:
        choice = input("\n👉 Choose file to open [1-N, a, 0]: ").strip().lower()
        if choice == "0":
            return
        elif choice == "a":
            reset_viewer()
            for i, f in enumerate(outputs):
                file_path = output_dir / f
                if i == 0:
                    print(f"\n🌐 Opening {f} in new window...")
                else:
                    print(f"   📑 Adding {f} as tab...")
                open_in_browser(html_path=file_path)
            print("\n✅ All files opened!")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(outputs):
                file_path = output_dir / outputs[idx]
                print(f"\n🌐 Opening {outputs[idx]}...")
                open_in_browser(html_path=file_path)
            else:
                print("\n❌ Invalid option")
    except (ValueError, EOFError, KeyboardInterrupt):
        pass


def file_exists(filename: str) -> bool:
    """Check if output file already exists."""
    return (get_output_dir() / filename).exists()


def confirm(message: str) -> bool:
    """Ask for user confirmation."""
    try:
        response = input(f"\n⚠️  {message} [y/N]: ").strip().lower()
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def ask_view_file(file_path) -> None:
    """Ask if user wants to view the generated file in browser."""
    try:
        response = input("\n🌐 Open in browser? [Y/n]: ").strip().lower()
        if response in ("", "y", "yes"):
            print(f"   Opening {file_path.name}...")
            open_in_browser(html_path=file_path)
    except (EOFError, KeyboardInterrupt):
        pass


def demo_quick_report(skip_confirm: bool = False, ask_view: bool = True) -> None:
    """Generate a quick report using ReportBuilder."""
    filename = "demo_report.html"
    if not skip_confirm and not file_exists(filename):
        if not confirm(f"Generate report {filename}?"):
            print("   ⏭️  Skipped")
            return

    print("\n📊 Generating report...")

    builder = (
        ReportBuilder("Sales Report Q4 2025", format_name="corporate")
        .header(title="Sales Report", subtitle="Fourth Quarter 2025")
        .footer(left="JinjaReportPy", center="Confidential", right="Page 1")
        .add_kpis("metrics", [
            {"label": "Total Sales", "value": "€125,430", "change": "+15%"},
            {"label": "New Customers", "value": "48", "change": "+8%"},
            {"label": "Conversion", "value": "3.2%", "change": "+0.5%"},
        ])
        .add_table("products",
            headers=["Product", "Units", "Revenue"],
            rows=[
                ["Product A", "150", "€4,498"],
                ["Product B", "320", "€15,997"],
                ["Product C", "89", "€8,900"],
            ],
            title="Sales by Product"
        )
        .add_text("notes", "Report generated automatically with JinjaReportPy.")
    )

    output_path = builder.export_html("demo_report.html")
    print(f"   ✅ Generated: {output_path}")
    if ask_view:
        ask_view_file(output_path)


def demo_invoice(skip_confirm: bool = False, ask_view: bool = True) -> None:
    """Generate a sample invoice."""
    filename = "invoice.html"
    if not skip_confirm and not file_exists(filename):
        if not confirm(f"Generate invoice {filename}?"):
            print("   ⏭️  Skipped")
            return

    print("\n📄 Generating invoice...")

    invoice = create_invoice(
        invoice_number="INV-2025-001",
        company={
            "name": "My Company Ltd.",
            "address": "123 Business Street",
            "city": "London EC1A 1BB",
            "tax_id": "GB123456789",
        },
        client={
            "name": "Client Corporation",
            "address": "456 Client Avenue",
            "city": "Manchester M1 1AA",
            "tax_id": "GB987654321",
        },
        items=[
            {"description": "Consulting Services", "quantity": 10, "unit_price": 150},
            {"description": "Software License", "quantity": 1, "unit_price": 500},
            {"description": "Support Package", "quantity": 1, "unit_price": 200},
        ],
        tax_rate=20,
        payment_info={
            "method": "Bank Transfer",
            "iban": "GB82 WEST 1234 5698 7654 32",
            "terms": "Net 30 days",
        },
    )

    output_path = invoice.export_html("invoice.html")
    print(f"   ✅ Generated: {output_path}")
    if ask_view:
        ask_view_file(output_path)


def demo_quote(skip_confirm: bool = False, ask_view: bool = True) -> None:
    """Generate a sample quote."""
    filename = "quote.html"
    if not skip_confirm and not file_exists(filename):
        if not confirm(f"Generate quote {filename}?"):
            print("   ⏭️  Skipped")
            return

    print("\n📋 Generating quote...")

    quote = create_quote(
        quote_number="QT-2025-015",
        company={"name": "My Company Ltd.", "tax_id": "GB123456789"},
        client={"name": "Potential Client Inc.", "tax_id": "GB555555555"},
        items=[
            {"description": "Web Development Project", "quantity": 1, "unit_price": 5000},
            {"description": "Monthly Maintenance", "quantity": 12, "unit_price": 200},
        ],
        validity_days=30,
        notes="This quote is valid for 30 days from the date of issue.",
    )

    output_path = quote.export_html("quote.html")
    print(f"   ✅ Generated: {output_path}")
    if ask_view:
        ask_view_file(output_path)


def show_menu() -> None:
    """Display interactive menu."""
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│                        📄 JinjaReportPy - MAIN MENU                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔍 EXPLORE PROJECT                                                         │
│     [1] Overview         Show formats, templates, outputs summary           │
│     [2] Formats          Detailed view of styling themes                    │
│     [3] Templates        Detailed view of document types                    │
│     [4] Outputs          Browse and open generated files                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🚀 GENERATE DOCUMENTS                                                      │
│     [5] Full Demo        Generate report + invoice + quote                  │
│     [6] Report           Sales report with KPIs and tables                  │
│     [7] Invoice          Commercial invoice                                 │
│     [8] Quote            Price quotation                                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│     [h] Help             Command line usage                                 │
│     [0] Exit                                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
""")


def show_help() -> None:
    """Display command line usage."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                         COMMAND LINE USAGE                                ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  uv run python examples/interactive_demo.py [command]                     ║
║                                                                           ║
║  EXPLORE:                                                                 ║
║  ─────────────────────────────────────────────────────────────────────    ║
║    overview       Show project overview (formats, templates, outputs)     ║
║    formats        List available styling formats                          ║
║    templates      List available document templates                       ║
║    outputs        Browse and open generated files                         ║
║                                                                           ║
║  GENERATE:                                                                ║
║  ─────────────────────────────────────────────────────────────────────    ║
║    demo           Generate all demo documents                             ║
║    report         Generate sales report                                   ║
║    invoice        Generate sample invoice                                 ║
║    quote          Generate sample quote                                   ║
║                                                                           ║
║  OTHER:                                                                   ║
║  ─────────────────────────────────────────────────────────────────────    ║
║    help           This help                                               ║
║    (no args)      Interactive menu                                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

📁 Output: jinjareportpy/output/
📖 Examples: examples/
""")


def interactive_menu() -> None:
    """Run interactive menu."""
    while True:
        show_menu()
        try:
            choice = input("👉 Choose option [1-8, h, 0]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if choice == "0":
            print("\n👋 Goodbye!")
            break
        # EXPLORE PROJECT
        elif choice == "1":
            show_project_overview()
        elif choice == "2":
            show_formats_detail()
        elif choice == "3":
            show_templates_detail()
        elif choice == "4":
            show_outputs_detail()
        # GENERATE DOCUMENTS
        elif choice == "5":
            # Full demo
            files = ["demo_report.html", "invoice.html", "quote.html"]
            all_exist = all(file_exists(f) for f in files)
            if all_exist or confirm("Generate ALL demo documents?"):
                demo_quick_report(skip_confirm=True, ask_view=False)
                demo_invoice(skip_confirm=True, ask_view=False)
                demo_quote(skip_confirm=True, ask_view=False)
                print("\n✨ Demo complete!")
                show_outputs_detail()  # Let user choose which to view
            else:
                print("   ⏭️  Cancelled")
        elif choice == "6":
            demo_quick_report()
        elif choice == "7":
            demo_invoice()
        elif choice == "8":
            demo_quote()
        elif choice == "h":
            show_help()
        else:
            print(f"\n❌ Invalid option: {choice}")

        input("\n⏎ Press Enter to continue...")


def main() -> None:
    """Main entry point."""
    print()
    print("╔═════════════════════════════════════════════════╗")
    print("║  📄 JinjaReportPy - Document Generator          ║")
    print("║     Reports  •  Invoices  •  Quotes             ║")
    print("╚═════════════════════════════════════════════════╝")

    # No arguments = interactive menu
    if len(sys.argv) == 1:
        interactive_menu()
        return

    # Parse command line arguments
    command = sys.argv[1].lower()

    def run_demo() -> None:
        files = ["demo_report.html", "invoice.html", "quote.html"]
        all_exist = all(file_exists(f) for f in files)
        if all_exist or confirm("Generate ALL demo documents?"):
            demo_quick_report(skip_confirm=True, ask_view=False)
            demo_invoice(skip_confirm=True, ask_view=False)
            demo_quote(skip_confirm=True, ask_view=False)
            print("\n✨ Demo complete!")
            show_outputs_detail()  # Let user choose which to view
        else:
            print("   ⏭️  Cancelled")

    commands = {
        # Explore
        "overview": show_project_overview,
        "formats": show_formats_detail,
        "templates": show_templates_detail,
        "outputs": show_outputs_detail,
        # Generate
        "demo": run_demo,
        "report": demo_quick_report,
        "invoice": demo_invoice,
        "quote": demo_quote,
        # Other
        "help": show_help,
        "view": show_outputs_detail,  # alias
    }

    if command in commands:
        commands[command]()
    else:
        print(f"\n❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
