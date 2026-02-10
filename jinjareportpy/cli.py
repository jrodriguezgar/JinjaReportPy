"""
JinjaReportPy Command Line Interface

Provides CLI commands for:
- Viewing and managing configuration
- Generating demo reports
- Creating documents (invoices, quotes, receipts, delivery notes)
- Listing available formats and templates

Usage:
    python -m jinjareportpy --help
    python -m jinjareportpy config show
    python -m jinjareportpy config set output_dir ./reports
    python -m jinjareportpy demo --format corporate --pdf --open
    python -m jinjareportpy invoice -n INV-001 --company "My Company"
    python -m jinjareportpy receipt -n REC-001 --amount 1500.00
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from . import __version__

__all__ = [
    # JinjaReportPy CLI
    "main",
    "get_parser",
    # Reusable CLIBase
    "CLIBase",
    "Subcommand",
    "CLIConfig",
    "create_cli",
    # Enums
    "OutputFormat",
    "LogLevel",
    # Output utilities
    "Colors",
    "cprint",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "print_header",
    "print_table",
    "print_summary",
    "print_progress",
    "confirm_action",
]

logger = logging.getLogger(__name__)


# ============================================================================
# COLORED OUTPUT
# ============================================================================


class Colors:
    """ANSI color codes with Windows compatibility.

    Colors are auto-initialized on module load. They are disabled
    automatically when output is not a TTY or the terminal does not
    support ANSI codes.

    Example::

        >>> print(f"{Colors.GREEN}Success{Colors.RESET}")
        >>> Colors.disable()  # Turn off all colors
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Semantic aliases
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = CYAN
    MUTED = GRAY

    _enabled: bool = True

    @classmethod
    def disable(cls) -> None:
        """Disable colors for non-TTY or unsupported terminals."""
        cls._enabled = False
        for attr in dir(cls):
            if attr.startswith("_") or callable(getattr(cls, attr)):
                continue
            if isinstance(getattr(cls, attr), str) and attr != "__module__":
                setattr(cls, attr, "")

    @classmethod
    def init(cls) -> None:
        """Initialize colors with Windows ANSI support."""
        if sys.platform == "win32":
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception:
                try:
                    import colorama  # type: ignore[import-untyped]

                    colorama.init()
                except ImportError:
                    cls.disable()
                    return
        if not sys.stdout.isatty():
            cls.disable()


Colors.init()


# ============================================================================
# ENUMS
# ============================================================================


class OutputFormat(Enum):
    """Supported output formats for CLI display."""

    TABLE = "table"
    JSON = "json"
    CSV = "csv"
    SUMMARY = "summary"
    QUIET = "quiet"


