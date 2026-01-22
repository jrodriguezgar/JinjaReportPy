"""
Report - Multi-page report generator.

Groups pages with dynamic sections and generates HTML/PDF output.
Inherits from BaseDocument for common export functionality.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import BaseDocument
from .page import Page
from .sections import Section, HeaderSection, FooterSection
from .config import ReportConfig, PageSize, Orientation
from .exceptions import ExportError


@dataclass
class Report(BaseDocument):
    """Multi-page report generator with dynamic sections.

    Supports multiple pages, each with its own header, footer, and
    content sections. Sections can be KPIs, tables, text, or custom.

    Attributes:
        title: Report title.
        pages: List of Page objects.
        config: Report configuration settings.
        global_css: Additional global CSS styles.
        format_name: Default format for the report (None = active format).

    Example:
        >>> report = Report(title="Sales Report")
        >>> page = report.add_page()
        >>> page.set_header(title="Q4 Sales", subtitle="2025")
        >>> page.add_section(Section(
        ...     name="summary",
        ...     template="<p>{{ text }}</p>",
        ...     data={"text": "Executive summary..."},
        ...     css=".section-summary { background: #f0f0f0; }"
        ... ))
        >>> html = report.render()
        >>> report.export_pdf("sales_report.pdf")
    """

    title: str = "Report"
    pages: list[Page] = field(default_factory=list)
    config: ReportConfig = field(default_factory=ReportConfig)
    global_css: str = ""
    format_name: str | None = None
    # Note: _last_rendered is inherited from BaseDocument

    def add_page(
        self,
        header: Section | None = None,
        footer: Section | None = None,
        format_name: str | None = None,
    ) -> Page:
        """Create and add a new page to the report.

        Args:
            header: Predefined header section (optional).
            footer: Predefined footer section (optional).
            format_name: Format for the page (None = report format or active).

        Returns:
            The created Page object for method chaining.

        Example:
            >>> page = report.add_page()
            >>> page.set_header(title="Page 1")
            >>> page.add_section(TableSection(...))
        """
        page = Page(
            header=header,
            footer=footer,
            page_number=len(self.pages) + 1,
            format_name=format_name or self.format_name,
        )
        self.pages.append(page)
        return page

    def get_page(self, index: int) -> Page:
        """Get a page by index.

        Args:
            index: Page index (0-based).

        Returns:
            The requested Page object.

        Raises:
            IndexError: If index is out of range.
        """
        return self.pages[index]

    def render_css(self) -> str:
        """Generate all CSS for the report (excluding base CSS).

        Returns:
            Combined CSS from all pages.
        """
        css_parts = []

        for i, page in enumerate(self.pages):
            page_css = page.render_css()
            if page_css:
                css_parts.append(f"/* Page {i + 1} CSS */\n{page_css}")

        return "\n\n".join(css_parts)

    def render_content(self) -> str:
        """Generate the HTML content for all pages.

        Returns:
            HTML string containing all rendered pages.
        """
        return "\n".join(page.render() for page in self.pages)

    def __repr__(self) -> str:
        return f"Report(title='{self.title}', pages={len(self.pages)})"
