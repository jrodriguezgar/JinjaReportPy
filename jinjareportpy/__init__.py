"""
📄 JinjaReportPy - Generador Programático de Documentos e Informes.

Módulo Python para generar informes multipágina y documentos profesionales
con secciones dinámicas, CSS personalizado y exportación PDF.
"""

__version__ = "0.1.0"
__author__ = "JinjaReportPy Team"

# Base class
from .base import BaseDocument

# Core classes
from .report import Report
from .document import (
    Document,
    create_invoice,
    create_quote,
    create_receipt,
    create_delivery_note,
)
from .page import Page
from .sections import (
    Section,
    HeaderSection,
    FooterSection,
    TableSection,
    TextSection,
    KPISection,
)

# Builder API (simplified)
from .builder import (
    ReportBuilder,
    HeaderConfig,
    FooterConfig,
    TableConfig,
    KPIConfig,
    TextConfig,
    PageLayout,
    ReportLayout,
    quick_report,
)

# Formats
from .formats import (
    set_default_format,
    get_default_format,
    get_available_formats,
)

# Configuration
from .config import (
    ReportConfig,
    PageSize,
    Orientation,
    JinjaReportConfig,
    get_templates_dir,
    set_templates_dir,
    get_formats_dir,
    set_formats_dir,
    get_output_dir,
    set_output_dir,
    get_assets_dir,
    set_assets_dir,
    get_locale,
    set_locale,
    get_page_size,
    set_page_size,
    get_orientation,
    set_orientation,
)

# Utilities
from .assets import AssetManager
from .filters import register_default_filters

# Viewer utilities
from .viewer import (
    ReportViewer,
    get_viewer,
    reset_viewer,
    open_in_browser,
    open_in_new_window,
    open_in_new_tab,
    open_pdf_viewer,
    get_available_browsers,
)

# Exceptions
from .exceptions import (
    NinjaReportError,
    TemplateNotFoundError,
    AssetNotFoundError,
    ExportError,
)

# CLI
from .cli import main as cli_main

# Legacy - kept for compatibility
from .generator import ReportGenerator

__all__ = [
    # Base
    "BaseDocument",
    # Core
    "Report",
    "Document",
    "Page",
    "Section",
    # Document factories
    "create_invoice",
    "create_quote",
    "create_receipt",
    "create_delivery_note",
    # Predefined sections
    "HeaderSection",
    "FooterSection",
    "TableSection",
    "TextSection",
    "KPISection",
    # Builder API
    "ReportBuilder",
    "HeaderConfig",
    "FooterConfig",
    "TableConfig",
    "KPIConfig",
    "TextConfig",
    "PageLayout",
    "ReportLayout",
    "quick_report",
    # Formats
    "set_default_format",
    "get_default_format",
    "get_available_formats",
    # Configuration
    "ReportConfig",
    "PageSize",
    "Orientation",
    "JinjaReportConfig",
    "get_templates_dir",
    "set_templates_dir",
    "get_formats_dir",
    "set_formats_dir",
    "get_output_dir",
    "set_output_dir",
    # Utilities
    "AssetManager",
    "register_default_filters",
    # Viewer utilities
    "ReportViewer",
    "get_viewer",
    "reset_viewer",
    "open_in_browser",
    "open_in_new_window",
    "open_in_new_tab",
    "open_pdf_viewer",
    "get_available_browsers",
    # Legacy
    "ReportGenerator",
    # Exceptions
    "NinjaReportError",
    "TemplateNotFoundError",
    "AssetNotFoundError",
    "ExportError",
]
