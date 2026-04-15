"""
Page - Represents a report page with header, footer, and sections.
"""

from dataclasses import dataclass, field
from typing import Any

from .sections import FooterSection, HeaderSection, Section


@dataclass
class Page:
    """A report page with header, footer, and dynamic sections.

    Attributes:
        header: Header section (optional).
        footer: Footer section (optional).
        sections: List of content sections.
        css: Additional page-specific CSS.
        page_number: Page number (assigned automatically).
        format_name: Default format for sections (None = active format).

    Example:
        >>> page = Page()
        >>> page.set_header(title="My Report", subtitle="2025")
        >>> page.add_section(Section(
        ...     name="intro",
        ...     template="<p>{{ text }}</p>",
        ...     data={"text": "Introduction..."}
        ... ))
    """

    header: Section | None = None
    footer: Section | None = None
    sections: list[Section] = field(default_factory=list)
    css: str = ""
    page_number: int = 1
    format_name: str | None = None

    def set_header(
        self,
        title: str | HeaderSection = "",
        subtitle: str = "",
        logo: str = "",
        date: str = "",
        *,
        template: str | None = None,
        css: str | None = None,
        data: dict[str, Any] | None = None,
        format_name: str | None = None,
    ) -> "Page":
        """Configure the page header.

        Accepts either a ``HeaderSection`` object directly or individual
        keyword arguments to create one.

        Args:
            title: Main title, or a ``HeaderSection`` instance.
            subtitle: Subtitle.
            logo: Path or Base64 logo string.
            date: Date to display.
            template: Custom HTML template (None = use format).
            css: Custom CSS (None = use format).
            data: Additional data.
            format_name: Format to use (None = page or active format).

        Returns:
            Self for method chaining.
        """
        if isinstance(title, HeaderSection):
            self.header = title
            if self.header.format_name is None and self.format_name:
                self.header.format_name = self.format_name
            return self

        self.header = HeaderSection(
            title=title,
            subtitle=subtitle,
            logo=logo,
            date=date,
            template=template,
            css=css,
            data=data,
            format_name=format_name or self.format_name,
        )
        return self

    def set_footer(
        self,
        left_text: str | FooterSection = "",
        right_text: str = "",
        center_text: str = "",
        *,
        template: str | None = None,
        css: str | None = None,
        data: dict[str, Any] | None = None,
        format_name: str | None = None,
    ) -> "Page":
        """Configure the page footer.

        Accepts either a ``FooterSection`` object directly or individual
        keyword arguments to create one.

        Args:
            left_text: Left-aligned text, or a ``FooterSection`` instance.
            right_text: Right-aligned text.
            center_text: Center-aligned text.
            template: Custom HTML template (None = use format).
            css: Custom CSS (None = use format).
            data: Additional data.
            format_name: Format to use (None = page or active format).

        Returns:
            Self for method chaining.
        """
        if isinstance(left_text, FooterSection):
            self.footer = left_text
            if self.footer.format_name is None and self.format_name:
                self.footer.format_name = self.format_name
            return self

        self.footer = FooterSection(
            left_text=left_text,
            right_text=right_text,
            center_text=center_text,
            template=template,
            css=css,
            data=data,
            format_name=format_name or self.format_name,
        )
        return self

    def add_section(
        self,
        section: Section | None = None,
        *,
        name: str = "",
        template: str | None = None,
        data: dict[str, Any] | None = None,
        css: str | None = None,
        format_name: str | None = None,
    ) -> "Page":
        """Add a section to the page.

        Accepts either a Section object or parameters to create one.

        Args:
            section: Existing Section object.
            name: Section name (if section is not provided).
            template: HTML template (None = use format).
            data: Data for the template.
            css: Section CSS (None = use format).
            format_name: Format to use (None = page or active format).

        Returns:
            Self for method chaining.
        """
        if section is not None:
            # If the section has no format, use the page's format
            if section.format_name is None and self.format_name:
                section.format_name = self.format_name
            self.sections.append(section)
        else:
            self.sections.append(Section(
                name=name or f"section_{len(self.sections)}",
                template=template,
                data=data or {},
                css=css,
                format_name=format_name or self.format_name,
            ))
        return self

    def render_css(self) -> str:
        """Collect all CSS from the page and its sections.

        Returns:
            Combined CSS string.
        """
        css_parts = []

        if self.css:
            css_parts.append(f"/* Page CSS */\n{self.css}")

        if self.header:
            header_css = self.header.render_css()
            if header_css:
                css_parts.append(header_css)

        if self.footer:
            footer_css = self.footer.render_css()
            if footer_css:
                css_parts.append(footer_css)

        for section in self.sections:
            section_css = section.render_css()
            if section_css:
                css_parts.append(section_css)

        return "\n\n".join(css_parts)

    def render(self) -> str:
        """Render the complete page.

        Returns:
            Page HTML string.
        """
        parts = ['<div class="page">']

        # Header
        if self.header:
            parts.append(self.header.render())

        # Content sections
        parts.append('<div class="page-content">')
        for section in self.sections:
            parts.append(section.render())
        parts.append('</div>')

        # Footer
        if self.footer:
            parts.append(self.footer.render())

        parts.append('</div>')

        return "\n".join(parts)

    def __repr__(self) -> str:
        return f"Page(sections={len(self.sections)}, page_number={self.page_number})"
