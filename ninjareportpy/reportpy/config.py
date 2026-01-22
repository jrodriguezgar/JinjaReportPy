"""Clases de configuración para NinjaReportPy."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class PageSize(Enum):
    """Standard page sizes for print reports."""

    A4 = ("210mm", "297mm")
    A3 = ("297mm", "420mm")
    LETTER = ("8.5in", "11in")
    LEGAL = ("8.5in", "14in")

    @property
    def width(self) -> str:
        return self.value[0]

    @property
    def height(self) -> str:
        return self.value[1]


class Orientation(Enum):
    """Page orientation for reports."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass
class ReportConfig:
    """Configuration for report generation.

    Attributes:
        template_dirs: List of directories to search for templates.
        assets_dir: Directory containing images, logos, and other assets.
        output_dir: Default directory for saving generated reports.
        page_size: Page size for print/PDF output.
        orientation: Page orientation (portrait/landscape).
        encoding: Character encoding for templates and output.
        auto_reload: Enable template auto-reload (useful for development).
        locale: Locale for date/number formatting (e.g., 'es_ES', 'en_US').
        browser_command: Custom browser command for preview (None = system default).
        pdf_viewer_command: Custom PDF viewer command (None = system default).
    """

    template_dirs: list[Path] = field(default_factory=list)
    assets_dir: Path | None = None
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    page_size: PageSize = PageSize.A4
    orientation: Orientation = Orientation.PORTRAIT
    encoding: str = "utf-8"
    auto_reload: bool = False
    locale: str = "es_ES"
    browser_command: str | None = None
    pdf_viewer_command: str | None = None

    # PDF-specific options
    pdf_options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and convert paths."""
        # Convert string paths to Path objects
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        if isinstance(self.assets_dir, str):
            self.assets_dir = Path(self.assets_dir)

        self.template_dirs = [
            Path(p) if isinstance(p, str) else p for p in self.template_dirs
        ]

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def effective_page_size(self) -> tuple[str, str]:
        """Get page dimensions considering orientation."""
        width, height = self.page_size.width, self.page_size.height
        if self.orientation == Orientation.LANDSCAPE:
            return (height, width)
        return (width, height)
