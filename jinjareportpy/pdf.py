"""PDF export functionality using WeasyPrint."""

import logging
from pathlib import Path

from .exceptions import PDFExportError

logger = logging.getLogger(__name__)


def check_weasyprint_available() -> bool:
    """Check if WeasyPrint is installed and available.

    Returns:
        True if WeasyPrint is available, False otherwise.
    """
    try:
        import weasyprint  # noqa: F401

        return True
    except ImportError:
        return False


def html_to_pdf(
    html_content: str,
    output_path: Path | str | None = None,
    stylesheets: list[str] | None = None,
    base_url: str | None = None,
    zoom: float = 1.0,
    optimize_images: bool = True,
) -> bytes:
    """Convert HTML content to PDF.

    Args:
        html_content: HTML string to convert.
        output_path: Optional path to save the PDF file.
        stylesheets: Optional list of additional CSS strings.
        base_url: Base URL for resolving relative URLs.
        zoom: Zoom factor for PDF rendering (default 1.0).
        optimize_images: Optimize embedded images in PDF output.

    Returns:
        PDF content as bytes.

    Raises:
        PDFExportError: If conversion fails or WeasyPrint not available.
    """
    try:
        from weasyprint import CSS, HTML
    except ImportError as e:
        raise PDFExportError(
            "WeasyPrint is not installed. Install it with: pip install weasyprint",
            original_error=e,
        )

    try:
        # Restrict base_url to safe schemes to prevent SSRF
        if base_url and base_url.startswith("//"):
            raise PDFExportError(
                f"Unsafe base_url (UNC paths not allowed): {base_url}"
            )
        if base_url and not base_url.startswith(("file://", "file:\\", "data:", ".", "/")):
            raise PDFExportError(
                f"Unsafe base_url scheme: {base_url}. "
                "Only file:// and data: schemes are allowed."
            )

        # Create HTML document
        html_doc = HTML(string=html_content, base_url=base_url)

        # Prepare stylesheets
        css_list = []
        if stylesheets:
            for css_content in stylesheets:
                css_list.append(CSS(string=css_content))

        # Generate PDF
        pdf_bytes = html_doc.write_pdf(
            stylesheets=css_list if css_list else None,
            zoom=zoom,
            optimize_images=optimize_images,
        )

        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(pdf_bytes)

        return pdf_bytes

    except Exception as e:
        logger.exception("PDF generation failed")
        raise PDFExportError(f"Failed to generate PDF: {e}", original_error=e)


def get_print_css(
    page_width: str = "210mm",
    page_height: str = "297mm",
    margin: str = "15mm",
) -> str:
    """Generate CSS for print/PDF output.

    Args:
        page_width: Page width (e.g., '210mm' for A4).
        page_height: Page height (e.g., '297mm' for A4).
        margin: Page margins.

    Returns:
        CSS string for print styling.
    """
    return f"""
@page {{
    size: {page_width} {page_height};
    margin: {margin};

    @top-center {{
        content: element(header);
    }}

    @bottom-center {{
        content: element(footer);
    }}

    @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }}
}}

@page :first {{
    @top-center {{
        content: none;
    }}
}}

.page-break {{
    page-break-after: always;
    break-after: page;
}}

.page-break-before {{
    page-break-before: always;
    break-before: page;
}}

.avoid-break {{
    page-break-inside: avoid;
    break-inside: avoid;
}}

.running-header {{
    position: running(header);
}}

.running-footer {{
    position: running(footer);
}}

@media print {{
    body {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}

    .no-print {{
        display: none !important;
    }}
}}
"""
