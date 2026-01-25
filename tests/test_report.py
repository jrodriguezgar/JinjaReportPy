"""Tests for Report, Page and Section classes."""

import pytest
from pathlib import Path
import tempfile

from jinjareportpy import (
    Report,
    Page,
    Section,
    HeaderSection,
    FooterSection,
    TableSection,
    KPISection,
    TextSection,
)


class TestSection:
    """Tests for Section class."""

    def test_create_section(self) -> None:
        """Test creating a basic section."""
        section = Section(name="test")
        assert section.name == "test"
        assert section.template == ""
        assert section.data == {}

    def test_render_section(self) -> None:
        """Test rendering a section with data."""
        section = Section(
            name="greeting",
            template="<h1>{{ title }}</h1>",
            data={"title": "Hello World"},
        )
        html = section.render()
        assert "Hello World" in html
        assert 'class="section section-greeting"' in html

    def test_section_with_css(self) -> None:
        """Test section CSS rendering."""
        section = Section(
            name="styled",
            template="<p>Content</p>",
            css=".styled { color: red; }",
        )
        css = section.render_css()
        assert "Section: styled" in css
        assert "color: red" in css

    def test_empty_template(self) -> None:
        """Test section with empty template."""
        section = Section(name="empty")
        assert section.render() == ""


class TestHeaderSection:
    """Tests for HeaderSection."""

    def test_default_header(self) -> None:
        """Test creating header with defaults."""
        header = HeaderSection(title="Test", subtitle="Subtitle")
        html = header.render()
        assert "Test" in html
        assert "Subtitle" in html

    def test_header_with_logo(self) -> None:
        """Test header with logo."""
        header = HeaderSection(title="Test", logo="data:image/png;base64,...")
        html = header.render()
        assert "<img" in html


class TestFooterSection:
    """Tests for FooterSection."""

    def test_default_footer(self) -> None:
        """Test creating footer with defaults."""
        footer = FooterSection(left_text="Left", right_text="Right")
        html = footer.render()
        assert "Left" in html
        assert "Right" in html


class TestTableSection:
    """Tests for TableSection."""

    def test_table_section(self) -> None:
        """Test creating a table section."""
        table = TableSection(
            name="data",
            headers=["A", "B"],
            rows=[["1", "2"], ["3", "4"]],
        )
        html = table.render()
        assert "<table>" in html
        assert "<th>A</th>" in html
        assert "<td>1</td>" in html

    def test_table_with_footer(self) -> None:
        """Test table with footer row."""
        table = TableSection(
            name="totals",
            headers=["Item", "Total"],
            rows=[["A", "100"]],
            footer_row=["Sum", "100"],
        )
        html = table.render()
        assert "<tfoot>" in html
        assert "Sum" in html


class TestKPISection:
    """Tests for KPISection."""

    def test_kpi_section(self) -> None:
        """Test creating KPI section."""
        kpis = KPISection(
            name="metrics",
            kpis=[
                {"label": "Sales", "value": "1000"},
                {"label": "Users", "value": "50"},
            ],
        )
        html = kpis.render()
        assert "Sales" in html
        assert "1000" in html
        assert "kpi-card" in html


class TestPage:
    """Tests for Page class."""

    def test_create_page(self) -> None:
        """Test creating an empty page."""
        page = Page()
        assert page.header is None
        assert page.footer is None
        assert page.sections == []

    def test_set_header(self) -> None:
        """Test setting page header."""
        page = Page()
        page.set_header(title="Test", subtitle="Sub")
        assert page.header is not None
        assert page.header.data["title"] == "Test"

    def test_set_footer(self) -> None:
        """Test setting page footer."""
        page = Page()
        page.set_footer(left_text="Left", right_text="Right")
        assert page.footer is not None

    def test_add_section(self) -> None:
        """Test adding sections to page."""
        page = Page()
        page.add_section(Section(name="s1", template="<p>1</p>"))
        page.add_section(name="s2", template="<p>2</p>")
        assert len(page.sections) == 2

    def test_method_chaining(self) -> None:
        """Test fluent API chaining."""
        page = (
            Page()
            .set_header(title="Title")
            .set_footer(left_text="Footer")
            .add_section(name="content", template="<p>Hello</p>")
        )
        assert page.header is not None
        assert page.footer is not None
        assert len(page.sections) == 1

    def test_render_page(self) -> None:
        """Test rendering complete page."""
        page = Page()
        page.set_header(title="Test")
        page.add_section(Section(name="body", template="<p>Content</p>"))
        html = page.render()
        assert 'class="page"' in html
        assert "Test" in html
        assert "Content" in html


class TestReport:
    """Tests for Report class."""

    def test_create_report(self) -> None:
        """Test creating an empty report."""
        report = Report(title="Test Report")
        assert report.title == "Test Report"
        assert report.pages == []

    def test_add_page(self) -> None:
        """Test adding pages to report."""
        report = Report()
        page1 = report.add_page()
        page2 = report.add_page()
        assert len(report.pages) == 2
        assert page1.page_number == 1
        assert page2.page_number == 2

    def test_render_report(self) -> None:
        """Test rendering complete report."""
        report = Report(title="My Report")
        page = report.add_page()
        page.set_header(title="Header")
        page.add_section(Section(name="content", template="<p>Hello</p>"))

        html = report.render()
        assert "<!DOCTYPE html>" in html
        assert "<title>My Report</title>" in html
        assert "Header" in html
        assert "Hello" in html

    def test_export_html(self) -> None:
        """Test exporting report to HTML."""
        report = Report(title="Export Test")
        page = report.add_page()
        page.add_section(Section(name="test", template="<p>Test</p>"))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.html"
            result = report.export_html(path)
            assert result.exists()
            content = result.read_text()
            assert "Export Test" in content

    def test_report_css_collection(self) -> None:
        """Test that CSS is collected from all sections."""
        report = Report()
        report.global_css = ".global { color: blue; }"

        page = report.add_page()
        page.add_section(Section(
            name="styled",
            template="<p>Text</p>",
            css=".custom { color: red; }",
        ))

        css = report.render_css()
        assert ".global" in css
        assert ".custom" in css

    def test_multiple_pages(self) -> None:
        """Test report with multiple pages."""
        report = Report(title="Multi-Page")

        page1 = report.add_page()
        page1.add_section(Section(name="p1", template="<p>Page 1</p>"))

        page2 = report.add_page()
        page2.add_section(Section(name="p2", template="<p>Page 2</p>"))

        html = report.render()
        assert "Page 1" in html
        assert "Page 2" in html
        assert html.count('class="page"') == 2
