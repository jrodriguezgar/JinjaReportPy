#!/usr/bin/env python3
"""
📄 JinjaReportPy - CLI Module Example

Demonstrates all CLI capabilities:
- Factory function (create_cli)
- CLIBase with subcommands
- Output utilities (colors, tables, progress, summary)
- Confirmation prompts
- Statistics tracking

Run:
    uv run python examples/cli_example.py --help
    uv run python examples/cli_example.py demo
    uv run python examples/cli_example.py demo --all
    uv run python examples/cli_example.py export --format csv --output report.csv
    uv run python examples/cli_example.py export -f json -o data.json -vv --dry-run
    uv run python examples/cli_example.py import --source data.csv --format csv
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure the package is importable when running from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jinjareportpy.cli import (
    # Base class & factory
    CLIBase,
    CLIConfig,
    # Output utilities
    Colors,
    LogLevel,
    # Enums
    OutputFormat,
    confirm_action,
    cprint,
    create_cli,
    print_error,
    print_header,
    print_info,
    print_progress,
    print_success,
    print_summary,
    print_table,
    print_warning,
)

# ============================================================================
# SUBCOMMAND HANDLERS
# ============================================================================


def run_demo(args, cli: CLIBase) -> None:
    """Handler for the 'demo' subcommand — showcases output utilities."""

    # -- Colored messages ----------------------------------------------------
    print_header("Colored Messages")
    print_success("Operation completed successfully")
    print_error("An error occurred (this goes to stderr)")
    print_warning("This is a warning message")
    print_info("Informational message")
    print()

    cprint("Bold cyan text", Colors.CYAN, bold=True)
    cprint("Muted gray text", Colors.MUTED)
    print()

    if not getattr(args, "all", False):
        print_info("Run with --all to see tables, progress bars and summary")
        return

    # -- Table ---------------------------------------------------------------
    print_header("Table Output")
    headers = ["Name", "Status", "Count"]
    rows = [
        ["Users", "Active", 150],
        ["Groups", "Synced", 25],
        ["Computers", "Pending", 78],
        ["Policies", "Applied", 42],
    ]
    print_table(headers, rows)
    print()

    # -- Progress bar --------------------------------------------------------
    print_header("Progress Bar")
    total = 50
    for i in range(total + 1):
        print_progress(i, total, prefix="Processing", suffix="done")
        time.sleep(0.02)
    print()

    # -- Summary statistics --------------------------------------------------
    print_header("Summary Statistics")
    stats = {
        "total_processed": 253,
        "success": 240,
        "warnings": 8,
        "errors": 5,
    }
    print_summary(stats, title="EXECUTION SUMMARY")

    # -- Track via CLIBase ---------------------------------------------------
    cli.increment_stat("demo_items", len(rows))
    cli.print_final_summary()


def run_export(args, cli: CLIBase) -> None:
    """Handler for the 'export' subcommand."""

    fmt = args.format
    output = args.output
    dry_run = getattr(args, "dry_run", False)

    print_header(f"Export → {fmt.upper()}")

    if dry_run:
        print_warning("DRY RUN — no files will be written")

    print_info(f"Format : {fmt}")
    print_info(f"Output : {output}")

    # Simulate export with progress
    total = 100
    for i in range(total + 1):
        print_progress(i, total, prefix="Exporting", suffix="records")
        time.sleep(0.01)

    cli.increment_stat("exported", total)

    if not dry_run:
        print_success(f"Exported {total} records to {output}")
    else:
        print_info(f"Would export {total} records to {output}")

    cli.print_final_summary()


def run_import(args, cli: CLIBase) -> None:
    """Handler for the 'import' subcommand."""

    source = args.source
    fmt = args.format

    print_header(f"Import ← {fmt.upper()}")
    print_info(f"Source : {source}")
    print_info(f"Format : {fmt}")

    # Simulate import
    total = 75
    for i in range(total + 1):
        print_progress(i, total, prefix="Importing", suffix="rows")
        time.sleep(0.01)

    cli.increment_stat("imported", total)
    cli.increment_stat("skipped", 3)
    print_success(f"Imported {total} records from {source}")

    cli.print_final_summary()


def run_confirm_demo(args, cli: CLIBase) -> None:
    """Handler for the 'confirm' subcommand — demonstrates confirm_action."""

    print_header("Confirmation Prompt")

    if confirm_action("Do you want to proceed with the operation?", default=False):
        print_success("User confirmed — proceeding")
        cli.increment_stat("confirmed", 1)
    else:
        print_warning("Operation cancelled by user")
        cli.increment_stat("cancelled", 1)

    cli.print_final_summary()


# ============================================================================
# EXAMPLE 1 — CLIBase WITH SUBCOMMANDS
# ============================================================================


def example_with_subcommands() -> None:
    """Build a CLI with subcommands, handlers, and aliases."""

    cli = CLIBase(
        prog="cli_example",
        description="JinjaReportPy CLI module demo — all capabilities in one script",
        version="1.0.0",
    )

    cli.init_subcommands()

    # demo subcommand
    demo_p = cli.add_subcommand(
        "demo", "Show output utilities (colors, tables, progress)", handler=run_demo, aliases=["d"]
    )
    demo_p.add_argument(
        "--all", "-a", action="store_true", help="Show all demos (tables, progress, summary)"
    )

    # export subcommand
    export_p = cli.add_subcommand(
        "export", "Simulate a data export", handler=run_export, aliases=["e"]
    )
    export_p.add_argument(
        "--format", "-f", required=True,
        choices=["csv", "json", "excel"], help="Output format",
    )
    export_p.add_argument(
        "--output", "-o", required=True, help="Output file path",
    )

    # import subcommand
    import_p = cli.add_subcommand(
        "import", "Simulate a data import", handler=run_import, aliases=["i"]
    )
    import_p.add_argument(
        "--source", "-s", required=True, help="Source file path",
    )
    import_p.add_argument(
        "--format", "-f", required=True,
        choices=["csv", "json", "excel"], help="Source format",
    )

    # confirm subcommand
    cli.add_subcommand(
        "confirm", "Demo interactive confirmation prompt", handler=run_confirm_demo, aliases=["c"]
    )

    cli.parse_args()
    cli.run()


# ============================================================================
# EXAMPLE 2 — FACTORY FUNCTION (create_cli)
# ============================================================================


def example_with_factory() -> None:
    """Create a pre-configured CLI using the factory function."""

    cli = create_cli(
        prog="db_export_tool",
        description="Export database tables to files",
        version="2.0.0",
        connection_type="database",
        operation_type="export",
    )

    args = cli.parse_args()

    print_header("Factory CLI")
    print_info(f"DB type : {args.db_type}")
    print_info(f"DB name : {args.db_name}")
    print_info(f"Format  : {args.format}")
    print_info(f"Output  : {args.output}")

    cli.increment_stat("exported", 42)
    cli.print_final_summary()


# ============================================================================
# EXAMPLE 3 — CUSTOM CLIConfig
# ============================================================================


def example_with_config() -> None:
    """Create a CLI with custom CLIConfig settings."""

    config = CLIConfig(
        prog_name="custom_tool",
        version="3.0.0",
        description="Tool with custom config defaults",
        default_output_format=OutputFormat.JSON,
        default_log_level=LogLevel.DEBUG,
        dry_run_by_default=True,
        default_timeout=60,
    )

    cli = CLIBase(config=config)
    cli.add_api_connection_group()

    args = cli.parse_args()

    print_header("Custom Config CLI")
    print_info(f"API URL : {args.api_url}")
    print_info(f"Timeout : {args.timeout}")
    print_info(f"Dry run : {args.dry_run}")

    cli.print_final_summary()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # By default, run the subcommand example (most complete).
    # Uncomment one of the others to try it:
    #
    #   example_with_factory()
    #   example_with_config()
    #
    example_with_subcommands()
