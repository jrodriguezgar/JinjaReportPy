"""
JinjaReportPy Configuration Module

Centralized configuration with multi-source resolution:
    Priority: Environment variables > Programmatic > Config file > Defaults

Environment Variables:
    JINJAREPORT_TEMPLATES_DIR: Path to templates directory
    JINJAREPORT_FORMATS_DIR: Path to formats directory
    JINJAREPORT_OUTPUT_DIR: Path to output directory
    JINJAREPORT_CONFIG_FILE: Path to config file (TOML)

Usage:
    from jinjareportpy.config import JinjaReportConfig, get_templates_dir
    
    # Option 1: Environment variables
    os.environ["JINJAREPORT_TEMPLATES_DIR"] = "/path/to/templates"
    
    # Option 2: Programmatic
    JinjaReportConfig.set_templates_dir("/path/to/templates")
    
    # Option 3: Custom config file
    JinjaReportConfig.load_from_file("/path/to/config.toml")
"""

import os
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger("jinjareportpy.config")

# Try to import TOML parser
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

# Module-level defaults
_MODULE_DIR = Path(__file__).parent
_DEFAULT_TEMPLATES_DIR = _MODULE_DIR / "templates"
_DEFAULT_FORMATS_DIR = _MODULE_DIR / "formats"
_DEFAULT_OUTPUT_DIR = _MODULE_DIR / "output"
_DEFAULT_CONFIG_FILE = _MODULE_DIR.parent / "jinjareportpy.toml"