class LogLevel(Enum):
    """Logging verbosity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    QUIET = "quiet"


# ============================================================================
# OUTPUT UTILITIES
# ============================================================================


def cprint(
    message: str,
    color: str = "",
    bold: bool = False,
    file: Any = sys.stdout,
) -> None:
    """Print colored message to terminal."""
    prefix = ""
    if bold:
        prefix += Colors.BOLD
    if color:
        prefix += color
    suffix = Colors.RESET if (bold or color) else ""
    print(f"{prefix}{message}{suffix}", file=file)


# Keep backward-compatible private alias
_cprint = cprint


def print_success(message: str) -> None:
    """Print success message with checkmark."""
    cprint(f"  ✓ {message}", Colors.SUCCESS)


def print_error(message: str) -> None:
    """Print error message with X mark to stderr."""
    cprint(f"  ✗ {message}", Colors.ERROR, file=sys.stderr)


def print_warning(message: str) -> None:
    """Print warning message with warning sign."""
    cprint(f"  ⚠ {message}", Colors.WARNING)


def print_info(message: str) -> None:
    """Print info message with info symbol."""
    cprint(f"  ℹ {message}", Colors.INFO)


def print_header(
    title: str,
    width: int = 60,
    char: str = "=",
) -> None:
    """Print formatted section header."""
    print()
    cprint(char * width, Colors.CYAN, bold=True)
    cprint(f"  {title}", Colors.CYAN, bold=True)
    cprint(char * width, Colors.CYAN, bold=True)
    print()


def print_table(
    headers: list[str],
    rows: list[list[Any]],
    max_col_width: int = 40,
    indent: int = 2,
) -> None:
    """Print formatted ASCII table.

    Args:
        headers: Column header labels.
        rows: List of row data (each row is a list of values).
        max_col_width: Maximum column width before truncation.
        indent: Number of spaces to indent the table.
    """
    if not headers or not rows:
        return

    # Calculate column widths
    col_widths: list[int] = []
    for i, header in enumerate(headers):
        max_w = len(str(header))
        for row in rows:
            if i < len(row):
                max_w = max(max_w, len(str(row[i])))
        col_widths.append(min(max_w, max_col_width))

    def _truncate(value: Any, width: int) -> str:
        s = str(value)
        return s[: width - 3] + "..." if len(s) > width else s

    pad = " " * indent

    # Header
    header_row = " | ".join(
        _truncate(h, w).ljust(w) for h, w in zip(headers, col_widths)
    )
    separator = "-+-".join("-" * w for w in col_widths)

    cprint(f"{pad}{header_row}", Colors.CYAN, bold=True)
    print(f"{pad}{separator}")

    # Rows
    for row in rows:
        row_str = " | ".join(
            _truncate(row[i] if i < len(row) else "", w).ljust(w)
            for i, w in enumerate(col_widths)
        )
        print(f"{pad}{row_str}")


def print_summary(stats: dict[str, Any], title: str = "SUMMARY") -> None:
    """Print formatted summary statistics."""
    print_header(title)
    for key, value in stats.items():
        key_display = key.replace("_", " ").title()

        if "error" in key.lower() and value:
            value_color = Colors.ERROR
        elif "success" in key.lower() or "created" in key.lower():
            value_color = Colors.SUCCESS
        elif "warning" in key.lower() or "skipped" in key.lower():
            value_color = Colors.WARNING
        else:
            value_color = Colors.WHITE

        print(f"  {key_display + ':':<22} ", end="")
        cprint(str(value), value_color)

    cprint("  " + "=" * 56, Colors.CYAN)
    print()


def print_progress(
    current: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    width: int = 40,
) -> None:
    """Print an in-place progress bar.

    Args:
        current: Current progress value.
        total: Total expected value.
        prefix: Text before the bar.
        suffix: Text after the percentage.
        width: Character width of the bar.
    """
    if total == 0:
        percent, filled = 100.0, width
    else:
        percent = (current / total) * 100
        filled = int(width * current // total)

    bar = "\u2588" * filled + "-" * (width - filled)
    print(f"\r{prefix} |{bar}| {percent:.1f}% {suffix}", end="", flush=True)

    if current >= total:
        print()


def confirm_action(message: str, default: bool = False) -> bool:
    """Prompt user for confirmation.

    Args:
        message: Prompt text.
        default: Default answer when user presses Enter.

    Returns:
        ``True`` if the user confirmed, ``False`` otherwise.
    """
    suffix = " [Y/n]" if default else " [y/N]"
    response = input(f"{message}{suffix}: ").strip().lower()

    if not response:
        return default
    return response in ("y", "yes", "si", "s")


def _sanitize_filename(name: str) -> str:
    """Sanitize a document number for use as filename."""
    return name.replace("-", "_").replace("/", "_").replace(" ", "_")


# ============================================================================
# CLI CONFIGURATION & DATACLASSES
# ============================================================================


@dataclass
class CLIConfig:
    """Configuration for CLI behavior and appearance."""

    prog_name: str = "jinjareportpy"
    version: str = "1.0.0"
    description: str = ""
    epilog: str = ""

    colors_enabled: bool = True
    default_output_format: OutputFormat = OutputFormat.SUMMARY
    default_log_level: LogLevel = LogLevel.INFO

    allow_parameter_files: bool = True
    require_confirmation: bool = False
    dry_run_by_default: bool = False

    default_timeout: int = 30
    default_page_size: int = 1000


@dataclass
class Subcommand:
    """Definition of a CLI subcommand."""

    name: str
    help: str
    handler: Callable[..., Any] | None = None
    aliases: list[str] = field(default_factory=list)
    parser: argparse.ArgumentParser | None = None


# ============================================================================
# REUSABLE CLI BASE CLASS
# ============================================================================


class CLIBase:
    """Reusable base class for CLI applications.

    Provides subcommand registration, connection argument groups, operation
    argument groups, statistics tracking, and colored output — all wired
    together so you can spin up a full CLI in a few lines.

    Usage without subcommands::

        cli = CLIBase(prog="mytool", description="My tool", version="1.0.0")
        cli.add_export_group(formats=["csv", "json"])
        args = cli.parse_args()
        # ... your logic ...
        cli.print_final_summary()

    Usage with subcommands::

        cli = CLIBase(prog="mytool", description="My tool", version="1.0.0")
        cli.init_subcommands()

        export_p = cli.add_subcommand("export", "Export data", handler=run_export)
        export_p.add_argument("--format", "-f", required=True)

        args = cli.parse_args()
        cli.run()
    """

    def __init__(
        self,
        prog: str | None = None,
        description: str = "",
        version: str = "1.0.0",
        epilog: str | None = None,
        config: CLIConfig | None = None,
    ) -> None:
        self.config = config or CLIConfig(
            prog_name=prog or os.path.basename(sys.argv[0]),
            version=version,
            description=description,
            epilog=epilog or "",
        )

        self.parser = argparse.ArgumentParser(
            prog=prog,
            description=description,
            epilog=epilog,
            formatter_class=argparse.RawTextHelpFormatter,
            fromfile_prefix_chars="@" if self.config.allow_parameter_files else None,
        )

        self.parser.add_argument(
            "--version", "-V", action="version", version=f"%(prog)s {version}"
        )
        self._add_global_arguments()

        self._groups: dict[str, argparse._ArgumentGroup] = {}
        self._subparsers: argparse._SubParsersAction | None = None
        self._subcommands: dict[str, Subcommand] = {}
        self._handlers: dict[str, Callable[..., Any]] = {}
        self.args: argparse.Namespace | None = None
        self.stats: dict[str, int] = {}
        self.start_time: datetime | None = None

    # ----- global arguments -------------------------------------------------

    def _add_global_arguments(self) -> None:
        grp = self.parser.add_argument_group("Global Options")
        grp.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Increase verbosity (-v=INFO, -vv=DEBUG)",
        )
        grp.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress non-error output",
        )
        grp.add_argument(
            "--no-color", action="store_true",
            help="Disable colored output",
        )
        grp.add_argument(
            "--dry-run", action="store_true",
            default=self.config.dry_run_by_default,
            help="Simulate without making changes",
        )
        grp.add_argument(
            "--output-format",
            choices=[f.value for f in OutputFormat],
            default=self.config.default_output_format.value,
            help="Output display format",
        )
        grp.add_argument(
            "--config-file", type=str, metavar="FILE",
            help="Load configuration from JSON file",
        )
        grp.add_argument(
            "--log-file", type=str, metavar="FILE",
            help="Write logs to file",
        )

    def _add_global_arguments_to_subparser(
        self, subparser: argparse.ArgumentParser,
    ) -> None:
        grp = subparser.add_argument_group("Global Options")
        grp.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Increase verbosity (-v=INFO, -vv=DEBUG)",
        )
        grp.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress non-error output",
        )
        grp.add_argument(
            "--no-color", action="store_true",
            help="Disable colored output",
        )
        grp.add_argument(
            "--dry-run", action="store_true",
            default=self.config.dry_run_by_default,
            help="Simulate without making changes",
        )
        grp.add_argument(
            "--log-file", type=str, metavar="FILE",
            help="Write logs to file",
        )

    # ----- subcommand support -----------------------------------------------

    def init_subcommands(
        self,
        title: str = "Commands",
        dest: str = "command",
    ) -> argparse._SubParsersAction:
        """Initialize subcommand support.  Must be called before ``add_subcommand``."""
        self._subparsers = self.parser.add_subparsers(
            title=title,
            dest=dest,
            help="Available commands (use '<command> --help' for details)",
        )
        return self._subparsers

    def add_subcommand(
        self,
        name: str,
        help: str,  # noqa: A002
        handler: Callable[..., Any] | None = None,
        aliases: list[str] | None = None,
    ) -> argparse.ArgumentParser:
        """Register a subcommand.

        Args:
            name: Subcommand name (e.g. ``"convert"``).
            help: Short help text.
            handler: ``(args, cli) -> None`` callback.
            aliases: Optional short aliases.

        Returns:
            The subcommand's ``ArgumentParser`` for adding arguments.
        """
        if not self._subparsers:
            self.init_subcommands()

        aliases = aliases or []
        subparser = self._subparsers.add_parser(  # type: ignore[union-attr]
            name,
            help=help,
            aliases=aliases,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._add_global_arguments_to_subparser(subparser)

        sub = Subcommand(
            name=name, help=help, handler=handler,
            aliases=aliases, parser=subparser,
        )
        self._subcommands[name] = sub
        for alias in aliases:
            self._subcommands[alias] = sub

        if handler:
            self._handlers[name] = handler
            for alias in aliases:
                self._handlers[alias] = handler

        return subparser

    def set_handler(
        self,
        command: str,
        handler: Callable[..., Any],
    ) -> None:
        """Set or update the handler for an existing subcommand."""
        self._handlers[command] = handler
        if command in self._subcommands:
            self._subcommands[command].handler = handler

    def run(self) -> None:
        """Execute the handler for the parsed subcommand.

        Raises:
            RuntimeError: If ``parse_args`` has not been called yet.
        """
        if not self.args:
            raise RuntimeError("parse_args() must be called before run()")

        command = getattr(self.args, "command", None)
        if not command:
            self.parser.print_help()
            sys.exit(1)

        handler = self._handlers.get(command)
        if handler:
            handler(self.args, self)
        else:
            print_error(f"No handler registered for command: {command}")
            sys.exit(1)

    # ----- argument groups --------------------------------------------------

    def add_group(
        self,
        name: str,
        title: str | None = None,
        description: str | None = None,
    ) -> argparse._ArgumentGroup:
        """Add a custom argument group to the root parser."""
        group = self.parser.add_argument_group(title or name.title(), description)
        self._groups[name] = group
        return group

    # Connection groups

    def add_database_connection_group(self) -> argparse._ArgumentGroup:
        """Add database connection arguments."""
        group = self.add_group("db_connection", "Database Connection")
        group.add_argument(
            "--db-type", required=True,
            choices=["postgresql", "mysql", "sqlite", "oracle", "mssql"],
            help="Database type",
        )
        group.add_argument("--db-host", help="Database host")
        group.add_argument("--db-port", type=int, help="Database port")
        group.add_argument("--db-name", required=True, help="Database name")
        group.add_argument("--db-user", help="Database username")
        group.add_argument("--db-password", help="Database password")
        group.add_argument(
            "--db-password-file", metavar="FILE",
            help="Read password from file",
        )
        return group

    def add_ldap_connection_group(self) -> argparse._ArgumentGroup:
        """Add LDAP / Active Directory connection arguments."""
        group = self.add_group("ldap_connection", "LDAP Connection")
        group.add_argument("--host", "-H", required=True, help="LDAP server hostname")
        group.add_argument("--user", "-U", required=True, help="Bind DN or user principal")
        group.add_argument("--password", "-P", required=True, help="Bind password")
        group.add_argument("--password-file", metavar="FILE", help="Read password from file")
        group.add_argument("--base-dn", "-b", required=True, help="Search base DN")
        group.add_argument("--no-ssl", action="store_true", help="Disable SSL/TLS")
        group.add_argument(
            "--auth-method",
            choices=["SIMPLE", "NTLM", "KERBEROS"],
            default="SIMPLE",
            help="Authentication method",
        )
        return group

    def add_api_connection_group(self) -> argparse._ArgumentGroup:
        """Add REST API connection arguments."""
        group = self.add_group("api_connection", "API Connection")
        group.add_argument("--api-url", required=True, help="API base URL")
        group.add_argument("--api-key", help="API key")
        group.add_argument("--api-key-file", metavar="FILE", help="Read API key from file")
        group.add_argument("--client-id", help="OAuth client ID")
        group.add_argument("--client-secret", help="OAuth client secret")
        group.add_argument("--token", help="Bearer token")
        group.add_argument(
            "--timeout", type=int, default=30,
            help="Request timeout (seconds)",
        )
        return group

    # Operation groups

    def add_export_group(
        self, formats: list[str] | None = None,
    ) -> argparse._ArgumentGroup:
        """Add export configuration arguments."""
        group = self.add_group("export", "Export Configuration")
        formats = formats or ["csv", "json"]
        group.add_argument(
            "--format", "-f", required=True, choices=formats,
            help="Output format",
        )
        group.add_argument("--output", "-o", required=True, help="Output file/connection")
        group.add_argument("--filter", help="Filter expression")
        group.add_argument("--select-fields", help="Comma-separated fields to include")
        group.add_argument("--limit", type=int, help="Maximum records to export")
        return group

    def add_import_group(
        self, formats: list[str] | None = None,
    ) -> argparse._ArgumentGroup:
        """Add import configuration arguments."""
        group = self.add_group("import", "Import Configuration")
        formats = formats or ["csv", "excel", "json"]
        group.add_argument("--source", "-s", required=True, help="Source file path")
        group.add_argument(
            "--format", "-f", required=True, choices=formats,
            help="Source format",
        )
        group.add_argument("--skip-validation", action="store_true", help="Skip data validation")
        group.add_argument("--update-existing", action="store_true", help="Update existing records")
        group.add_argument(
            "--batch-size", type=int, default=100,
            help="Batch size for processing",
        )
        return group

    def add_sync_group(self) -> argparse._ArgumentGroup:
        """Add synchronization configuration arguments."""
        group = self.add_group("sync", "Sync Configuration")
        group.add_argument("--source", "-s", required=True, help="Source connection/file")
        group.add_argument("--target", "-t", required=True, help="Target connection/file")
        group.add_argument(
            "--mode",
            choices=["full", "incremental", "delta"],
            default="incremental",
            help="Sync mode",
        )
        group.add_argument(
            "--conflict-resolution",
            choices=["source", "target", "newest"],
            default="source",
            help="Conflict resolution strategy",
        )
        return group

    # ----- parsing ----------------------------------------------------------

    def parse_args(self, args: list[str] | None = None) -> argparse.Namespace:
        """Parse command-line arguments and configure logging."""
        if args is None and len(sys.argv) == 1:
            self._print_usage_hint()
            sys.exit(1)

        self.args = self.parser.parse_args(args)
        self._post_process_args()
        self._configure_logging()
        self.start_time = datetime.now()
        return self.args

    def _print_usage_hint(self) -> None:
        print(f"{self.config.prog_name} v{self.config.version}")
        print(f"\nUsage: {self.config.prog_name} [options]")
        print(f"Try '{self.config.prog_name} --help' for more information.")

    def _post_process_args(self) -> None:
        if getattr(self.args, "no_color", False):
            Colors.disable()
        # Load secrets from file when applicable
        for file_arg, target_arg in [
            ("password_file", "password"),
            ("db_password_file", "db_password"),
            ("api_key_file", "api_key"),
        ]:
            file_path = getattr(self.args, file_arg, None)
            if file_path and os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as fh:
                    setattr(self.args, target_arg, fh.readline().strip())

    def _configure_logging(self) -> None:
        if getattr(self.args, "quiet", False):
            level = logging.ERROR
        elif getattr(self.args, "verbose", 0) >= 2:
            level = logging.DEBUG
        elif getattr(self.args, "verbose", 0) >= 1:
            level = logging.INFO
        else:
            level = logging.WARNING
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        log_file = getattr(self.args, "log_file", None)
        if log_file:
            handler = logging.FileHandler(log_file, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            logging.getLogger().addHandler(handler)

    # ----- statistics -------------------------------------------------------

    def increment_stat(self, key: str, amount: int = 1) -> None:
        """Increment a statistic counter."""
        self.stats[key] = self.stats.get(key, 0) + amount

    def get_elapsed_time(self) -> str:
        """Return elapsed time as a human-readable string."""
        if not self.start_time:
            return "0:00:00"
        elapsed = datetime.now() - self.start_time
        return str(elapsed).split(".")[0]

    def print_final_summary(self) -> None:
        """Print execution summary including elapsed time."""
        elapsed = datetime.now() - self.start_time if self.start_time else None
        if elapsed:
            self.stats["elapsed_time"] = str(elapsed).split(".")[0]
        print_summary(
            self.stats,
            title=f"{self.config.prog_name.upper()} RESULTS",
        )

    def exit_with_error(self, message: str, code: int = 1) -> None:
        """Print error and exit."""
        print_error(message)
        sys.exit(code)

    def exit_success(self, message: str | None = None) -> None:
        """Print success message and exit."""
        if message:
            print_success(message)
        sys.exit(0)


# ============================================================================
# FACTORY FUNCTION
# ============================================================================


def create_cli(
    prog: str,
    description: str,
    version: str = "1.0.0",
    connection_type: str | None = None,
    operation_type: str | None = None,
) -> CLIBase:
    """Create a pre-configured ``CLIBase`` instance.

    Args:
        prog: Program name.
        description: Program description.
        version: Version string.
        connection_type: ``'database'``, ``'ldap'``, ``'api'``, or ``None``.
        operation_type: ``'export'``, ``'import'``, ``'sync'``, or ``None``.

    Returns:
        A ready-to-use ``CLIBase``.
    """
    cli = CLIBase(prog=prog, description=description, version=version)

    if connection_type == "database":
        cli.add_database_connection_group()
    elif connection_type == "ldap":
        cli.add_ldap_connection_group()
    elif connection_type == "api":
        cli.add_api_connection_group()

    if operation_type == "export":
        cli.add_export_group()
    elif operation_type == "import":
        cli.add_import_group()
    elif operation_type == "sync":
        cli.add_sync_group()

    return cli


# ============================================================================
# ARGUMENT PARSER (JinjaReportPy-specific)
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


def get_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ``ArgumentParser`` with all subcommands.
    """
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

    # --- demo command ---
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

    # --- formats command ---
    formats_parser = subparsers.add_parser(
        "formats",
        help="List available formats",
    )
    formats_parser.add_argument(
        "--details",
        action="store_true",
        help="Show format file details",
    )

    # --- templates command ---
    subparsers.add_parser(
        "templates",
        help="List available document templates",
    )

    # --- invoice command ---
    invoice_parser = subparsers.add_parser(
        "invoice",
        help="Generate an invoice",
    )
    _add_document_args(invoice_parser)

    # --- quote command ---
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

    # --- receipt command ---
    receipt_parser = subparsers.add_parser(
        "receipt",
        help="Generate a receipt",
    )
    _add_document_args(receipt_parser)
    receipt_parser.add_argument(
        "--amount",
        type=float,
        default=0.0,
        help="Receipt amount (default: 0.00)",
    )
    receipt_parser.add_argument(
        "--concept",
        default="Payment received",
        help="Payment concept (default: Payment received)",
    )

    # --- delivery command ---
    delivery_parser = subparsers.add_parser(
        "delivery",
        help="Generate a delivery note",
    )
    _add_document_args(delivery_parser)

    return parser


