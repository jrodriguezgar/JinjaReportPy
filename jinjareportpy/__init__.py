"""
JinjaReportPy - Programmatic Document & Report Generator.

Python module for generating multi-page reports and professional documents
with dynamic sections, custom CSS, and PDF export.
"""

__version__ = "0.2.0"
__author__ = "JinjaReportPy Team"

# Base class
# Utilities
from .assets import AssetManager
from .base import BaseDocument

# Builder API (simplified)
from .builder import (
    FooterConfig,
    HeaderConfig,
    KPIConfig,
    PageLayout,
    ReportBuilder,
    ReportLayout,
    TableConfig,
    TextConfig,
    quick_report,
)

# Configuration
from .config import (
    JinjaReportConfig,
    Orientation,
    PageSize,
    ReportConfig,
    get_assets_dir,
    get_formats_dir,
    get_locale,
    get_orientation,
    get_output_dir,
    get_page_size,
    get_templates_dir,
    set_assets_dir,
    set_formats_dir,
    set_locale,
    set_orientation,
    set_output_dir,
    set_page_size,
    set_templates_dir,
)
from .document import (
    DeliveryNoteData,
    Document,
    InvoiceData,
    PartyInfo,
    QuoteData,
    ReceiptData,
    create_delivery_note,
    create_invoice,
    create_quote,
    create_receipt,
)

# Exceptions
from .exceptions import (
    AssetNotFoundError,
    ExportError,
    JinjaReportError,
    TemplateNotFoundError,
)
from .filters import register_default_filters

# Formats
from .formats import (
    get_available_formats,
    get_default_format,
    set_default_format,
)
from .page import Page
from .pdf import check_weasyprint_available

# Core classes
from .report import Report
from .sections import (
    ChartSection,
    FooterSection,
    HeaderSection,
    KPISection,
    Section,
    TableSection,
    TextSection,
)

# Viewer utilities
from .viewer import open_in_browser, open_pdf_viewer

# CLI entry point
try:
    from .cli import main as cli_main
except ImportError:
    cli_main = None

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
    # Document data classes
    "PartyInfo",
    "InvoiceData",
    "QuoteData",
    "ReceiptData",
    "DeliveryNoteData",
    # Predefined sections
    "HeaderSection",
    "FooterSection",
    "TableSection",
    "TextSection",
    "KPISection",
    "ChartSection",
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
    "get_assets_dir",
    "set_assets_dir",
    "get_locale",
    "set_locale",
    "get_page_size",
    "set_page_size",
    "get_orientation",
    "set_orientation",
    # Utilities
    "AssetManager",
    "register_default_filters",
    "check_weasyprint_available",
    # Viewer (shortcuts)
    "open_in_browser",
    "open_pdf_viewer",
    # Exceptions
    "JinjaReportError",
    "TemplateNotFoundError",
    "AssetNotFoundError",
    "ExportError",
]
