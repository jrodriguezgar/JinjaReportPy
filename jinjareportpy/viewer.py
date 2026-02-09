"""Viewer utilities for opening reports in browser or PDF viewer."""

import os
import platform
import shutil
import subprocess
import tempfile
import webbrowser
from pathlib import Path
from typing import Optional

from .exceptions import ViewerError


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
        self._browser: Optional[webbrowser.BaseBrowser] = None
    
    @property
    def has_window(self) -> bool:
        """Check if a browser window has been opened."""
        return self._window_opened
    
    def reset(self) -> None:
        """Reset state - next open will create a new window."""
        self._window_opened = False
    
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
        temp_dir = Path(tempfile.gettempdir()) / "jinjareportpy"
        temp_dir.mkdir(exist_ok=True)
        html_path = temp_dir / filename
        html_path.write_text(html_content, encoding="utf-8")
        
        return self.open(html_path, force_new_window, force_new_tab)


# Shared viewer instance for module-level functions
_default_viewer = ReportViewer()


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
        if html_content is not None:
            temp_dir = Path(tempfile.gettempdir()) / "jinjareportpy"
            temp_dir.mkdir(exist_ok=True)
            html_path = temp_dir / f"report_{os.getpid()}.html"
            Path(html_path).write_text(html_content, encoding="utf-8")
        
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
