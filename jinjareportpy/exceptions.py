"""Excepciones personalizadas para JinjaReportPy."""


class NinjaReportError(Exception):
    """Excepción base para todos los errores de JinjaReportPy."""

    pass


class TemplateNotFoundError(NinjaReportError):
    """Raised when a template file cannot be found."""

    def __init__(self, template_name: str, search_paths: list[str] | None = None):
        self.template_name = template_name
        self.search_paths = search_paths or []
        paths_info = f" in {self.search_paths}" if self.search_paths else ""
        super().__init__(f"Template '{template_name}' not found{paths_info}")


class AssetNotFoundError(NinjaReportError):
    """Raised when an asset (image, CSS, etc.) cannot be found."""

    def __init__(self, asset_path: str):
        self.asset_path = asset_path
        super().__init__(f"Asset not found: '{asset_path}'")


class ExportError(NinjaReportError):
    """Raised when export operation fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message)


class PDFExportError(ExportError):
    """Raised when PDF export fails."""

    pass


class ViewerError(NinjaReportError):
    """Raised when opening a viewer fails."""

    pass
