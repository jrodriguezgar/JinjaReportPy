"""Tests for ReportGenerator class."""

import pytest
from pathlib import Path
import tempfile

from jinjareportpy import ReportGenerator, ReportConfig, PageSize, Orientation
from jinjareportpy.exceptions import TemplateNotFoundError, ExportError


class TestReportConfig:
    """Tests for ReportConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ReportConfig()
        assert config.page_size == PageSize.A4
        assert config.orientation == Orientation.PORTRAIT
        assert config.encoding == "utf-8"
        assert config.locale == "es_ES"

    def test_page_size_dimensions(self) -> None:
        """Test page size dimensions."""
        assert PageSize.A4.width == "210mm"
        assert PageSize.A4.height == "297mm"
        assert PageSize.LETTER.width == "8.5in"

    def test_effective_page_size_portrait(self) -> None:
        """Test effective page size in portrait mode."""
        config = ReportConfig(page_size=PageSize.A4, orientation=Orientation.PORTRAIT)
        width, height = config.effective_page_size
        assert width == "210mm"
        assert height == "297mm"

    def test_effective_page_size_landscape(self) -> None:
        """Test effective page size in landscape mode."""
        config = ReportConfig(page_size=PageSize.A4, orientation=Orientation.LANDSCAPE)
        width, height = config.effective_page_size
        assert width == "297mm"
        assert height == "210mm"


class TestReportGenerator:
    """Tests for ReportGenerator."""

    def test_create_generator(self) -> None:
        """Test creating a generator with default config."""
        generator = ReportGenerator()
        assert generator.config is not None
        assert generator.config.page_size == PageSize.A4

    def test_create_generator_with_config(self) -> None:
        """Test creating a generator with custom config."""
        config = ReportConfig(page_size=PageSize.LETTER)
        generator = ReportGenerator(config)
        assert generator.config.page_size == PageSize.LETTER

    def test_render_string(self) -> None:
        """Test rendering a template from string."""
        generator = ReportGenerator()
        html = generator.render_string(
            "<h1>{{ title }}</h1>",
            {"title": "Test Report"}
        )
        assert "<h1>Test Report</h1>" in html

    def test_render_string_with_filters(self) -> None:
        """Test rendering with custom filters."""
        generator = ReportGenerator()
        html = generator.render_string(
            "{{ amount | currency }}",
            {"amount": 1234.56}
        )
        assert "1.234,56" in html
        assert "€" in html

    def test_add_custom_filter(self) -> None:
        """Test adding a custom filter."""
        generator = ReportGenerator()
        generator.add_filter("reverse", lambda s: s[::-1])
        html = generator.render_string("{{ 'hello' | reverse }}")
        assert "olleh" in html

    def test_add_global(self) -> None:
        """Test adding a global variable."""
        generator = ReportGenerator()
        generator.add_global("company", "Acme Corp")
        html = generator.render_string("{{ company }}")
        assert "Acme Corp" in html

    def test_export_html(self) -> None:
        """Test exporting HTML to file."""
        generator = ReportGenerator()
        html = generator.render_string("<h1>Test</h1>")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.html"
            result = generator.export_html(html, output_path)
            
            assert result.exists()
            assert result.read_text(encoding="utf-8") == html

    def test_export_without_render_raises_error(self) -> None:
        """Test that export without render raises error."""
        generator = ReportGenerator()
        
        with pytest.raises(ExportError):
            generator.export_html()

    def test_builtin_templates(self) -> None:
        """Test that built-in templates are available."""
        generator = ReportGenerator()
        
        # The base template should be available
        html = generator.render("report.html", {
            "title": "Test Report",
            "headers": ["Col1", "Col2"],
            "data": [["A", "B"], ["C", "D"]]
        })
        
        assert "Test Report" in html
        assert "<table" in html

    def test_is_pdf_available(self) -> None:
        """Test PDF availability check."""
        # This should return True or False without error
        result = ReportGenerator.is_pdf_available()
        assert isinstance(result, bool)


class TestFilters:
    """Tests for custom Jinja2 filters."""

    @pytest.fixture
    def generator(self) -> ReportGenerator:
        return ReportGenerator()

    def test_currency_filter(self, generator: ReportGenerator) -> None:
        """Test currency formatting filter."""
        html = generator.render_string("{{ 1234.56 | currency }}")
        assert "1.234,56" in html
        assert "€" in html

    def test_date_filter(self, generator: ReportGenerator) -> None:
        """Test date formatting filter."""
        from datetime import date
        html = generator.render_string(
            "{{ d | format_date }}",
            {"d": date(2025, 1, 15)}
        )
        assert "15/01/2025" in html

    def test_percentage_filter(self, generator: ReportGenerator) -> None:
        """Test percentage formatting filter."""
        html = generator.render_string("{{ 0.156 | percentage(multiply=True) }}")
        assert "15.6%" in html

    def test_truncate_filter(self, generator: ReportGenerator) -> None:
        """Test text truncation filter."""
        html = generator.render_string(
            "{{ text | truncate_text(20) }}",
            {"text": "This is a very long text that should be truncated"}
        )
        assert "..." in html
        assert len(html.strip()) <= 25  # 20 chars + "..." + some buffer

    def test_nl2br_filter(self, generator: ReportGenerator) -> None:
        """Test newline to BR filter."""
        html = generator.render_string(
            "{{ text | nl2br }}",
            {"text": "Line 1\nLine 2"}
        )
        assert "<br>" in html

    def test_default_if_none_filter(self, generator: ReportGenerator) -> None:
        """Test default_if_none filter."""
        html = generator.render_string(
            "{{ value | default_if_none('N/A') }}",
            {"value": None}
        )
        assert "N/A" in html
