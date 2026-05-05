"""Tests for Jinja2 custom filters."""

from unittest.mock import patch

from jinjareportpy.filters import (
    default_if_none,
    dict_get,
    format_currency,
    format_date,
    format_number,
    format_percentage,
    nl2br,
    truncate_text,
)


class TestFormatNumber:
    """Tests for format_number filter."""

    def test_basic_integer(self) -> None:
        # Default: European format (. thousands, , decimal, 2 dp)
        assert format_number(1234) == "1.234,00"

    def test_with_decimal_places(self) -> None:
        assert format_number(1234.5, decimal_places=2) == "1.234,50"

    def test_zero(self) -> None:
        assert format_number(0) == "0,00"

    def test_negative(self) -> None:
        result = format_number(-1500.75, decimal_places=2)
        assert result == "-1.500,75"

    def test_none_returns_empty(self) -> None:
        assert format_number(None) == ""

    def test_custom_separators(self) -> None:
        result = format_number(1234.5, thousands_sep=",", decimal_sep=".")
        assert result == "1,234.50"


class TestFormatCurrency:
    """Tests for format_currency filter."""

    def test_default_euro(self) -> None:
        result = format_currency(1234.56)
        assert result == "1.234,56 €"

    def test_custom_symbol(self) -> None:
        result = format_currency(99.99, symbol="$")
        assert result == "99,99 $"

    def test_symbol_before(self) -> None:
        result = format_currency(99.99, symbol="$", symbol_after=False)
        assert result == "$ 99,99"

    def test_none_returns_empty(self) -> None:
        assert format_currency(None) == ""

    def test_zero(self) -> None:
        result = format_currency(0)
        assert result == "0,00 €"


class TestFormatDate:
    """Tests for format_date filter."""

    def test_none_returns_empty(self) -> None:
        assert format_date(None) == ""

    def test_string_passthrough(self) -> None:
        result = format_date("2025-01-15")
        assert isinstance(result, str)
        assert result  # not empty

    def test_iso_datetime_parsed(self) -> None:
        result = format_date("2025-01-15T10:30:00")
        assert result == "15/01/2025"

    def test_iso_datetime_no_seconds(self) -> None:
        result = format_date("2025-01-15T10:30")
        assert result == "15/01/2025"

    def test_unparseable_returns_original(self) -> None:
        result = format_date("not-a-date")
        assert result == "not-a-date"


class TestFormatPercentage:
    """Tests for format_percentage filter."""

    def test_basic_no_multiply(self) -> None:
        result = format_percentage(75)
        assert result == "75.0%"

    def test_with_multiply(self) -> None:
        result = format_percentage(0.75, multiply=True)
        assert result == "75.0%"

    def test_none_returns_empty(self) -> None:
        assert format_percentage(None) == ""


class TestTruncateText:
    """Tests for truncate_text filter."""

    def test_short_text_unchanged(self) -> None:
        assert truncate_text("Hello", 100) == "Hello"

    def test_long_text_truncated(self) -> None:
        result = truncate_text("A" * 200, 50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_none_returns_empty(self) -> None:
        assert truncate_text(None, 50) == ""


class TestNl2br:
    """Tests for nl2br filter."""

    def test_newlines_to_br(self) -> None:
        result = nl2br("line1\nline2")
        assert "<br>" in result
        assert "line1" in result
        assert "line2" in result

    def test_none_returns_empty(self) -> None:
        assert nl2br(None) == ""

    def test_no_newlines(self) -> None:
        assert nl2br("hello") == "hello"

    def test_html_is_escaped(self) -> None:
        result = nl2br("<script>alert(1)</script>\ntext")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        assert "<br>" in result


class TestDefaultIfNone:
    """Tests for default_if_none filter."""

    def test_none_returns_default(self) -> None:
        assert default_if_none(None, "fallback") == "fallback"

    def test_value_returned(self) -> None:
        assert default_if_none("actual", "fallback") == "actual"

    def test_zero_not_replaced(self) -> None:
        assert default_if_none(0, "fallback") == 0

    def test_empty_string_not_replaced(self) -> None:
        assert default_if_none("", "fallback") == ""


class TestDictGet:
    """Tests for dict_get filter."""

    def test_existing_key(self) -> None:
        assert dict_get({"a": 1}, "a") == 1

    def test_missing_key(self) -> None:
        assert dict_get({"a": 1}, "b") is None

    def test_missing_key_with_default(self) -> None:
        assert dict_get({"a": 1}, "b", "fallback") == "fallback"

    def test_none_dict(self) -> None:
        assert dict_get(None, "a") is None

    def test_non_dict(self) -> None:
        assert dict_get("not a dict", "a") is None


class TestLocaleAwareDefaults:
    """Verify filters pick separators from JinjaReportConfig locale."""

    @patch("jinjareportpy.filters.get_locale", return_value="en_US")
    def test_format_number_uses_english_separators(self, _mock: object) -> None:
        result = format_number(1234.5)
        assert result == "1,234.50"

    @patch("jinjareportpy.filters.get_locale", return_value="es_ES")
    def test_format_number_uses_spanish_separators(self, _mock: object) -> None:
        result = format_number(1234.5)
        assert result == "1.234,50"

    @patch("jinjareportpy.filters.get_locale", return_value="en_US")
    def test_format_currency_uses_english_separators(self, _mock: object) -> None:
        result = format_currency(1234.56, symbol="$", symbol_after=False)
        assert result == "$ 1,234.56"

    def test_explicit_separators_override_locale(self) -> None:
        result = format_number(1234.5, thousands_sep=" ", decimal_sep=".")
        assert result == "1 234.50"


class TestFormatNumberNonFinite:
    """Verify format_number handles inf/nan gracefully."""

    def test_inf_returns_zero(self) -> None:
        result = format_number(float("inf"))
        assert "inf" not in result.lower()

    def test_negative_inf_returns_zero(self) -> None:
        result = format_number(float("-inf"))
        assert "inf" not in result.lower()

    def test_nan_returns_zero(self) -> None:
        result = format_number(float("nan"))
        assert "nan" not in result.lower()
