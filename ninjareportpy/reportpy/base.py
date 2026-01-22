"""
BaseDocument - Abstract base class for documents and reports.

Provides common functionality for generating HTML/PDF output.
This is the parent class for both Document and Report classes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, BaseLoader, TemplateNotFound

from .config import ReportConfig
from .exceptions import ExportError, TemplateNotFoundError


# Base CSS for A4 print layout
BASE_CSS = """
/* Reset & Base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --primary-color: #2563eb;
    --text-color: #1e293b;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    --bg-light: #f8fafc;
    --page-width: 210mm;
    --page-height: 297mm;
    --page-margin: 15mm;
}

html { font-size: 10pt; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: var(--text-color);
    background: #fff;
}

/* Page Structure */
.page {
    width: var(--page-width);
    min-height: var(--page-height);
    padding: var(--page-margin);
    margin: 0 auto 20px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    position: relative;
    page-break-after: always;
}
.page:last-child { page-break-after: auto; }
.page-content { min-height: calc(var(--page-height) - 2 * var(--page-margin) - 40mm); }

/* Section */
.section { margin-bottom: 20px; }

/* Typography */
h1, h2, h3, h4 { font-weight: 600; line-height: 1.25; margin-bottom: 0.5em; }
h1 { font-size: 20pt; }
h2 { font-size: 16pt; border-bottom: 2px solid var(--primary-color); padding-bottom: 0.25em; }
h3 { font-size: 13pt; }
p { margin-bottom: 1em; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin: 1em 0; }
th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--border-color); }
th { background: var(--bg-light); font-weight: 600; }
tbody tr:hover { background: #f8fafc; }
.table-bordered th, .table-bordered td { border: 1px solid var(--border-color); }

/* Cards */
.card { border: 1px solid var(--border-color); border-radius: 4px; padding: 15px; margin-bottom: 15px; }
.card-header { font-weight: 600; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid var(--border-color); }

/* Grid Layout */
.row { display: flex; flex-wrap: wrap; margin: 0 -10px; }
.col-6 { flex: 0 0 50%; max-width: 50%; padding: 0 10px; }
.col-12 { flex: 0 0 100%; max-width: 100%; padding: 0 10px; }

/* Utilities */
.text-right { text-align: right; }
.text-center { text-align: center; }
.text-muted { color: var(--text-muted); }
.font-bold { font-weight: 700; }
.font-mono { font-family: 'Consolas', 'Monaco', monospace; }
.mb-1 { margin-bottom: 5px; }
.mb-2 { margin-bottom: 10px; }
.mb-3 { margin-bottom: 15px; }
.mb-4 { margin-bottom: 20px; }
.mt-4 { margin-top: 20px; }
.border-top { border-top: 2px solid var(--border-color); }

/* Info boxes */
.info-box { background: var(--bg-light); padding: 10px; border-radius: 4px; font-size: 9pt; }

/* Print */
@media print {
    body { background: none; }
    .page { width: 100%; min-height: auto; padding: 0; margin: 0; box-shadow: none; }
    .no-print { display: none !important; }
}
@page { size: A4 portrait; margin: 15mm; }

/* Page break utilities */
.page-break { page-break-after: always; }
.avoid-break { page-break-inside: avoid; }
"""


@dataclass
class BaseDocument(ABC):
    """Abstract base class for documents and reports.
    
    Provides common functionality:
    - HTML rendering
    - HTML and PDF export
    - Browser preview
    
    Subclasses must implement:
    - render_content(): Returns the document body HTML
    - render_css(): Returns document-specific CSS
    
    Attributes:
        title: Document title.
        config: Document configuration settings.
        global_css: Additional global CSS styles.
    
    Example:
        >>> class MyDocument(BaseDocument):
        ...     def render_content(self):
        ...         return "<div>My content</div>"
        ...     def render_css(self):
        ...         return ".my-class { color: blue; }"
        >>> doc = MyDocument(title="My Doc")
        >>> doc.export_html("output.html")
    """
    
    title: str = "Document"
    config: ReportConfig = field(default_factory=ReportConfig)
    global_css: str = ""
    
    _last_rendered: str = field(default="", repr=False)
    
    @abstractmethod
    def render_content(self) -> str:
        """Render the main content of the document.
        
        Returns:
            HTML content string.
        """
        pass
    
    @abstractmethod
    def render_css(self) -> str:
        """Generate document-specific CSS.
        
        Returns:
            CSS string.
        """
        pass
    
    def get_base_css(self) -> str:
        """Return the base CSS.
        
        Returns:
            Base CSS for documents (A4 layout, typography, etc.).
        """
        return BASE_CSS
    
    def render(self) -> str:
        """Generate the complete HTML document.
        
        Combines base CSS, document CSS, and global CSS with the
        rendered content to produce a complete HTML document.
        
        Returns:
            Complete HTML string ready for viewing or export.
        """
        # Collect CSS
        css_parts = [self.get_base_css()]
        
        doc_css = self.render_css()
        if doc_css:
            css_parts.append(f"/* Document CSS */\n{doc_css}")
        
        if self.global_css:
            css_parts.append(f"/* Global CSS */\n{self.global_css}")
        
        all_css = "\n\n".join(css_parts)
        
        # Render content
        content_html = self.render_content()
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
{all_css}
    </style>
</head>
<body>
{content_html}
</body>
</html>"""
        
        self._last_rendered = html
        return html
    
    def export_html(
        self,
        path: Path | str | None = None,
        filename: str = "document.html",
    ) -> Path:
        """Export the document to an HTML file.
        
        Args:
            path: Full path or output directory. If None, uses config.output_dir.
            filename: Filename to use if path is a directory.
        
        Returns:
            Path to the generated file.
        
        Example:
            >>> doc.export_html("output/report.html")
            >>> doc.export_html("output/", filename="my_report.html")
        """
        html = self._last_rendered or self.render()
        
        if path is None:
            path = self.config.output_dir / filename
        else:
            path = Path(path)
            if path.is_dir():
                path = path / filename
        
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        
        return path
    
    def export_pdf(
        self,
        path: Path | str | None = None,
        filename: str = "document.pdf",
    ) -> Path:
        """Export the document to a PDF file.
        
        Requires WeasyPrint to be installed (pip install weasyprint).
        
        Args:
            path: Full path or output directory. If None, uses config.output_dir.
            filename: Filename to use if path is a directory.
        
        Returns:
            Path to the generated PDF file.
        
        Raises:
            ExportError: If WeasyPrint is not installed.
        
        Example:
            >>> doc.export_pdf("output/report.pdf")
        """
        from .pdf import html_to_pdf, check_weasyprint_available
        
        if not check_weasyprint_available():
            raise ExportError(
                "WeasyPrint is not installed. Install with: pip install weasyprint"
            )
        
        html = self._last_rendered or self.render()
        
        if path is None:
            path = self.config.output_dir / filename
        else:
            path = Path(path)
            if path.is_dir():
                path = path / filename
        
        html_to_pdf(html, path)
        return path
    
    def preview(self, browser: str | None = None) -> Path:
        """Open the document in a web browser.
        
        Args:
            browser: Browser command (None = system default).
        
        Returns:
            Path to the temporary HTML file.
        
        Example:
            >>> doc.preview()  # Opens in default browser
            >>> doc.preview("chrome")  # Opens in Chrome
        """
        from .viewer import open_in_browser
        
        html = self._last_rendered or self.render()
        return open_in_browser(html_content=html, browser_command=browser)
    
    def preview_pdf(self, viewer: str | None = None) -> Path:
        """Generate PDF and open it in a PDF viewer.
        
        Args:
            viewer: PDF viewer command (None = system default).
        
        Returns:
            Path to the generated PDF file.
        
        Example:
            >>> doc.preview_pdf()  # Opens in default PDF viewer
        """
        import tempfile
        from .viewer import open_pdf_viewer
        
        temp_dir = Path(tempfile.gettempdir()) / "reportpy"
        temp_dir.mkdir(exist_ok=True)
        pdf_path = temp_dir / f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        self.export_pdf(pdf_path)
        open_pdf_viewer(pdf_path, viewer)
        
        return pdf_path

    def preview_embedded(
        self,
        parent: Any,
        props: dict | None = None,
        with_navigation: bool = False,
    ) -> Any:
        """Display the document in a WinFormPy embedded browser.
        
        Requires WinFormPy and tkinterweb to be installed.
        
        Args:
            parent: Parent WinFormPy control (Form, Panel, etc.).
            props: Dictionary of properties for the browser control.
            with_navigation: If True, includes navigation bar.
        
        Returns:
            WebBrowser or WebBrowserPanel control instance.
        
        Raises:
            ViewerError: If WinFormPy is not installed.
        
        Example:
            >>> from winformpy import Form, DockStyle, Application
            >>> 
            >>> class DocViewer(Form):
            ...     def __init__(self, doc):
            ...         super().__init__()
            ...         self.Text = doc.title
            ...         self.Width = 800
            ...         self.Height = 600
            ...         doc.preview_embedded(self, {'Dock': DockStyle.Fill})
            >>> 
            >>> doc = Document(title="Invoice", ...)
            >>> viewer = DocViewer(doc)
            >>> Application.Run(viewer)
        """
        from .viewer import open_in_embedded_browser
        
        html = self._last_rendered or self.render()
        return open_in_embedded_browser(parent, html, props, with_navigation)

    def create_viewer_form(
        self,
        title: str | None = None,
        width: int = 900,
        height: int = 700,
        with_navigation: bool = True,
    ) -> Any:
        """Create a WinFormPy Form to display this document.
        
        Creates a standalone Form window with an embedded browser
        displaying the document content. Call Application.Run(form)
        or form.Show() to display it.
        
        Requires WinFormPy and tkinterweb to be installed.
        
        Args:
            title: Window title (defaults to document title).
            width: Form width in pixels.
            height: Form height in pixels.
            with_navigation: If True, includes navigation bar.
        
        Returns:
            A WinFormPy Form instance ready to be displayed.
        
        Raises:
            ViewerError: If WinFormPy is not installed.
        
        Example:
            >>> from winformpy import Application
            >>> 
            >>> report = Report(title="Sales Report")
            >>> report.add_page().add_section(...)
            >>> 
            >>> viewer = report.create_viewer_form()
            >>> Application.Run(viewer)
        """
        from .viewer import check_winformpy_available
        from .exceptions import ViewerError
        
        if not check_winformpy_available():
            raise ViewerError(
                "WinFormPy is not installed. Install with: pip install winformpy tkinterweb"
            )
        
        from winformpy import Form, DockStyle
        
        html = self._last_rendered or self.render()
        
        class DocumentViewerForm(Form):
            def __init__(inner_self):
                super().__init__()
                inner_self.Text = title or self.title
                inner_self.Width = width
                inner_self.Height = height
                inner_self.StartPosition = "CenterScreen"
                
                # Create embedded browser
                inner_self.browser = self.preview_embedded(
                    inner_self,
                    {'Dock': DockStyle.Fill},
                    with_navigation=with_navigation,
                )
        
        return DocumentViewerForm()
