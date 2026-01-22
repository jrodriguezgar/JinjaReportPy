"""
Section - Basic content component for reports.

A section represents a content block with its own CSS, HTML template,
and data. If not provided, uses the active format's defaults.
"""

from dataclasses import dataclass, field
from typing import Any

from jinja2 import Template

from .formats import (
    get_header_template,
    get_footer_template,
    get_section_template,
    get_table_template,
    get_kpi_template,
    get_text_template,
)


@dataclass
class Section:
    """A content section with CSS, template, and data.

    Sections are the building blocks of reports. Each section has:
    - A unique name for identification
    - An HTML template (Jinja2 syntax)
    - Data to inject into the template
    - CSS styles specific to the section

    Attributes:
        name: Unique identifier for the section.
        template: HTML template string (Jinja2 syntax).
                  If None/empty, uses the active format's template.
        data: Data dictionary to inject into the template.
        css: CSS styles specific to this section.
             If None, uses the active format's CSS.
        css_class: Additional CSS class for the container.
        format_name: Name of the format to use (None = active format).

    Example:
        >>> # Using default format
        >>> section = Section(name="intro", data={"title": "Intro", "content": "..."})
        
        >>> # With custom template and CSS
        >>> section = Section(
        ...     name="custom",
        ...     template="<h2>{{ title }}</h2>",
        ...     data={"title": "My Section"},
        ...     css=".section-custom h2 { color: blue; }"
        ... )
    """

    name: str
    template: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    css: str | None = None
    css_class: str = ""
    format_name: str | None = None

    def _get_default_template_css(self) -> tuple[str, str]:
        """Get default template and CSS from the active format."""
        return get_section_template(self.format_name)

    def render(self) -> str:
        """Render the section with its data.

        Returns:
            Rendered HTML string for the section.
        """
        # Get template (custom or from format)
        template_str = self.template
        if not template_str:
            template_str, _ = self._get_default_template_css()
        
        if not template_str:
            return ""

        jinja_template = Template(template_str)
        content = jinja_template.render(**self.data)

        # Build CSS class string
        classes = f"section section-{self.name}"
        if self.css_class:
            classes += f" {self.css_class}"

        return f'<div class="{classes}">\n{content}\n</div>'

    def render_css(self) -> str:
        """Return the CSS for this section.

        If no CSS was provided, uses the active format's CSS.

        Returns:
            CSS string scoped to this section.
        """
        css_content = self.css
        if css_content is None:
            _, css_content = self._get_default_template_css()
        
        if not css_content:
            return ""
        return f"/* Section: {self.name} */\n{css_content}"

    def __repr__(self) -> str:
        return f"Section(name='{self.name}')"


# ============================================
# Predefined common sections
# ============================================

class HeaderSection(Section):
    """Predefined header section.
    
    Uses the active format's template/CSS if not provided.
    """

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        logo: str = "",
        date: str = "",
        data: dict[str, Any] | None = None,
        template: str | None = None,
        css: str | None = None,
        format_name: str | None = None,
    ):
        """Initialize a header section.
        
        Args:
            title: Main header title.
            subtitle: Subtitle text.
            logo: URL or Base64 string for the logo image.
            date: Date to display.
            data: Additional data for the template.
            template: Custom HTML template (None = use format).
            css: Custom CSS (None = use format).
            format_name: Specific format name (None = active format).
        """
        default_data = {
            "title": title,
            "subtitle": subtitle,
            "logo": logo,
            "date": date,
        }
        if data:
            default_data.update(data)

        super().__init__(
            name="header",
            template=template,
            data=default_data,
            css=css,
            format_name=format_name,
        )

    def _get_default_template_css(self) -> tuple[str, str]:
        """Get header template and CSS from the format."""
        return get_header_template(self.format_name)


class FooterSection(Section):
    """Predefined footer section.
    
    Uses the active format's template/CSS if not provided.
    Supports left, center, and right text areas.
    """

    def __init__(
        self,
        left_text: str = "",
        right_text: str = "",
        center_text: str = "",
        data: dict[str, Any] | None = None,
        template: str | None = None,
        css: str | None = None,
        format_name: str | None = None,
    ):
        """Initialize a footer section.
        
        Args:
            left_text: Left-aligned footer text.
            right_text: Right-aligned footer text.
            center_text: Center-aligned footer text.
            data: Additional data for the template.
            template: Custom HTML template (None = use format).
            css: Custom CSS (None = use format).
            format_name: Specific format name (None = active format).
        """
        default_data = {
            "left_text": left_text,
            "right_text": right_text,
            "center_text": center_text,
        }
        if data:
            default_data.update(data)

        super().__init__(
            name="footer",
            template=template,
            data=default_data,
            css=css,
            format_name=format_name,
        )

    def _get_default_template_css(self) -> tuple[str, str]:
        """Get footer template and CSS from the format."""
        return get_footer_template(self.format_name)


