"""Viewer utilities for opening reports in browser or PDF viewer."""

from __future__ import annotations

import atexit
import logging
import os
import platform
import shutil
import subprocess
import tempfile
import uuid
import webbrowser
from pathlib import Path

from .exceptions import ViewerError

logger = logging.getLogger(__name__)

# Shared temp directory for all viewer temp files
_TEMP_DIR = Path(tempfile.gettempdir()) / "jinjareportpy"


class ReportViewer:
    """Manages browser windows for viewing reports.

    Opens the first report in a new browser window, and subsequent
    reports as new tabs in the same window.

    Example:
        >>> viewer = ReportViewer()
        >>> viewer.open("report1.html")  # Opens new window
        >>> viewer.open("report2.html")  # Opens new tab
        >>> viewer.open("report3.html")  # Opens new tab
        >>> viewer.reset()  # Next open will be new window

    For convenience, use the module-level functions:
        >>> open_in_browser("report.html")  # Uses shared viewer
        >>> open_in_new_window("report.html")  # Always new window
        >>> open_in_new_tab("report.html")  # Always new tab
    """

    def __init__(self) -> None:
        """Initialize the viewer."""
        self._window_opened: bool = False
        self._browser: webbrowser.BaseBrowser | None = None
        self._temp_files: list[Path] = []

    @property
    def has_window(self) -> bool:
        """Check if a browser window has been opened."""
        return self._window_opened

    def reset(self) -> None:
        """Reset state - next open will create a new window."""
        self._window_opened = False

    def cleanup(self) -> None:
        """Remove temporary HTML files created by this viewer."""
        for path in self._temp_files:
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                logger.debug("Failed to remove temp file: %s", path)
        self._temp_files.clear()

    def open(
        self,
        html_path: Path | str,
        force_new_window: bool = False,
        force_new_tab: bool = False,
    ) -> Path:
        """Open HTML file in browser (new window first time, then tabs).

        Args:
            html_path: Path to the HTML file.
            force_new_window: Always open in a new window.
            force_new_tab: Always open in a new tab.

        Returns:
            Path to the opened file.

        Raises:
            ViewerError: If file not found or browser fails.
        """
        html_path = Path(html_path)

        if not html_path.exists():
            raise ViewerError(f"HTML file not found: {html_path}")

        file_url = html_path.as_uri()

        try:
            if force_new_window or (not self._window_opened and not force_new_tab):
                # Open in new window
                webbrowser.open_new(file_url)
                self._window_opened = True
            else:
                # Open in new tab
                webbrowser.open_new_tab(file_url)
        except Exception as e:
            raise ViewerError(f"Failed to open browser: {e}")

        return html_path

    def open_content(
        self,
        html_content: str,
        filename: str = "report.html",
        force_new_window: bool = False,
        force_new_tab: bool = False,
    ) -> Path:
        """Open HTML content in browser (saves to temp file first).

        Args:
            html_content: HTML string to display.
            filename: Name for the temp file.
            force_new_window: Always open in a new window.
            force_new_tab: Always open in a new tab.

        Returns:
            Path to the temp file.
        """
        _TEMP_DIR.mkdir(exist_ok=True)
        # Add unique suffix to avoid collisions between concurrent processes
        stem = Path(filename).stem
        suffix = Path(filename).suffix or ".html"
        unique_name = f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"
        html_path = _TEMP_DIR / unique_name
        html_path.write_text(html_content, encoding="utf-8")
        self._temp_files.append(html_path)

        return self.open(html_path, force_new_window, force_new_tab)


# Shared viewer instance for module-level functions
_default_viewer = ReportViewer()
atexit.register(_default_viewer.cleanup)


def get_viewer() -> ReportViewer:
    """Get the shared ReportViewer instance.

    Returns:
        The module-level ReportViewer.
    """
    return _default_viewer


def reset_viewer() -> None:
    """Reset the shared viewer - next open will create a new window."""
    _default_viewer.reset()


