"""
🥷 NinjaReportPy - Generador Programático de Documentos e Informes.

Módulo Python para generar informes multipágina y documentos profesionales
con secciones dinámicas, CSS personalizado y exportación PDF.
"""

__version__ = "0.1.0"
__author__ = "NinjaReportPy Team"

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
from .config import ReportConfig, PageSize, Orientation

# Utilities
from .assets import AssetManager
from .filters import register_default_filters

# Viewer utilities (WinFormPy integration)
from .viewer import (
    open_in_browser,
    open_pdf_viewer,
    get_available_browsers,
    check_winformpy_available,
    create_embedded_browser,
    create_browser_panel,
    display_html_in_browser,
    display_html_in_panel,
    open_in_embedded_browser,
)

# Exceptions
from .exceptions import (
    NinjaReportError,
    TemplateNotFoundError,
    AssetNotFoundError,
    ExportError,
)

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
    # Utilities
    "AssetManager",
    "register_default_filters",
    # Viewer utilities (WinFormPy integration)
    "open_in_browser",
    "open_pdf_viewer",
    "get_available_browsers",
    "check_winformpy_available",
    "create_embedded_browser",
    "create_browser_panel",
    "display_html_in_browser",
    "display_html_in_panel",
    "open_in_embedded_browser",
    # Legacy
    "ReportGenerator",
    # Exceptions
    "NinjaReportError",
    "TemplateNotFoundError",
    "AssetNotFoundError",
    "ExportError",
]