class TableSection(Section):
    """Predefined table section.
    
    Uses the active format's template/CSS if not provided.
    Supports headers, data rows, and an optional footer row.
    """

    def __init__(
        self,
        name: str,
        headers: list[str],
        rows: list[list[Any]],
        title: str = "",
        footer_row: list[Any] | None = None,
        template: str | None = None,
        css: str | None = None,
        format_name: str | None = None,
    ):
        """Initialize a table section.
        
        Args:
            name: Unique identifier for the table.
            headers: List of column header strings.
            rows: List of rows (each row is a list of cell values).
            title: Optional table title.
            footer_row: Optional footer row (e.g., totals).
            template: Custom HTML template (None = use format).
            css: Custom CSS (None = use format).
            format_name: Specific format name (None = active format).
        
        Example:
            >>> table = TableSection(
            ...     name="sales",
            ...     headers=["Product", "Units", "Revenue"],
            ...     rows=[
            ...         ["Widget A", 100, "£1,000"],
            ...         ["Widget B", 200, "£2,000"],
            ...     ],
            ...     title="Sales Data",
            ...     footer_row=["Total", 300, "£3,000"],
            ... )
        """
        super().__init__(
            name=name,
            template=template,
            data={
                "title": title,
                "headers": headers,
                "rows": rows,
                "footer_row": footer_row,
            },
            css=css,
            css_class="table",
            format_name=format_name,
        )

    def _get_default_template_css(self) -> tuple[str, str]:
        """Get table template and CSS from the format."""
        return get_table_template(self.format_name)


class TextSection(Section):
    """Predefined text section.
    
    Uses the active format's template/CSS if not provided.
    Supports HTML content.
    """

    def __init__(
        self,
        name: str,
        content: str,
        title: str = "",
        template: str | None = None,
        css: str | None = None,
        format_name: str | None = None,
    ):
        """Initialize a text section.
        
        Args:
            name: Unique identifier for the section.
            content: Text content (can include HTML).
            title: Optional section title.
            template: Custom HTML template (None = use format).
            css: Custom CSS (None = use format).
            format_name: Specific format name (None = active format).
        
        Example:
            >>> text = TextSection(
            ...     name="notes",
            ...     content="<p>Important notes go here.</p>",
            ...     title="Notes",
            ... )
        """
        super().__init__(
            name=name,
            template=template,
            data={"title": title, "content": content},
            css=css,
            css_class="text",
            format_name=format_name,
        )

    def _get_default_template_css(self) -> tuple[str, str]:
        """Get text template and CSS from the format."""
        return get_text_template(self.format_name)


class KPISection(Section):
    """Predefined KPI (Key Performance Indicator) section.
    
    Uses the active format's template/CSS if not provided.
    Displays metrics with optional change indicators.
    """

    def __init__(
        self,
        name: str,
        kpis: list[dict[str, Any]],
        title: str = "",
        template: str | None = None,
        css: str | None = None,
        format_name: str | None = None,
    ):
        """Initialize a KPI section.
        
        Args:
            name: Unique identifier for the section.
            kpis: List of KPI dictionaries, each containing:
                - label (str): KPI label/name
                - value (str): Value to display
                - change (int|float|str, optional): Percentage change
                - description (str, optional): Additional description
                - color_class (str, optional): CSS color class
            title: Optional section title.
            template: Custom HTML template (None = use format).
            css: Custom CSS (None = use format).
            format_name: Specific format name (None = active format).
        
        Example:
            >>> kpis = KPISection(
            ...     name="metrics",
            ...     kpis=[
            ...         {"label": "Revenue", "value": "£125K", "change": 15},
            ...         {"label": "Orders", "value": "1,234", "change": -5},
            ...     ],
            ...     title="Key Metrics",
            ... )
        """
        super().__init__(
            name=name,
            template=template,
            data={"title": title, "kpis": kpis},
            css=css,
            css_class="kpi",
            format_name=format_name,
        )

    def _get_default_template_css(self) -> tuple[str, str]:
        """Get KPI template and CSS from the format."""
        return get_kpi_template(self.format_name)
