"""Tests for viewer utilities."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from jinjareportpy.exceptions import ViewerError
from jinjareportpy.viewer import (
    ReportViewer,
    check_winformpy_available,
    open_in_browser,
    open_pdf_viewer,
)


class TestReportViewer:
    """Tests for ReportViewer class."""

    def test_initial_state(self) -> None:
        viewer = ReportViewer()
        assert viewer.has_window is False

    def test_reset(self) -> None:
        viewer = ReportViewer()
        viewer._window_opened = True
        viewer.reset()
        assert viewer.has_window is False

    def test_open_nonexistent_file_raises(self, tmp_path: Path) -> None:
        viewer = ReportViewer()
        with pytest.raises(ViewerError, match="not found"):
            viewer.open(tmp_path / "missing.html")

    @patch("webbrowser.open_new")
    def test_open_sets_window_flag(
        self, mock_open: MagicMock, tmp_path: Path,
    ) -> None:
        html_file = tmp_path / "test.html"
        html_file.write_text("<html></html>", encoding="utf-8")

        viewer = ReportViewer()
        viewer.open(html_file)
        assert viewer.has_window is True
        mock_open.assert_called_once()

    @patch("webbrowser.open_new_tab")
    @patch("webbrowser.open_new")
    def test_second_open_uses_tab(
        self,
        mock_new: MagicMock,
        mock_tab: MagicMock,
        tmp_path: Path,
    ) -> None:
        html_file = tmp_path / "test.html"
        html_file.write_text("<html></html>", encoding="utf-8")

        viewer = ReportViewer()
        viewer.open(html_file)  # first → new window
        viewer.open(html_file)  # second → new tab
        mock_new.assert_called_once()
        mock_tab.assert_called_once()


class TestOpenInBrowser:
    """Tests for open_in_browser module function."""

    def test_raises_when_no_args(self) -> None:
        with pytest.raises(ViewerError, match="Either"):
            open_in_browser()

    @patch("webbrowser.open_new")
    def test_open_by_path(self, mock_open: MagicMock, tmp_path: Path) -> None:
        html_file = tmp_path / "report.html"
        html_file.write_text("<html></html>", encoding="utf-8")
        from jinjareportpy.viewer import reset_viewer
        reset_viewer()
        result = open_in_browser(html_path=html_file)
        assert result == html_file
        mock_open.assert_called_once()

    @patch("webbrowser.open_new")
    def test_open_by_content(self, mock_open: MagicMock) -> None:
        from jinjareportpy.viewer import reset_viewer
        reset_viewer()
        result = open_in_browser(html_content="<html>test</html>")
        assert result.exists()
        mock_open.assert_called_once()


class TestOpenPdfViewer:
    """Tests for open_pdf_viewer module function."""

    def test_raises_for_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(ViewerError, match="not found"):
            open_pdf_viewer(tmp_path / "missing.pdf")

    @patch("jinjareportpy.viewer._open_with_default_app")
    def test_opens_existing_pdf(
        self, mock_app: MagicMock, tmp_path: Path,
    ) -> None:
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake")
        open_pdf_viewer(pdf_file)
        mock_app.assert_called_once_with(pdf_file)


class TestCheckWinformpyAvailable:
    """Tests for check_winformpy_available."""

    def test_returns_bool(self) -> None:
        result = check_winformpy_available()
        assert isinstance(result, bool)


class TestReportViewerCleanup:
    """Tests for ReportViewer temp file cleanup."""

    @patch("webbrowser.open_new")
    def test_cleanup_removes_temp_files(self, mock_open: MagicMock) -> None:
        viewer = ReportViewer()
        path = viewer.open_content("<html>test</html>", filename="cleanup_test.html")
        assert path.exists()
        viewer.cleanup()
        assert not path.exists()
        assert viewer._temp_files == []

    def test_cleanup_on_empty_is_safe(self) -> None:
        viewer = ReportViewer()
        viewer.cleanup()  # should not raise

    @patch("webbrowser.open_new")
    def test_open_content_generates_unique_filenames(
        self, mock_open: MagicMock,
    ) -> None:
        """Concurrent calls must produce different temp file paths."""
        viewer = ReportViewer()
        path1 = viewer.open_content("<html>a</html>")
        path2 = viewer.open_content("<html>b</html>")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()
        viewer.cleanup()
