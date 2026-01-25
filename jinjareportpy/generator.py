"""Clase ReportGenerator - API principal para JinjaReportPy (legacy)."""

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .assets import AssetManager
from .config import ReportConfig, PageSize, Orientation
from .exceptions import TemplateNotFoundError, ExportError
from .filters import register_default_filters
from .pdf import html_to_pdf, get_print_css, check_weasyprint_available
from .viewer import open_in_browser, open_pdf_viewer


class ReportGenerator:
    """Main class for generating professional multi-page reports.

    This class provides a clean API for:
    - Loading and rendering Jinja2 templates
    - Managing assets (images, CSS) with Base64 embedding
    - Exporting to HTML and PDF formats
    - Opening reports in browser or PDF viewer

    Example:
        >>> from jinjareportpy import ReportGenerator, ReportConfig
        >>> config = ReportConfig(template_dirs=["./templates"])
        >>> generator = ReportGenerator(config)
        >>> html = generator.render("invoice.html", {"items": items})
        >>> generator.export_pdf(html, "invoice.pdf")
    """

    def __init__(
        self,
        config: ReportConfig | None = None,
        template_dirs: list[Path | str] | None = None,
        assets_dir: Path | str | None = None,
    ):
        """Initialize the ReportGenerator.

        Args:
            config: ReportConfig instance with all settings.
            template_dirs: List of template directories (alternative to config).
            assets_dir: Assets directory (alternative to config).
        """
        # Use provided config or create default
        if config is None:
            config = ReportConfig()

        # Override with direct parameters if provided
        if template_dirs:
            config.template_dirs = [
                Path(d) if isinstance(d, str) else d for d in template_dirs
            ]
        if assets_dir:
            config.assets_dir = Path(assets_dir) if isinstance(assets_dir, str) else assets_dir

        self.config = config
        self._env: Environment | None = None
        self._asset_manager: AssetManager | None = None
        self._last_rendered_html: str | None = None

    @property
    def env(self) -> Environment:
        """Get or create the Jinja2 Environment.

        Returns:
            Configured Jinja2 Environment instance.
        """
        if self._env is None:
            self._env = self._create_environment()
        return self._env

    @property
    def assets(self) -> AssetManager:
        """Get the AssetManager instance.

        Returns:
            AssetManager for handling images and static files.
        """
        if self._asset_manager is None:
            assets_dirs = []
            if self.config.assets_dir:
                assets_dirs.append(self.config.assets_dir)
            # Also add template directories as asset sources
            assets_dirs.extend(self.config.template_dirs)
            self._asset_manager = AssetManager(assets_dirs)
        return self._asset_manager

    def _create_environment(self) -> Environment:
        """Create and configure the Jinja2 Environment.

        Returns:
            Configured Jinja2 Environment.
        """
        # Prepare template loaders
        template_paths = [str(p) for p in self.config.template_dirs if p.exists()]

        # Add built-in templates directory
        builtin_templates = Path(__file__).parent / "templates"
        if builtin_templates.exists():
            template_paths.append(str(builtin_templates))

        if not template_paths:
            # Create a default templates directory
            default_templates = Path.cwd() / "templates"
            default_templates.mkdir(exist_ok=True)
            template_paths.append(str(default_templates))

        loader = FileSystemLoader(template_paths)

        env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
            auto_reload=self.config.auto_reload,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register default filters
        register_default_filters(env)

        # Add global functions
        env.globals.update(
            {
                "asset": self.assets.to_base64_safe,
                "asset_url": self.assets.to_base64,
                "embed_css": self.assets.embed_css,
                "now": datetime.now,
                "page_size": self.config.page_size,
                "orientation": self.config.orientation,
            }
        )

        return env

    def add_filter(self, name: str, filter_func: callable) -> None:
        """Add a custom Jinja2 filter.

        Args:
            name: Filter name to use in templates.
            filter_func: Filter function.

        Example:
            >>> generator.add_filter("reverse", lambda s: s[::-1])
            >>> # In template: {{ "hello" | reverse }}
        """
        self.env.filters[name] = filter_func

    def add_global(self, name: str, value: Any) -> None:
        """Add a global variable available in all templates.

        Args:
            name: Variable name.
            value: Variable value (can be any type including functions).
        """
        self.env.globals[name] = value

    def render(
        self,
        template_name: str,
        context: dict[str, Any] | None = None,
        **extra_context: Any,
    ) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of the template file.
            context: Dictionary of template variables.
            **extra_context: Additional variables passed as kwargs.

        Returns:
            Rendered HTML string.

        Raises:
            TemplateNotFoundError: If template cannot be found.

        Example:
            >>> html = generator.render("report.html", {
            ...     "title": "Sales Report",
            ...     "data": sales_data
            ... })
        """
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            raise TemplateNotFoundError(
                template_name,
                [str(p) for p in self.config.template_dirs],
            ) from e

        # Merge contexts
        full_context = context.copy() if context else {}
        full_context.update(extra_context)

        # Add report metadata
        full_context.setdefault("_report", {
            "generated_at": datetime.now(),
            "page_size": self.config.page_size.name,
            "orientation": self.config.orientation.value,
        })

        self._last_rendered_html = template.render(**full_context)
        return self._last_rendered_html

    def render_string(
        self,
        template_string: str,
        context: dict[str, Any] | None = None,
        **extra_context: Any,
    ) -> str:
        """Render a template from a string.

        Args:
            template_string: Jinja2 template as string.
            context: Dictionary of template variables.
            **extra_context: Additional variables.

        Returns:
            Rendered HTML string.

        Example:
            >>> html = generator.render_string(
            ...     "<h1>{{ title }}</h1>",
            ...     {"title": "Hello World"}
            ... )
        """
        template = self.env.from_string(template_string)
        full_context = context.copy() if context else {}
        full_context.update(extra_context)

        self._last_rendered_html = template.render(**full_context)
        return self._last_rendered_html

    def export_html(
        self,
        html_content: str | None = None,
        output_path: Path | str | None = None,
        filename: str = "report.html",
    ) -> Path:
        """Save rendered HTML to a file.

        Args:
            html_content: HTML string to save. Uses last rendered if None.
            output_path: Full path for output file.
            filename: Filename if output_path is a directory.

        Returns:
            Path to the saved file.

        Raises:
            ExportError: If no content to export or save fails.
        """
        content = html_content or self._last_rendered_html
        if content is None:
            raise ExportError("No HTML content to export. Call render() first.")

        if output_path is None:
            output_path = self.config.output_dir / filename
        else:
            output_path = Path(output_path)
            if output_path.is_dir():
                output_path = output_path / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding=self.config.encoding)

        return output_path

    def export_pdf(
        self,
        html_content: str | None = None,
        output_path: Path | str | None = None,
        filename: str = "report.pdf",
        include_print_css: bool = True,
    ) -> Path:
        """Export HTML content to PDF.

        Args:
            html_content: HTML string to convert. Uses last rendered if None.
            output_path: Full path for output file.
            filename: Filename if output_path is a directory.
            include_print_css: Include default print CSS.

        Returns:
            Path to the saved PDF file.

        Raises:
            ExportError: If export fails.
            PDFExportError: If WeasyPrint is not available.
        """
        content = html_content or self._last_rendered_html
        if content is None:
            raise ExportError("No HTML content to export. Call render() first.")

        if output_path is None:
            output_path = self.config.output_dir / filename
        else:
            output_path = Path(output_path)
            if output_path.is_dir():
                output_path = output_path / filename

        # Prepare stylesheets
        stylesheets = []
        if include_print_css:
            width, height = self.config.effective_page_size
            stylesheets.append(get_print_css(width, height))

        html_to_pdf(content, output_path, stylesheets)

        return output_path

    def preview_html(
        self,
        html_content: str | None = None,
        browser: str | None = None,
    ) -> Path:
        """Open HTML content in a web browser for preview.

        Args:
            html_content: HTML to preview. Uses last rendered if None.
            browser: Custom browser command (None = system default).

        Returns:
            Path to the temporary HTML file.
        """
        content = html_content or self._last_rendered_html
        if content is None:
            raise ExportError("No HTML content to preview. Call render() first.")

        return open_in_browser(
            html_content=content,
            browser_command=browser or self.config.browser_command,
        )

    def preview_pdf(
        self,
        html_content: str | None = None,
        viewer: str | None = None,
    ) -> Path:
        """Generate PDF and open in PDF viewer.

        Args:
            html_content: HTML to convert and preview.
            viewer: Custom PDF viewer command (None = system default).

        Returns:
            Path to the PDF file.
        """
        import tempfile
        from pathlib import Path as PathLib

        content = html_content or self._last_rendered_html
        if content is None:
            raise ExportError("No HTML content to preview. Call render() first.")

        # Create temp PDF
        temp_dir = PathLib(tempfile.gettempdir()) / "jinjareportpy"
        temp_dir.mkdir(exist_ok=True)
        pdf_path = temp_dir / f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        self.export_pdf(content, pdf_path)
        open_pdf_viewer(pdf_path, viewer or self.config.pdf_viewer_command)

        return pdf_path

    @staticmethod
    def is_pdf_available() -> bool:
        """Check if PDF export is available (WeasyPrint installed).

        Returns:
            True if PDF export is available.
        """
        return check_weasyprint_available()

    def __repr__(self) -> str:
        return (
            f"ReportGenerator(template_dirs={self.config.template_dirs}, "
            f"page_size={self.config.page_size.name})"
        )