class JinjaReportConfig:
    """Central configuration with priority: env > programmatic > file > default.
    
    This class provides a centralized way to configure JinjaReportPy paths.
    All methods are class methods - no instantiation needed.
    
    Example:
        >>> JinjaReportConfig.set_templates_dir("./my_templates")
        >>> templates = JinjaReportConfig.get_templates_dir()
        
        >>> # Or use environment variables
        >>> os.environ["JINJAREPORT_OUTPUT_DIR"] = "/custom/output"
    """
    
    # Class-level storage
    _templates_dir: Optional[Path] = None
    _formats_dir: Optional[Path] = None
    _output_dir: Optional[Path] = None
    _config_data: Dict[str, Any] = {}
    _config_loaded: bool = False
    
    # --- Templates Dir ---
    @classmethod
    def set_templates_dir(cls, path: Union[str, Path]) -> None:
        """Set templates directory programmatically."""
        path = Path(path)
        if not path.is_absolute():
            path = Path.cwd() / path
        cls._templates_dir = path
        logger.info(f"Templates directory set to: {path}")
    
    @classmethod
    def get_templates_dir(cls) -> Path:
        """Get templates directory with priority resolution."""
        # 1. Environment variable
        env_path = os.environ.get("JINJAREPORT_TEMPLATES_DIR")
        if env_path:
            p = Path(env_path)
            return p if p.is_absolute() else Path.cwd() / p
        
        # 2. Programmatic
        if cls._templates_dir is not None:
            return cls._templates_dir
        
        # 3. Config file
        cls._ensure_config_loaded()
        config_path = cls._config_data.get("paths", {}).get("templates_dir", "")
        if config_path:
            p = Path(config_path)
            return p if p.is_absolute() else _MODULE_DIR.parent / p
        
        # 4. Default
        return _DEFAULT_TEMPLATES_DIR
    
    # --- Formats Dir ---
    @classmethod
    def set_formats_dir(cls, path: Union[str, Path]) -> None:
        """Set formats directory programmatically."""
        path = Path(path)
        if not path.is_absolute():
            path = Path.cwd() / path
        cls._formats_dir = path
        logger.info(f"Formats directory set to: {path}")
    
    @classmethod
    def get_formats_dir(cls) -> Path:
        """Get formats directory with priority resolution."""
        # 1. Environment variable
        env_path = os.environ.get("JINJAREPORT_FORMATS_DIR")
        if env_path:
            p = Path(env_path)
            return p if p.is_absolute() else Path.cwd() / p
        
        # 2. Programmatic
        if cls._formats_dir is not None:
            return cls._formats_dir
        
        # 3. Config file
        cls._ensure_config_loaded()
        config_path = cls._config_data.get("paths", {}).get("formats_dir", "")
        if config_path:
            p = Path(config_path)
            return p if p.is_absolute() else _MODULE_DIR.parent / p
        
        # 4. Default
        return _DEFAULT_FORMATS_DIR
    
    # --- Output Dir ---
    @classmethod
    def set_output_dir(cls, path: Union[str, Path]) -> None:
        """Set output directory programmatically."""
        path = Path(path)
        if not path.is_absolute():
            path = Path.cwd() / path
        cls._output_dir = path
        logger.info(f"Output directory set to: {path}")
    
    @classmethod
    def get_output_dir(cls) -> Path:
        """Get output directory with priority resolution."""
        # 1. Environment variable
        env_path = os.environ.get("JINJAREPORT_OUTPUT_DIR")
        if env_path:
            p = Path(env_path)
            return p if p.is_absolute() else Path.cwd() / p
        
        # 2. Programmatic
        if cls._output_dir is not None:
            return cls._output_dir
        
        # 3. Config file
        cls._ensure_config_loaded()
        config_path = cls._config_data.get("paths", {}).get("output_dir", "")
        if config_path:
            p = Path(config_path)
            return p if p.is_absolute() else _MODULE_DIR.parent / p
        
        # 4. Default
        return _DEFAULT_OUTPUT_DIR
    
    # --- Config File ---
    @classmethod
    def load_from_file(cls, config_path: Union[str, Path]) -> None:
        """Load configuration from a TOML file.
        
        Args:
            config_path: Path to the TOML configuration file.
        """
        if tomllib is None:
            logger.warning("TOML parser not available (install tomli for Python <3.11)")
            return
        
        config_path = Path(config_path)
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return
        
        with open(config_path, "rb") as f:
            cls._config_data = tomllib.load(f)
        cls._config_loaded = True
        logger.info(f"Configuration loaded from: {config_path}")
    
    @classmethod
    def _ensure_config_loaded(cls) -> None:
        """Lazily load config file if not already loaded."""
        if cls._config_loaded:
            return
        
        if tomllib is None:
            cls._config_loaded = True
            return
        
        env_config = os.environ.get("JINJAREPORT_CONFIG_FILE")
        config_path = Path(env_config) if env_config else _DEFAULT_CONFIG_FILE
        
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    cls._config_data = tomllib.load(f)
                logger.debug(f"Configuration loaded from: {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        cls._config_loaded = True
    
    @classmethod
    def reset(cls) -> None:
        """Reset all configuration to defaults."""
        cls._templates_dir = None
        cls._formats_dir = None
        cls._output_dir = None
        cls._config_data = {}
        cls._config_loaded = False
        logger.info("Configuration reset to defaults")
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all current configuration values.
        
        Returns:
            Dictionary with all resolved paths and raw config data.
        """
        cls._ensure_config_loaded()
        return {
            "templates_dir": str(cls.get_templates_dir()),
            "formats_dir": str(cls.get_formats_dir()),
            "output_dir": str(cls.get_output_dir()),
            "config_file_data": cls._config_data,
            "env_templates_dir": os.environ.get("JINJAREPORT_TEMPLATES_DIR"),
            "env_formats_dir": os.environ.get("JINJAREPORT_FORMATS_DIR"),
            "env_output_dir": os.environ.get("JINJAREPORT_OUTPUT_DIR"),
        }


# Convenience functions
def get_templates_dir() -> Path:
    """Get templates directory (convenience wrapper)."""
    return JinjaReportConfig.get_templates_dir()


def set_templates_dir(path: Union[str, Path]) -> None:
    """Set templates directory (convenience wrapper)."""
    JinjaReportConfig.set_templates_dir(path)


def get_formats_dir() -> Path:
    """Get formats directory (convenience wrapper)."""
    return JinjaReportConfig.get_formats_dir()


def set_formats_dir(path: Union[str, Path]) -> None:
    """Set formats directory (convenience wrapper)."""
    JinjaReportConfig.set_formats_dir(path)


def get_output_dir() -> Path:
    """Get output directory (convenience wrapper)."""
    return JinjaReportConfig.get_output_dir()


def set_output_dir(path: Union[str, Path]) -> None:
    """Set output directory (convenience wrapper)."""
    JinjaReportConfig.set_output_dir(path)


def _default_output_dir() -> Path:
    """Return the default output directory (uses centralized config)."""
    return JinjaReportConfig.get_output_dir()


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
    output_dir: Path = field(default_factory=_default_output_dir)
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
