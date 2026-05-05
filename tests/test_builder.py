"""Tests for ReportBuilder fluent API."""

from pathlib import Path

from jinjareportpy.builder import (
    FooterConfig,
    HeaderConfig,
    ReportBuilder,
)
from jinjareportpy.sections import Section


class TestHeaderConfig:
    """Tests for HeaderConfig dataclass."""

    def test_defaults(self) -> None:
        cfg = HeaderConfig()
        assert cfg.title == ""
        assert cfg.subtitle == ""

    def test_to_dict_includes_date(self) -> None:
        cfg = HeaderConfig(title="Report")
        d = cfg.to_dict()
        assert d["title"] == "Report"
        assert "date" in d
        assert d["date"]  # non-empty


class TestFooterConfig:
    """Tests for FooterConfig dataclass."""

    def test_to_dict(self) -> None:
        cfg = FooterConfig(left="Company", right="Page 1")
        d = cfg.to_dict()
        assert d["left_text"] == "Company"
        assert d["right_text"] == "Page 1"


class TestReportBuilder:
    """Tests for ReportBuilder fluent API."""

    def test_create_builder(self) -> None:
        builder = ReportBuilder("Test Report")
        assert builder is not None

    def test_fluent_chaining(self) -> None:
        builder = (
            ReportBuilder("Test")
            .header(title="Header")
            .footer(left="Left")
            .add_text("notes", "Some text")
        )
        assert builder is not None

    def test_build_returns_report(self) -> None:
        builder = ReportBuilder("Test Report")
        builder.header(title="Header")
        builder.add_text("content", "Hello world")
        report = builder.build()
        assert report.title == "Test Report"
        assert len(report.pages) >= 1

    def test_render_produces_html(self) -> None:
        builder = (
            ReportBuilder("Test")
            .header(title="Title")
            .add_text("body", "Content here")
        )
        html = builder.render()
        assert "<html" in html.lower() or "Content here" in html

    def test_add_table(self) -> None:
        builder = ReportBuilder("Test")
        builder.add_table(
            "data",
            headers=["A", "B"],
            rows=[["1", "2"]],
        )
        report = builder.build()
        assert len(report.pages) >= 1

    def test_add_kpis(self) -> None:
        builder = ReportBuilder("Test")
        builder.add_kpis(
            "metrics",
            [{"label": "Sales", "value": "100", "change": 5}],
        )
        report = builder.build()
        assert len(report.pages) >= 1

    def test_add_section(self) -> None:
        builder = ReportBuilder("Test")
        section = Section(name="custom", template="<p>Custom</p>")
        builder.add_section(section)
        report = builder.build()
        assert len(report.pages) >= 1

    def test_css_method(self) -> None:
        builder = ReportBuilder("Test")
        builder.css("body { color: red; }")
        html = builder.render()
        assert "color: red" in html

    def test_export_html(self, tmp_path: Path) -> None:
        builder = (
            ReportBuilder("Test")
            .header(title="Header")
            .add_text("body", "Export test")
        )
        output = tmp_path / "test_report.html"
        result = builder.export_html(str(output))
        assert Path(result).exists()
        content = Path(result).read_text(encoding="utf-8")
        assert "Export test" in content
