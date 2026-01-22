"""Tests for AssetManager."""

import pytest
from pathlib import Path
import tempfile
import base64

from reportpy.assets import AssetManager
from reportpy.exceptions import AssetNotFoundError


class TestAssetManager:
    """Tests for AssetManager class."""

    @pytest.fixture
    def temp_assets_dir(self):
        """Create a temporary directory with test assets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assets_dir = Path(tmpdir)
            
            # Create a test image (1x1 red PNG)
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
            )
            (assets_dir / "test.png").write_bytes(png_data)
            
            # Create a test CSS file
            (assets_dir / "style.css").write_text("body { color: red; }")
            
            # Create a subdirectory with assets
            subdir = assets_dir / "images"
            subdir.mkdir()
            (subdir / "logo.png").write_bytes(png_data)
            
            yield assets_dir

    def test_create_asset_manager(self) -> None:
        """Test creating an AssetManager."""
        manager = AssetManager()
        assert manager.assets_dirs == []

    def test_add_directory(self, temp_assets_dir: Path) -> None:
        """Test adding a directory."""
        manager = AssetManager()
        manager.add_directory(temp_assets_dir)
        assert temp_assets_dir in manager.assets_dirs

    def test_find_asset(self, temp_assets_dir: Path) -> None:
        """Test finding an asset."""
        manager = AssetManager([temp_assets_dir])
        path = manager.find_asset("test.png")
        assert path.exists()
        assert path.name == "test.png"

    def test_find_asset_in_subdirectory(self, temp_assets_dir: Path) -> None:
        """Test finding an asset in subdirectory."""
        manager = AssetManager([temp_assets_dir])
        path = manager.find_asset("images/logo.png")
        assert path.exists()

    def test_find_asset_not_found(self, temp_assets_dir: Path) -> None:
        """Test that missing asset raises error."""
        manager = AssetManager([temp_assets_dir])
        with pytest.raises(AssetNotFoundError):
            manager.find_asset("nonexistent.png")

    def test_to_base64(self, temp_assets_dir: Path) -> None:
        """Test converting image to Base64."""
        manager = AssetManager([temp_assets_dir])
        result = manager.to_base64("test.png")
        
        assert result.startswith("data:image/png;base64,")
        assert len(result) > 30

    def test_to_base64_safe(self, temp_assets_dir: Path) -> None:
        """Test safe Base64 conversion with fallback."""
        manager = AssetManager([temp_assets_dir])
        
        # Existing file
        result = manager.to_base64_safe("test.png")
        assert result.startswith("data:")
        
        # Non-existing file with fallback
        result = manager.to_base64_safe("missing.png", "fallback")
        assert result == "fallback"

    def test_read_css(self, temp_assets_dir: Path) -> None:
        """Test reading a CSS file."""
        manager = AssetManager([temp_assets_dir])
        css = manager.read_css("style.css")
        assert "color: red" in css

    def test_embed_css(self, temp_assets_dir: Path) -> None:
        """Test embedding CSS in style tags."""
        manager = AssetManager([temp_assets_dir])
        result = manager.embed_css("style.css")
        assert "<style>" in result
        assert "</style>" in result
        assert "color: red" in result

    def test_cache_clearing(self, temp_assets_dir: Path) -> None:
        """Test cache clearing."""
        manager = AssetManager([temp_assets_dir])
        
        # First call should cache
        manager.to_base64("test.png")
        
        # Clear cache
        manager.clear_cache()
        
        # Should work after clearing
        result = manager.to_base64("test.png")
        assert result.startswith("data:")
