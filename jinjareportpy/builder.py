"""
ReportBuilder - Fluent API for creating reports in a few lines of code.

Encapsulates complexity by allowing separation of data from layout
and generating easily configurable reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
import re

from .report import Report
from .page import Page
from .sections import (
    Section,
    HeaderSection,
    FooterSection,
    TableSection,
    TextSection,
    KPISection,
)
from .formats import get_default_format


# ============================================
# Simple section configurations
# ============================================

@dataclass
class HeaderConfig:
    """Header configuration.
    
    Example:
        >>> header = HeaderConfig(title="Report", subtitle="2025")
    """
    title: str = ""
    subtitle: str = ""
    logo: str = ""
    date: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "logo": self.logo,
            "date": self.date or datetime.now().strftime("%Y-%m-%d"),
        }


@dataclass
class FooterConfig:
    """Footer configuration.
    
    Supports left, center, and right text areas.
    
    Example:
        >>> footer = FooterConfig(left="Company", center="Draft", right="Page {page}")
    """
    left: str = ""
    center: str = ""
    right: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "left_text": self.left,
            "center_text": self.center,
            "right_text": self.right,
        }


@dataclass
class TableConfig:
    """Table configuration.
    
    Example:
        >>> table = TableConfig(
        ...     title="Sales",
        ...     headers=["Product", "Quantity"],
        ...     rows=[["A", 100], ["B", 200]],
        ...     footer=["Total", 300]
        ... )
    """
    headers: list[str] = field(default_factory=list)
    rows: list[list[Any]] = field(default_factory=list)
    title: str = ""
    footer: list[Any] | None = None
    
    def to_section(self, name: str = "table", format_name: str | None = None) -> TableSection:
        return TableSection(
            name=name,
            headers=self.headers,
            rows=self.rows,
            title=self.title,
            footer_row=self.footer,
            format_name=format_name,
        )


@dataclass
class KPIConfig:
    """KPI indicators configuration.
    
    Example:
        >>> kpis = KPIConfig(
        ...     title="Metrics",
        ...     items=[
        ...         {"label": "Sales", "value": "£50K", "change": "+15%"},
        ...         {"label": "Customers", "value": "1,234"},
        ...     ]
        ... )
    """
    items: list[dict[str, Any]] = field(default_factory=list)
    title: str = ""
    
    def add(
        self,
        label: str,
        value: str,
        change: str = "",
        description: str = "",
        color: str = "",
    ) -> "KPIConfig":
        """Add a KPI to the list."""
        self.items.append({
            "label": label,
            "value": value,
            "change": change,
            "description": description,
            "color_class": color,
        })
        return self
    
    def to_section(self, name: str = "kpis", format_name: str | None = None) -> KPISection:
        return KPISection(
            name=name,
            kpis=self.items,
            title=self.title,
            format_name=format_name,
        )


@dataclass
class TextConfig:
    """Text configuration.
    
    Example:
        >>> text = TextConfig(title="Summary", content="Report content...")
    """
    content: str = ""
    title: str = ""
    
    def to_section(self, name: str = "text", format_name: str | None = None) -> TextSection:
        return TextSection(
            name=name,
            content=self.content,
            title=self.title,
            format_name=format_name,
        )


# ============================================
# Layout: report structure
# ============================================

@dataclass
class PageLayout:
    """Page layout configuration.
    
    Example:
        >>> layout = PageLayout(
        ...     header=HeaderConfig(title="My Report"),
        ...     footer=FooterConfig(right="Page {page}"),
        ...     sections=["kpis", "sales_table", "summary"]
        ... )
    """
    header: HeaderConfig | None = None
    footer: FooterConfig | None = None
    sections: list[str] = field(default_factory=list)  # Section names to include


@dataclass
class ReportLayout:
    """Complete report layout configuration.
    
    Example:
        >>> layout = ReportLayout(
        ...     format_name="corporate",
        ...     header=HeaderConfig(title="Global Report"),
        ...     footer=FooterConfig(left="Company Ltd."),
        ...     pages=[
        ...         PageLayout(sections=["kpis", "table"]),
        ...         PageLayout(sections=["chart", "summary"]),
        ...     ]
        ... )
    """
    format_name: str | None = None
    header: HeaderConfig | None = None  # Default header for all pages
    footer: FooterConfig | None = None  # Default footer for all pages
    pages: list[PageLayout] = field(default_factory=list)  # If empty, single page
    global_css: str = ""


# ============================================
# ReportBuilder - Fluent API
# ============================================

class ReportBuilder:
    """Fluent report builder.
    
    Allows creating reports by separating data from layout in a few lines.
    
    Example:
        >>> # Create report in a few lines
        >>> builder = ReportBuilder("Sales Report", format_name="corporate")
        >>> builder.header(title="Q4 Sales", subtitle="2025")
        >>> builder.footer(left="Company", center="Draft", right="Page {page}")
        >>> builder.add_kpis("metrics", [
        ...     {"label": "Total", "value": "£100K"},
        ... ])
        >>> builder.add_table("sales", 
        ...     headers=["Product", "Quantity"],
        ...     rows=[["A", 100], ["B", 200]]
        ... )
        >>> html = builder.build()
        
        >>> # Or using data + layout separated
        >>> data = {"sales": [...], "kpis": [...]}
        >>> layout = ReportLayout(format_name="minimal")
        >>> html = ReportBuilder.from_data_layout(data, layout)
    """
    
    def __init__(
        self,
        title: str = "Report",
        format_name: str | None = None,
    ):
        """Initialize the report builder.
        
        Args:
            title: Report title.
            format_name: Format to use (None = active format).
        """
        self.title = title
        self.format_name = format_name or get_default_format()
        
        self._header_config: HeaderConfig | None = None
        self._footer_config: FooterConfig | None = None
        self._sections: list[tuple[str, Section | TableConfig | KPIConfig | TextConfig]] = []
        self._global_css: str = ""
        
    # ---- Header Configuration ----
    
    def header(
        self,
        title: str = "",
        subtitle: str = "",
        logo: str = "",
        date: str = "",
    ) -> "ReportBuilder":
        """Configure the report header.
        
        Args:
            title: Main title.
            subtitle: Subtitle text.
            logo: URL or Base64 string for logo.
            date: Date string (empty = current date).
            
        Returns:
            Self for method chaining.
        """
        self._header_config = HeaderConfig(
            title=title,
            subtitle=subtitle,
            logo=logo,
            date=date,
        )
        return self
    
    # ---- Footer Configuration ----
    
    def footer(
        self,
        left: str = "",
        center: str = "",
        right: str = "",
    ) -> "ReportBuilder":
        """Configure the report footer.
        
        Args:
            left: Left-aligned text.
            center: Center-aligned text.
            right: Right-aligned text.
            
        Returns:
            Self for method chaining.
        """
        self._footer_config = FooterConfig(
            left=left,
            center=center,
            right=right,
        )
        return self
    
    # ---- Add Sections ----
    
    def add_table(
        self,
        name: str,
        headers: list[str],
        rows: list[list[Any]],
        title: str = "",
        footer: list[Any] | None = None,
    ) -> "ReportBuilder":
        """Add a table to the report.
        
        Args:
            name: Unique identifier.
            headers: Column headers.
            rows: Data rows.
            title: Table title.
            footer: Footer row (e.g., totals).
            
        Returns:
            Self for method chaining.
        """
        config = TableConfig(
            headers=headers,
            rows=rows,
            title=title,
            footer=footer,
        )
        self._sections.append((name, config))
        return self
    
    def add_kpis(
        self,
        name: str,
        kpis: list[dict[str, Any]],
        title: str = "",
    ) -> "ReportBuilder":
        """Add KPI indicators to the report.
        
        Args:
            name: Unique identifier.
            kpis: List of KPIs with label, value, change, etc.
            title: Section title.
            
        Returns:
            Self for method chaining.
        """
        config = KPIConfig(items=kpis, title=title)
        self._sections.append((name, config))
        return self
    
    def add_text(
        self,
        name: str,
        content: str,
        title: str = "",
    ) -> "ReportBuilder":
        """Add text to the report.
        
        Args:
            name: Unique identifier.
            content: Text content (can include HTML).
            title: Section title.
            
        Returns:
            Self for method chaining.
        """
        config = TextConfig(content=content, title=title)
        self._sections.append((name, config))
        return self
    
    def add_section(self, section: Section) -> "ReportBuilder":
        """Add a custom section.
        
        Args:
            section: Section object with custom template/CSS.
            
        Returns:
            Self for method chaining.
        """
        self._sections.append((section.name, section))
        return self
    
    def css(self, css: str) -> "ReportBuilder":
        """Add additional global CSS.
        
        Args:
            css: CSS styles.
            
        Returns:
            Self for method chaining.
        """
        self._global_css += f"\n{css}"
        return self
    
    # ---- Building ----
    
    def build(self) -> Report:
        """Build the Report object.
        
        Returns:
            Configured Report ready for rendering.
        """
        report = Report(
            title=self.title,
            format_name=self.format_name,
            global_css=self._global_css.strip(),
        )
        
        page = report.add_page()
        
        # Header
        if self._header_config:
            page.set_header(**self._header_config.to_dict())
        
        # Footer
        if self._footer_config:
            page.set_footer(**self._footer_config.to_dict())
        
        # Sections
        for name, config in self._sections:
            if isinstance(config, TableConfig):
                page.add_section(config.to_section(name, self.format_name))
            elif isinstance(config, KPIConfig):
                page.add_section(config.to_section(name, self.format_name))
            elif isinstance(config, TextConfig):
                page.add_section(config.to_section(name, self.format_name))
            elif isinstance(config, Section):
                page.add_section(config)
        
        return report
    
    def render(self) -> str:
        """Generate the report HTML.
        
        Returns:
            Complete HTML of the report.
        """
        return self.build().render()
    
    def render_inline(self) -> str:
        """Generate HTML with inline styles, ideal for emails.
        
        Converts CSS classes to inline styles for maximum
        compatibility with email clients.
        
        Returns:
            HTML with embedded styles.
        """
        return _inline_styles(self.render())
    
    def to_clipboard_html(self) -> str:
        """Generate HTML optimized for clipboard copying.
        
        Extracts only the content (without <html>, <head>) with inline styles.
        Returns the HTML as a string - does NOT copy to clipboard.
        
        Returns:
            Body HTML content with inline styles as a string.
        """
        html = self.render_inline()
        # Extract only the body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        if body_match:
            return body_match.group(1).strip()
        return html
    
    def export_html(self, path: Path | str) -> Path:
        """Export to HTML file.
        
        Args:
            path: File path.
            
        Returns:
            Path to the created file.
        """
        return self.build().export_html(path)
    
    def export_pdf(self, path: Path | str) -> Path:
        """Export to PDF file.
        
        Args:
            path: File path.
            
        Returns:
            Path to the created file.
        """
        return self.build().export_pdf(path)
    
    def preview(self, browser: str | None = None) -> Path:
        """Open the report in a web browser.
        
        Args:
            browser: Browser command (None = system default).
            
        Returns:
            Path to the temporary HTML file.
        """
        return self.build().preview(browser)
    
    # ---- Class method for data + layout ----
    
    @classmethod
    def from_data_layout(
        cls,
        data: dict[str, Any],
        layout: ReportLayout,
        title: str = "Report",
    ) -> str:
        """Create report from separate data and layout.
        
        Args:
            data: Dictionary with data by section name.
            layout: Report layout configuration.
            title: Report title.
            
        Returns:
            HTML of the generated report.
            
        Example:
            >>> data = {
            ...     "kpis": [{"label": "Sales", "value": "£50K"}],
            ...     "table": {
            ...         "headers": ["Col1", "Col2"],
            ...         "rows": [["A", "B"]],
            ...     },
            ... }
            >>> layout = ReportLayout(
            ...     format_name="corporate",
            ...     header=HeaderConfig(title="Report"),
            ... )
            >>> html = ReportBuilder.from_data_layout(data, layout)
        """
        builder = cls(title=title, format_name=layout.format_name)
        
        # Apply header/footer from layout
        if layout.header:
            builder._header_config = layout.header
        if layout.footer:
            builder._footer_config = layout.footer
        if layout.global_css:
            builder._global_css = layout.global_css
        
        # Process data
        for section_name, section_data in data.items():
            if isinstance(section_data, list) and section_data and isinstance(section_data[0], dict):
                # List of dictionaries -> KPIs
                if all("label" in kpi and "value" in kpi for kpi in section_data):
                    builder.add_kpis(section_name, section_data)
                else:
                    # List of dictionaries -> table
                    if section_data:
                        headers = list(section_data[0].keys())
                        rows = [[row.get(h, "") for h in headers] for row in section_data]
                        builder.add_table(section_name, headers, rows)
            elif isinstance(section_data, dict):
                # Dictionary with headers/rows -> table
                if "headers" in section_data and "rows" in section_data:
                    builder.add_table(
                        section_name,
                        section_data["headers"],
                        section_data["rows"],
                        section_data.get("title", ""),
                        section_data.get("footer"),
                    )
                else:
                    # Simple text
                    builder.add_text(section_name, str(section_data))
            elif isinstance(section_data, str):
                # Text
                builder.add_text(section_name, section_data)
        
        return builder.render()


# ============================================
# Utility functions
# ============================================

def _inline_styles(html: str) -> str:
    """Convert CSS styles to inline for email compatibility.
    
    This is a basic implementation. For production, consider
    using libraries like `premailer` or `css-inline`.
    
    Args:
        html: HTML with styles in <style> tags.
        
    Returns:
        HTML with inline styles.
    """
    # Extract basic CSS rules
    style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    if not style_match:
        return html
    
    css_content = style_match.group(1)
    
    # Apply basic inline styles to body
    # Add common styles directly to main elements
    inline_html = html
    
    # Add inline style to common elements
    inline_replacements = [
        # Tables
        (r'<table([^>]*)>', 
         r'<table\1 style="width:100%;border-collapse:collapse;font-family:Arial,sans-serif;">'),
        # Table headers
        (r'<th([^>]*)>', 
         r'<th\1 style="background:#f0f0f0;padding:8px;text-align:left;border-bottom:2px solid #ddd;">'),
        # Table cells
        (r'<td([^>]*)>', 
         r'<td\1 style="padding:8px;border-bottom:1px solid #eee;">'),
        # Headers
        (r'<h1([^>]*)>', 
         r'<h1\1 style="font-size:24px;color:#333;margin-bottom:10px;">'),
        (r'<h2([^>]*)>', 
         r'<h2\1 style="font-size:18px;color:#333;margin-bottom:8px;">'),
        (r'<h3([^>]*)>', 
         r'<h3\1 style="font-size:14px;color:#333;margin-bottom:6px;">'),
        # Paragraphs
        (r'<p([^>]*)>', 
         r'<p\1 style="margin-bottom:10px;line-height:1.5;">'),
    ]
    
    for pattern, replacement in inline_replacements:
        inline_html = re.sub(pattern, replacement, inline_html)
    
    return inline_html


def quick_report(
    title: str,
    header: dict[str, str] | None = None,
    sections: list[dict[str, Any]] | None = None,
    format_name: str | None = None,
    inline: bool = False,
) -> str:
    """Generate a quick report in a single call.
    
    Args:
        title: Report title.
        header: Header configuration {"title", "subtitle", "date"}.
        sections: List of sections, each with "type" and data.
        format_name: Format to use.
        inline: If True, returns HTML with inline styles.
        
    Returns:
        HTML of the report.
        
    Example:
        >>> html = quick_report(
        ...     title="Summary",
        ...     header={"title": "My Report", "subtitle": "2025"},
        ...     sections=[
        ...         {"type": "kpis", "data": [{"label": "Total", "value": "100"}]},
        ...         {"type": "table", "headers": ["A", "B"], "rows": [["1", "2"]]},
        ...         {"type": "text", "content": "Final notes..."},
        ...     ]
        ... )
    """
    builder = ReportBuilder(title, format_name)
    
    if header:
        builder.header(**header)
    
    if sections:
        for i, section in enumerate(sections):
            section_type = section.get("type", "text")
            name = section.get("name", f"section_{i}")
            
            if section_type == "table":
                builder.add_table(
                    name,
                    section.get("headers", []),
                    section.get("rows", []),
                    section.get("title", ""),
                    section.get("footer"),
                )
            elif section_type == "kpis":
                builder.add_kpis(
                    name,
                    section.get("data", section.get("kpis", [])),
                    section.get("title", ""),
                )
            elif section_type == "text":
                builder.add_text(
                    name,
                    section.get("content", section.get("data", "")),
                    section.get("title", ""),
                )
    
    if inline:
        return builder.render_inline()
    return builder.render()
