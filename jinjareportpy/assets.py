"""Gestión de assets para JinjaReportPy - imágenes, logos y archivos estáticos."""

import base64
import mimetypes
from functools import lru_cache
from pathlib import Path

from .exceptions import AssetNotFoundError


class AssetManager:
    """Manages assets (images, logos, CSS) for report generation.

    Provides functionality to:
    - Locate assets in configured directories
    - Convert images to Base64 for self-contained HTML
    - Cache converted assets for performance
    """

    # Supported image MIME types
    SUPPORTED_IMAGE_TYPES = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".ico": "image/x-icon",
    }

    def __init__(self, assets_dirs: list[Path] | None = None):
        """Initialize the asset manager.

        Args:
            assets_dirs: List of directories to search for assets.
        """
        self.assets_dirs = assets_dirs or []

    def add_directory(self, directory: Path | str) -> None:
        """Add a directory to the search path.

        Args:
            directory: Directory path to add.
        """
        path = Path(directory) if isinstance(directory, str) else directory
        if path not in self.assets_dirs:
            self.assets_dirs.append(path)

    def find_asset(self, asset_name: str) -> Path:
        """Find an asset file in the configured directories.

        Args:
            asset_name: Name or relative path of the asset.

        Returns:
            Full path to the asset file.

        Raises:
            AssetNotFoundError: If asset cannot be found.
        """
        asset_path = Path(asset_name)

        # Check if it's an absolute path
        if asset_path.is_absolute() and asset_path.exists():
            return asset_path

        # Search in configured directories
        for directory in self.assets_dirs:
            full_path = directory / asset_name
            if full_path.exists():
                return full_path

        raise AssetNotFoundError(asset_name)

    @lru_cache(maxsize=128)
    def to_base64(self, asset_name: str) -> str:
        """Convert an image asset to a Base64 data URI.

        Args:
            asset_name: Name or path of the image file.

        Returns:
            Base64 data URI string ready for use in HTML img src.

        Raises:
            AssetNotFoundError: If asset cannot be found.
        """
        asset_path = self.find_asset(asset_name)
        mime_type = self._get_mime_type(asset_path)

        with open(asset_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        return f"data:{mime_type};base64,{encoded}"

    def to_base64_safe(self, asset_name: str, fallback: str = "") -> str:
        """Convert an image to Base64, returning fallback on error.

        Args:
            asset_name: Name or path of the image file.
            fallback: Value to return if asset not found.

        Returns:
            Base64 data URI or fallback value.
        """
        try:
            return self.to_base64(asset_name)
        except AssetNotFoundError:
            return fallback

    def read_css(self, css_name: str) -> str:
        """Read a CSS file and return its contents.

        Args:
            css_name: Name or path of the CSS file.

        Returns:
            CSS file contents as string.

        Raises:
            AssetNotFoundError: If CSS file cannot be found.
        """
        css_path = self.find_asset(css_name)
        return css_path.read_text(encoding="utf-8")

    def embed_css(self, css_name: str) -> str:
        """Read a CSS file and wrap it in style tags.

        Args:
            css_name: Name or path of the CSS file.

        Returns:
            CSS wrapped in <style> tags.
        """
        css_content = self.read_css(css_name)
        return f"<style>\n{css_content}\n</style>"

    def _get_mime_type(self, path: Path) -> str:
        """Get MIME type for a file.

        Args:
            path: Path to the file.

        Returns:
            MIME type string.
        """
        suffix = path.suffix.lower()
        if suffix in self.SUPPORTED_IMAGE_TYPES:
            return self.SUPPORTED_IMAGE_TYPES[suffix]

        # Fallback to mimetypes library
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type or "application/octet-stream"

    def clear_cache(self) -> None:
        """Clear the Base64 conversion cache."""
        self.to_base64.cache_clear()
