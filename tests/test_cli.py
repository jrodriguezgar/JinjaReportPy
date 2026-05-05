"""Tests for CLI package (output, base, commands)."""

import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from jinjareportpy.cli.base import CLIBase, CLIConfig, Subcommand, create_cli
from jinjareportpy.cli.commands import get_parser, main
from jinjareportpy.cli.output import (
    Colors,
    LogLevel,
    OutputFormat,
    confirm_action,
    cprint,
    print_summary,
    print_table,
)


class TestColors:
    """Tests for Colors class."""

    def test_has_reset(self) -> None:
        assert hasattr(Colors, "RESET")

    def test_semantic_aliases(self) -> None:
        assert hasattr(Colors, "SUCCESS")
        assert hasattr(Colors, "ERROR")
        assert hasattr(Colors, "WARNING")
        assert hasattr(Colors, "INFO")


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_values(self) -> None:
        assert OutputFormat.TABLE.value == "table"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.QUIET.value == "quiet"


class TestLogLevel:
    """Tests for LogLevel enum."""

    def test_values(self) -> None:
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.ERROR.value == "error"


class TestPrintFunctions:
    """Tests for print helper functions."""

    def test_cprint_no_crash(self) -> None:
        buf = StringIO()
        cprint("hello", file=buf)
        assert "hello" in buf.getvalue()

    def test_print_table_empty(self) -> None:
        # Should not crash on empty input
        print_table([], [])

    def test_print_table_with_data(self, capsys: pytest.CaptureFixture) -> None:
        print_table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]])
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out

    def test_print_summary(self, capsys: pytest.CaptureFixture) -> None:
        print_summary({"total": 42, "errors": 0})
        captured = capsys.readouterr()
        assert "Total" in captured.out

    def test_confirm_action_default_no(self) -> None:
        with patch("builtins.input", return_value=""):
            assert confirm_action("Continue?", default=False) is False

    def test_confirm_action_yes(self) -> None:
        with patch("builtins.input", return_value="y"):
            assert confirm_action("Continue?") is True


class TestCLIConfig:
    """Tests for CLIConfig dataclass."""

    def test_defaults(self) -> None:
        cfg = CLIConfig()
        assert cfg.prog_name == "jinjareportpy"
        assert cfg.default_output_format == OutputFormat.SUMMARY


class TestSubcommand:
    """Tests for Subcommand dataclass."""

    def test_creation(self) -> None:
        sub = Subcommand(name="test", help="A test command")
        assert sub.name == "test"
        assert sub.handler is None
        assert sub.aliases == []


class TestCLIBase:
    """Tests for CLIBase class."""

    def test_create_instance(self) -> None:
        cli = CLIBase(prog="test", description="Test CLI", version="0.1.0")
        assert cli.parser is not None
        assert cli.config.prog_name == "test"

    def test_add_subcommand(self) -> None:
        cli = CLIBase(prog="test", description="Test")
        cli.init_subcommands()
        parser = cli.add_subcommand("sub1", "A subcommand")
        assert parser is not None

    def test_increment_stat(self) -> None:
        cli = CLIBase(prog="test", description="Test")
        cli.increment_stat("processed", 5)
        cli.increment_stat("processed", 3)
        assert cli.stats["processed"] == 8


class TestCreateCli:
    """Tests for create_cli factory."""

    def test_basic(self) -> None:
        cli = create_cli("myapp", "My application")
        assert cli.config.prog_name == "myapp"

    def test_with_database_connection(self) -> None:
        cli = create_cli("myapp", "My app", connection_type="database")
        assert "db_connection" in cli._groups


class TestGetParser:
    """Tests for get_parser."""

    def test_returns_parser(self) -> None:
        parser = get_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_has_subcommands(self) -> None:
        parser = get_parser()
        # Parsing with no args should not raise
        args = parser.parse_args([])
        assert args.command is None


class TestMainEntryPoint:
    """Tests for main() function."""

    def test_no_args_returns_zero(self) -> None:
        result = main([])
        assert result == 0

    def test_version_flag(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
