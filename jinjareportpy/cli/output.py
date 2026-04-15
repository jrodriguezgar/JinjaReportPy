"""Colored terminal output utilities.

Provides ANSI color codes, formatted print helpers, progress bars,
confirmation prompts, and output format/log-level enums.
"""

from __future__ import annotations

import sys
from enum import Enum
from typing import Any

__all__ = [
    "Colors",
    "OutputFormat",
    "LogLevel",
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



def print_success(message: str) -> None:
    """Print success message with checkmark."""
    cprint(f"  \u2713 {message}", Colors.SUCCESS)


def print_error(message: str) -> None:
    """Print error message with X mark to stderr."""
    cprint(f"  \u2717 {message}", Colors.ERROR, file=sys.stderr)


def print_warning(message: str) -> None:
    """Print warning message with warning sign."""
    cprint(f"  \u26a0 {message}", Colors.WARNING)


def print_info(message: str) -> None:
    """Print info message with info symbol."""
    cprint(f"  \u2139 {message}", Colors.INFO)


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
