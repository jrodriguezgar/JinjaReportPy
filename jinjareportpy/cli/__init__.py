"""JinjaReportPy Command Line Interface.

This package provides:

- **output** — ANSI colors, formatted print helpers, progress bars.
- **base** — Reusable ``CLIBase`` class, ``CLIConfig``, ``Subcommand``.
- **commands** — Argument parser, command handlers, and ``main()`` entry point.

All public symbols are re-exported here so that existing imports like
``from jinjareportpy.cli import main`` continue to work.
"""

from __future__ import annotations

# --- base class & dataclasses ----------------------------------------------
from .base import (
    CLIBase,
    CLIConfig,
    Subcommand,
    create_cli,
)

# --- parser & commands ------------------------------------------------------
from .commands import (
    get_parser,
    main,
)

# --- output utilities -------------------------------------------------------
from .output import (
    Colors,
    LogLevel,
    OutputFormat,
    confirm_action,
    cprint,
    print_error,
    print_header,
    print_info,
    print_progress,
    print_success,
    print_summary,
    print_table,
    print_warning,
)

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
