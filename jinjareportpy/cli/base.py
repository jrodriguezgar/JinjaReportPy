"""Reusable CLI base class and configuration dataclasses.

Provides ``CLIBase`` for building CLI applications with subcommand
registration, connection/operation argument groups, statistics tracking,
and colored output.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from .output import (
    Colors,
    LogLevel,
    OutputFormat,
    print_error,
    print_success,
    print_summary,
)

__all__ = [
    "CLIConfig",
    "Subcommand",
    "CLIBase",
    "create_cli",
]


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

    def _add_common_global_arguments(
        self, parser: argparse.ArgumentParser,
    ) -> argparse._ArgumentGroup:
        """Add common global arguments shared by root parser and subparsers."""
        grp = parser.add_argument_group("Global Options")
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
        return grp

    def _add_global_arguments(self) -> None:
        grp = self._add_common_global_arguments(self.parser)
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

    def _add_global_arguments_to_subparser(
        self, subparser: argparse.ArgumentParser,
    ) -> None:
        self._add_common_global_arguments(subparser)

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