# ============================================================================
# COMMAND HANDLERS
# ============================================================================


def cmd_config_show(args: argparse.Namespace) -> int:
    """Show current configuration."""
    from .config import JinjaReportConfig

    config = JinjaReportConfig.get_all_config()

    if getattr(args, "json", False):
        print(json.dumps(config, indent=2, default=str))
        return 0

    print_header("JinjaReportPy Configuration")

    # Paths
    cprint("  Paths:", Colors.BOLD)
    for key in ("templates_dir", "formats_dir", "output_dir", "assets_dir"):
        value = config.get(key, "—")
        print(f"    {key:<18} {value}")
    print()

    # Settings
    cprint("  Settings:", Colors.BOLD)
    for key in ("default_format", "page_size", "orientation", "locale"):
        value = config.get(key, "—")
        print(f"    {key:<18} {value}")
    print()

    # PDF
    cprint("  PDF Options:", Colors.BOLD)
    for key in ("pdf_zoom", "pdf_optimize_images"):
        value = config.get(key, "—")
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
    from .config import JinjaReportConfig

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
    from .config import JinjaReportConfig

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
    from .formats import set_default_format
    from .report import Report
    from .sections import KPISection, Section, TableSection
    from .viewer import open_in_browser

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
    from .config import get_formats_dir
    from .formats import get_available_formats

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
    from .config import get_templates_dir

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
        from .viewer import open_in_browser

        open_in_browser(str(path))
        print_success("Opened in browser")

    return 0


def cmd_invoice(args: argparse.Namespace) -> int:
    """Generate an invoice."""
    from .document import create_invoice

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
    from .document import create_quote

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
    from .document import create_receipt

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
    from .document import create_delivery_note

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


def main(argv: Optional[list[str]] = None) -> int:
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
