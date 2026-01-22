"""
Page - Representa una página del informe con cabecera, pie y secciones.
"""

from dataclasses import dataclass, field
from typing import Any

from .sections import Section, HeaderSection, FooterSection


@dataclass
class Page:
    """Una página del informe con cabecera, pie y secciones dinámicas.

    Attributes:
        header: Sección de cabecera (opcional).
        footer: Sección de pie de página (opcional).
        sections: Lista de secciones de contenido.
        css: CSS adicional específico de la página.
        page_number: Número de página (se asigna automáticamente).
        format_name: Formato por defecto para las secciones (None = formato activo).

    Example:
        >>> page = Page()
        >>> page.set_header(title="Mi Informe", subtitle="2025")
        >>> page.add_section(Section(
        ...     name="intro",
        ...     template="<p>{{ text }}</p>",
        ...     data={"text": "Introducción..."}
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
        title: str = "",
        subtitle: str = "",
        logo: str = "",
        date: str = "",
        template: str | None = None,
        css: str | None = None,
        data: dict[str, Any] | None = None,
        format_name: str | None = None,
    ) -> "Page":
        """Configura la cabecera de la página.

        Args:
            title: Título principal.
            subtitle: Subtítulo.
            logo: Ruta o Base64 del logo.
            date: Fecha a mostrar.
            template: Template HTML personalizado (None = usar formato).
            css: CSS personalizado (None = usar formato).
            data: Datos adicionales.
            format_name: Formato a usar (None = formato de la página o activo).

        Returns:
            Self para encadenamiento.
        """
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
        left_text: str = "",
        right_text: str = "",
        center_text: str = "",
        template: str | None = None,
        css: str | None = None,
        data: dict[str, Any] | None = None,
        format_name: str | None = None,
    ) -> "Page":
        """Configura el pie de página.

        Args:
            left_text: Texto izquierdo.
            right_text: Texto derecho.
            center_text: Texto central.
            template: Template HTML personalizado (None = usar formato).
            css: CSS personalizado (None = usar formato).
            data: Datos adicionales.
            format_name: Formato a usar (None = formato de la página o activo).

        Returns:
            Self para encadenamiento.
        """
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
        """Añade una sección a la página.

        Puede recibir un objeto Section o los parámetros para crear uno.

        Args:
            section: Objeto Section existente.
            name: Nombre de la sección (si no se pasa section).
            template: Template HTML (None = usar formato).
            data: Datos para el template.
            css: CSS de la sección (None = usar formato).
            format_name: Formato a usar (None = formato de la página o activo).

        Returns:
            Self para encadenamiento.
        """
        if section is not None:
            # Si la sección no tiene formato, usar el de la página
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
        """Recopila todo el CSS de la página y sus secciones.

        Returns:
            CSS combinado.
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
        """Renderiza la página completa.

        Returns:
            HTML de la página.
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