def open_in_browser(
    html_content: str | None = None,
    html_path: Path | str | None = None,
    browser_command: str | None = None,
    new_window: bool | None = None,
) -> Path:
    """Open HTML content or file in a web browser.

    First call opens a new browser window. Subsequent calls open new tabs
    in the same window. Use reset_viewer() to start fresh.

    Args:
        html_content: HTML string to display.
        html_path: Path to an existing HTML file.
        browser_command: Custom browser command (None = system default).
        new_window: If True, force new window. If False, force new tab.
                   If None (default), auto-detect based on history.

    Returns:
        Path to the HTML file opened.

    Raises:
        ViewerError: If neither content nor path provided.

    Example:
        >>> open_in_browser(html_path="report1.html")  # New window
        >>> open_in_browser(html_path="report2.html")  # New tab
        >>> reset_viewer()
        >>> open_in_browser(html_path="report3.html")  # New window again
    """
    if html_content is None and html_path is None:
        raise ViewerError("Either html_content or html_path must be provided")

    # Handle custom browser command (legacy behavior)
    if browser_command:
        if not shutil.which(browser_command):
            raise ViewerError(f"Browser command not found: {browser_command}")

        if html_content is not None:
            _TEMP_DIR.mkdir(exist_ok=True)
            html_path = _TEMP_DIR / f"report_{uuid.uuid4().hex[:8]}.html"
            Path(html_path).write_text(html_content, encoding="utf-8")
            _default_viewer._temp_files.append(Path(html_path))

        html_path = Path(html_path)
        if not html_path.exists():
            raise ViewerError(f"HTML file not found: {html_path}")

        file_url = html_path.as_uri()
        try:
            subprocess.Popen([browser_command, file_url])
        except Exception as e:
            raise ViewerError(f"Failed to open browser: {e}")
        return html_path

    # Use ReportViewer for smart window/tab handling
    force_new_window = new_window is True
    force_new_tab = new_window is False

    if html_content is not None:
        return _default_viewer.open_content(
            html_content,
            force_new_window=force_new_window,
            force_new_tab=force_new_tab,
        )
    else:
        return _default_viewer.open(
            html_path,  # type: ignore
            force_new_window=force_new_window,
            force_new_tab=force_new_tab,
        )


def open_in_new_window(html_path: Path | str) -> Path:
    """Open HTML file in a new browser window.

    Args:
        html_path: Path to the HTML file.

    Returns:
        Path to the opened file.
    """
    return _default_viewer.open(html_path, force_new_window=True)


def open_in_new_tab(html_path: Path | str) -> Path:
    """Open HTML file in a new browser tab.

    Args:
        html_path: Path to the HTML file.

    Returns:
        Path to the opened file.
    """
    return _default_viewer.open(html_path, force_new_tab=True)


def open_pdf_viewer(
    pdf_path: Path | str,
    viewer_command: str | None = None,
) -> None:
    """Open a PDF file in the system PDF viewer.

    Args:
        pdf_path: Path to the PDF file.
        viewer_command: Custom PDF viewer command (None = system default).

    Raises:
        ViewerError: If file not found or viewer fails to open.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise ViewerError(f"PDF file not found: {pdf_path}")

    try:
        if viewer_command:
            # Validate command exists
            if not shutil.which(viewer_command):
                raise ViewerError(f"PDF viewer command not found: {viewer_command}")
            # Use custom viewer command
            subprocess.Popen([viewer_command, str(pdf_path)])
        else:
            # Use system default
            _open_with_default_app(pdf_path)
    except Exception as e:
        raise ViewerError(f"Failed to open PDF viewer: {e}")


def _open_with_default_app(file_path: Path) -> None:
    """Open a file with the system's default application.

    Args:
        file_path: Path to the file to open.
    """
    system = platform.system().lower()

    if system == "windows":
        os.startfile(str(file_path))  # type: ignore
    elif system == "darwin":  # macOS
        subprocess.Popen(["open", str(file_path)])
    else:  # Linux and others
        # Try common openers
        for opener in ["xdg-open", "gnome-open", "kde-open"]:
            if shutil.which(opener):
                subprocess.Popen([opener, str(file_path)])
                return
        raise ViewerError("No suitable file opener found on this system")


def check_winformpy_available() -> bool:
    """Check if WinFormPy and tkinterweb are installed.

    Returns:
        True if both packages are available, False otherwise.
    """
    try:
        import tkinterweb  # noqa: F401
        import winformpy  # noqa: F401

        return True
    except ImportError:
        return False


def open_in_embedded_browser(
    parent: object,
    html_content: str,
    props: dict | None = None,
    with_navigation: bool = False,
) -> object:
    """Display HTML content in a WinFormPy embedded browser control.

    Args:
        parent: Parent WinFormPy control (Form, Panel, etc.).
        html_content: HTML string to render.
        props: Dictionary of properties for the browser control.
        with_navigation: If True, includes a navigation bar.

    Returns:
        WebBrowser or WebBrowserPanel control instance.

    Raises:
        ViewerError: If WinFormPy or tkinterweb is not installed.
    """
    try:
        from winformpy import WebBrowser, WebBrowserPanel
    except ImportError as e:
        raise ViewerError(
            "WinFormPy is not installed. Install with: pip install winformpy tkinterweb"
        ) from e

    if with_navigation:
        browser = WebBrowserPanel(parent)
    else:
        browser = WebBrowser(parent)

    if props:
        for key, value in props.items():
            setattr(browser, key, value)

    browser.load_html(html_content)
    return browser


def get_available_browsers() -> list[str]:
    """Get list of available browsers on the system.

    Returns:
        List of browser names that are available.
    """
    browsers = []

    # Common browser commands to check
    browser_commands = {
        "chrome": ["chrome", "google-chrome", "google-chrome-stable"],
        "firefox": ["firefox"],
        "edge": ["msedge", "microsoft-edge"],
        "safari": ["safari"],
        "opera": ["opera"],
    }

    for name, commands in browser_commands.items():
        for cmd in commands:
            if shutil.which(cmd):
                browsers.append(name)
                break

    return browsers
