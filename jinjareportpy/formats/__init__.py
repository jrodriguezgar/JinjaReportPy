"""
Formatos predefinidos para JinjaReportPy.

Cada formato contiene templates HTML y CSS para:
- Header: Cabecera de página
- Footer: Pie de página
- Section: Sección genérica
- Table: Sección de tabla
- KPI: Sección de indicadores clave

Los formatos disponibles son:
- default: Formato profesional moderno (azul/gris)
- corporate: Formato corporativo serio
- minimal: Formato minimalista limpio

The formats directory is configurable via:
- Environment variable: JINJAREPORT_FORMATS_DIR
- Programmatic: JinjaReportConfig.set_formats_dir()
- Config file: jinjareportpy.toml [paths.formats_dir]
"""

from pathlib import Path
from functools import lru_cache
from typing import TypedDict

from jinjareportpy.config import get_formats_dir


class FormatTemplates(TypedDict):
    """Estructura de un formato."""
    header_html: str
    header_css: str
    footer_html: str
    footer_css: str
    section_html: str
    section_css: str
    table_html: str
    table_css: str
    kpi_html: str
    kpi_css: str
    text_html: str
    text_css: str


# Formato activo por defecto
_active_format: str = "default"


def set_default_format(format_name: str) -> None:
    """Establece el formato por defecto para nuevas secciones.
    
    Args:
        format_name: Nombre del formato (default, corporate, minimal).
    
    Raises:
        ValueError: Si el formato no existe.
    """
    global _active_format
    formats_dir = get_formats_dir()
    format_path = formats_dir / format_name
    if not format_path.is_dir():
        available = get_available_formats()
        raise ValueError(
            f"Formato '{format_name}' no encontrado. "
            f"Disponibles: {', '.join(available)}"
        )
    _active_format = format_name
    # Limpiar cache
    get_format_templates.cache_clear()


def get_default_format() -> str:
    """Devuelve el nombre del formato activo."""
    return _active_format


def get_available_formats() -> list[str]:
    """Lista los formatos disponibles.
    
    Returns:
        Lista de nombres de formatos.
    """
    formats = []
    formats_dir = get_formats_dir()
    for path in formats_dir.iterdir():
        if path.is_dir() and not path.name.startswith("_"):
            formats.append(path.name)
    return sorted(formats)


@lru_cache(maxsize=8)
def get_format_templates(format_name: str | None = None) -> FormatTemplates:
    """Carga los templates de un formato.
    
    Args:
        format_name: Nombre del formato. Si es None, usa el formato activo.
    
    Returns:
        Diccionario con todos los templates del formato.
    
    Raises:
        ValueError: Si el formato no existe.
    """
    name = format_name or _active_format
    formats_dir = get_formats_dir()
    format_path = formats_dir / name
    
    if not format_path.is_dir():
        raise ValueError(f"Formato '{name}' no encontrado en {formats_dir}")
    
    def read_file(filename: str) -> str:
        """Lee un archivo del formato, devuelve string vacío si no existe."""
        file_path = format_path / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    return FormatTemplates(
        header_html=read_file("header.html"),
        header_css=read_file("header.css"),
        footer_html=read_file("footer.html"),
        footer_css=read_file("footer.css"),
        section_html=read_file("section.html"),
        section_css=read_file("section.css"),
        table_html=read_file("table.html"),
        table_css=read_file("table.css"),
        kpi_html=read_file("kpi.html"),
        kpi_css=read_file("kpi.css"),
        text_html=read_file("text.html"),
        text_css=read_file("text.css"),
    )


def get_header_template(format_name: str | None = None) -> tuple[str, str]:
    """Obtiene template HTML y CSS para Header."""
    templates = get_format_templates(format_name)
    return templates["header_html"], templates["header_css"]


def get_footer_template(format_name: str | None = None) -> tuple[str, str]:
    """Obtiene template HTML y CSS para Footer."""
    templates = get_format_templates(format_name)
    return templates["footer_html"], templates["footer_css"]


def get_section_template(format_name: str | None = None) -> tuple[str, str]:
    """Obtiene template HTML y CSS para Section genérica."""
    templates = get_format_templates(format_name)
    return templates["section_html"], templates["section_css"]


def get_table_template(format_name: str | None = None) -> tuple[str, str]:
    """Obtiene template HTML y CSS para Table."""
    templates = get_format_templates(format_name)
    return templates["table_html"], templates["table_css"]


def get_kpi_template(format_name: str | None = None) -> tuple[str, str]:
    """Obtiene template HTML y CSS para KPI."""
    templates = get_format_templates(format_name)
    return templates["kpi_html"], templates["kpi_css"]


def get_text_template(format_name: str | None = None) -> tuple[str, str]:
    """Obtiene template HTML y CSS para Text."""
    templates = get_format_templates(format_name)
    return templates["text_html"], templates["text_css"]
