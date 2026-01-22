"""Filtros Jinja2 personalizados para NinjaReportPy."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from jinja2 import Environment


def format_currency(
    value: float | Decimal | int | None,
    symbol: str = "€",
    decimal_places: int = 2,
    thousands_sep: str = ".",
    decimal_sep: str = ",",
    symbol_after: bool = True,
) -> str:
    """Format a number as currency.

    Args:
        value: Numeric value to format.
        symbol: Currency symbol.
        decimal_places: Number of decimal places.
        thousands_sep: Thousands separator.
        decimal_sep: Decimal separator.
        symbol_after: Place symbol after value (European style).

    Returns:
        Formatted currency string.
    """
    if value is None:
        return ""

    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)

    # Format with proper separators
    formatted = f"{num:,.{decimal_places}f}"
    # Replace default separators with custom ones
    formatted = formatted.replace(",", "TEMP")
    formatted = formatted.replace(".", decimal_sep)
    formatted = formatted.replace("TEMP", thousands_sep)

    if symbol_after:
        return f"{formatted} {symbol}"
    return f"{symbol} {formatted}"


def format_date(
    value: datetime | date | str | None,
    format_str: str = "%d/%m/%Y",
    input_format: str | None = None,
) -> str:
    """Format a date value.

    Args:
        value: Date value to format.
        format_str: Output format string.
        input_format: Input format if value is a string.

    Returns:
        Formatted date string.
    """
    if value is None:
        return ""

    if isinstance(value, str):
        if input_format:
            value = datetime.strptime(value, input_format)
        else:
            # Try common formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
            else:
                return value  # Return original if parsing fails

    if isinstance(value, (datetime, date)):
        return value.strftime(format_str)

    return str(value)


def format_datetime(
    value: datetime | str | None,
    format_str: str = "%d/%m/%Y %H:%M",
) -> str:
    """Format a datetime value.

    Args:
        value: Datetime value to format.
        format_str: Output format string.

    Returns:
        Formatted datetime string.
    """
    return format_date(value, format_str)


def format_number(
    value: float | int | None,
    decimal_places: int = 2,
    thousands_sep: str = ".",
    decimal_sep: str = ",",
) -> str:
    """Format a number with custom separators.

    Args:
        value: Numeric value to format.
        decimal_places: Number of decimal places.
        thousands_sep: Thousands separator.
        decimal_sep: Decimal separator.

    Returns:
        Formatted number string.
    """
    if value is None:
        return ""

    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)

    formatted = f"{num:,.{decimal_places}f}"
    formatted = formatted.replace(",", "TEMP")
    formatted = formatted.replace(".", decimal_sep)
    formatted = formatted.replace("TEMP", thousands_sep)

    return formatted


def format_percentage(
    value: float | int | None,
    decimal_places: int = 1,
    multiply: bool = False,
) -> str:
    """Format a value as percentage.

    Args:
        value: Numeric value.
        decimal_places: Number of decimal places.
        multiply: If True, multiply by 100 (for decimal percentages).

    Returns:
        Formatted percentage string.
    """
    if value is None:
        return ""

    try:
        num = float(value)
        if multiply:
            num *= 100
    except (ValueError, TypeError):
        return str(value)

    return f"{num:.{decimal_places}f}%"


def truncate_text(
    value: str | None,
    length: int = 100,
    suffix: str = "...",
    preserve_words: bool = True,
) -> str:
    """Truncate text to a maximum length.

    Args:
        value: Text to truncate.
        length: Maximum length.
        suffix: Suffix to add when truncated.
        preserve_words: Don't cut words in the middle.

    Returns:
        Truncated text.
    """
    if value is None:
        return ""

    value = str(value)

    if len(value) <= length:
        return value

    if preserve_words:
        truncated = value[: length - len(suffix)]
        # Find last space
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        return truncated + suffix

    return value[: length - len(suffix)] + suffix


def nl2br(value: str | None) -> str:
    """Convert newlines to HTML <br> tags.

    Args:
        value: Text with newlines.

    Returns:
        Text with <br> tags.
    """
    if value is None:
        return ""
    return str(value).replace("\n", "<br>\n")


def default_if_none(value: Any, default: Any = "") -> Any:
    """Return default value if value is None.

    Args:
        value: Value to check.
        default: Default value to return.

    Returns:
        Original value or default.
    """
    return default if value is None else value


def dict_get(value: dict | None, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary.

    Args:
        value: Dictionary.
        key: Key to get.
        default: Default value if key not found.

    Returns:
        Value from dictionary or default.
    """
    if value is None or not isinstance(value, dict):
        return default
    return value.get(key, default)


def register_default_filters(env: Environment) -> None:
    """Register all default filters with a Jinja2 environment.

    Args:
        env: Jinja2 Environment instance.
    """
    filters = {
        # Formatting
        "currency": format_currency,
        "format_date": format_date,
        "format_datetime": format_datetime,
        "format_number": format_number,
        "percentage": format_percentage,
        # Text manipulation
        "truncate_text": truncate_text,
        "nl2br": nl2br,
        # Utilities
        "default_if_none": default_if_none,
        "dict_get": dict_get,
    }

    env.filters.update(filters)
    
    # Register globals (functions available in templates)
    env.globals["now"] = datetime.now
