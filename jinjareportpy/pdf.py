"""PDF export functionality using WeasyPrint."""

from pathlib import Path
from typing import TYPE_CHECKING

from .exceptions import PDFExportError

if TYPE_CHECKING:
    from weasyprint import HTML, CSS


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
) -> bytes:
    """Convert HTML content to PDF.

    Args:
        html_content: HTML string to convert.
        output_path: Optional path to save the PDF file.
        stylesheets: Optional list of additional CSS strings.
        base_url: Base URL for resolving relative URLs.

    Returns:
        PDF content as bytes.

    Raises:
        PDFExportError: If conversion fails or WeasyPrint not available.
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError as e:
        raise PDFExportError(
            "WeasyPrint is not installed. Install it with: pip install weasyprint",
            original_error=e,
        )

    try:
        # Create HTML document
        html_doc = HTML(string=html_content, base_url=base_url)

        # Prepare stylesheets
        css_list = []
        if stylesheets:
            for css_content in stylesheets:
                css_list.append(CSS(string=css_content))

        # Generate PDF
        pdf_bytes = html_doc.write_pdf(stylesheets=css_list if css_list else None)

        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(pdf_bytes)

        return pdf_bytes

    except Exception as e:
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
        content: "Página " counter(page) " de " counter(pages);
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
