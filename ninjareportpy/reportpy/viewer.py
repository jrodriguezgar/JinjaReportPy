"""Viewer utilities for opening reports in browser, PDF viewer, or embedded panels."""

import os
import platform
import shutil
import subprocess
import tempfile
import webbrowser
from pathlib import Path
from typing import Any

from .exceptions import ViewerError


# Type hint for WinFormPy controls (optional dependency)
try:
    from winformpy.ui_elements.web_browser import WebBrowser, WebBrowserPanel
    WINFORMPY_AVAILABLE = True
except ImportError:
    WINFORMPY_AVAILABLE = False
    WebBrowser = Any
    WebBrowserPanel = Any


def open_in_browser(
    html_content: str | None = None,
    html_path: Path | str | None = None,
    browser_command: str | None = None,
) -> Path:
    """Open HTML content or file in a web browser.

    Args:
        html_content: HTML string to display.
        html_path: Path to an existing HTML file.
        browser_command: Custom browser command (None = system default).

    Returns:
        Path to the HTML file opened.

    Raises:
        ViewerError: If neither content nor path provided.
    """
    if html_content is None and html_path is None:
        raise ViewerError("Either html_content or html_path must be provided")

    # If content provided, save to temp file
    if html_content is not None:
        temp_dir = Path(tempfile.gettempdir()) / "ninjareportpy"
        temp_dir.mkdir(exist_ok=True)
        html_path = temp_dir / f"report_{os.getpid()}.html"
        Path(html_path).write_text(html_content, encoding="utf-8")

    html_path = Path(html_path)

    if not html_path.exists():
        raise ViewerError(f"HTML file not found: {html_path}")

    # Convert to file URL
    file_url = html_path.as_uri()

    try:
        if browser_command:
            # Use custom browser command
            subprocess.Popen([browser_command, file_url])
        else:
            # Use system default browser
            webbrowser.open(file_url)
    except Exception as e:
        raise ViewerError(f"Failed to open browser: {e}")

    return html_path


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


def check_winformpy_available() -> bool:
    """Check if WinFormPy is installed and available.
    
    Returns:
        True if WinFormPy and WebBrowser components are available.
    """
    return WINFORMPY_AVAILABLE


def create_embedded_browser(parent: Any, props: dict | None = None) -> "WebBrowser":
    """Create a WinFormPy WebBrowser control for embedding HTML content.
    
    Requires WinFormPy to be installed (pip install winformpy).
    Also requires tkinterweb: pip install tkinterweb
    
    Args:
        parent: Parent WinFormPy control (Form, Panel, etc.).
        props: Dictionary of properties to apply to the WebBrowser control.
    
    Returns:
        WebBrowser control instance.
    
    Raises:
        ViewerError: If WinFormPy is not installed.
    
    Example:
        >>> from winformpy import Form, DockStyle
        >>> form = Form()
        >>> browser = create_embedded_browser(form, {'Dock': DockStyle.Fill})
        >>> browser.DocumentText = "<h1>Hello World</h1>"
    """
    if not WINFORMPY_AVAILABLE:
        raise ViewerError(
            "WinFormPy is not installed. Install with: pip install winformpy tkinterweb"
        )
    
    from winformpy.ui_elements.web_browser import WebBrowser
    
    props = props or {}
    return WebBrowser(parent, props)


def create_browser_panel(parent: Any, props: dict | None = None) -> "WebBrowserPanel":
    """Create a WinFormPy WebBrowserPanel with navigation bar.
    
    The panel includes a navigation bar with back, forward, refresh,
    home buttons and an address bar.
    
    Requires WinFormPy to be installed (pip install winformpy).
    Also requires tkinterweb: pip install tkinterweb
    
    Args:
        parent: Parent WinFormPy control (Form, Panel, etc.).
        props: Dictionary of properties to apply to the panel.
    
    Returns:
        WebBrowserPanel control instance.
    
    Raises:
        ViewerError: If WinFormPy is not installed.
    
    Example:
        >>> from winformpy import Form, DockStyle
        >>> form = Form()
        >>> panel = create_browser_panel(form, {'Dock': DockStyle.Fill})
        >>> panel.browser.DocumentText = "<h1>Report Content</h1>"
    """
    if not WINFORMPY_AVAILABLE:
        raise ViewerError(
            "WinFormPy is not installed. Install with: pip install winformpy tkinterweb"
        )
    
    from winformpy.ui_elements.web_browser import WebBrowserPanel
    
    props = props or {}
    return WebBrowserPanel(parent, props)


def display_html_in_browser(
    browser: "WebBrowser",
    html_content: str,
) -> None:
    """Display HTML content in a WinFormPy WebBrowser control.
    
    Args:
        browser: WebBrowser control instance.
        html_content: HTML string to display.
    
    Example:
        >>> browser = create_embedded_browser(form)
        >>> display_html_in_browser(browser, "<h1>My Report</h1>")
    """
    browser.DocumentText = html_content


def display_html_in_panel(
    panel: "WebBrowserPanel",
    html_content: str,
) -> None:
    """Display HTML content in a WinFormPy WebBrowserPanel.
    
    Args:
        panel: WebBrowserPanel instance.
        html_content: HTML string to display.
    
    Example:
        >>> panel = create_browser_panel(form)
        >>> display_html_in_panel(panel, "<h1>My Report</h1>")
    """
    # WebBrowserPanel has a browser property that gives access to the WebBrowser
    if hasattr(panel, 'browser'):
        panel.browser.DocumentText = html_content
    else:
        # Fallback: try to set DocumentText directly
        panel.DocumentText = html_content


def open_in_embedded_browser(
    parent: Any,
    html_content: str,
    props: dict | None = None,
    with_navigation: bool = False,
) -> "WebBrowser | WebBrowserPanel":
    """Create and configure a WinFormPy browser control with HTML content.
    
    This is a convenience function that creates an embedded browser
    and displays the HTML content in a single call.
    
    Args:
        parent: Parent WinFormPy control (Form, Panel, etc.).
        html_content: HTML string to display.
        props: Dictionary of properties to apply to the browser control.
        with_navigation: If True, creates a WebBrowserPanel with navigation bar.
                        If False, creates a basic WebBrowser control.
    
    Returns:
        WebBrowser or WebBrowserPanel control instance.
    
    Raises:
        ViewerError: If WinFormPy is not installed.
    
    Example:
        >>> from winformpy import Form, DockStyle, Application
        >>> 
        >>> class ReportViewer(Form):
        ...     def __init__(self, html):
        ...         super().__init__()
        ...         self.Text = "Report Viewer"
        ...         self.Width = 800
        ...         self.Height = 600
        ...         self.browser = open_in_embedded_browser(
        ...             self, html, 
        ...             props={'Dock': DockStyle.Fill},
        ...             with_navigation=True
        ...         )
        >>> 
        >>> # Usage with a report
        >>> report = Report(title="Sales Report")
        >>> html = report.render()
        >>> viewer = ReportViewer(html)
        >>> Application.Run(viewer)
    """
    if with_navigation:
        panel = create_browser_panel(parent, props)
        display_html_in_panel(panel, html_content)
        return panel
    else:
        browser = create_embedded_browser(parent, props)
        display_html_in_browser(browser, html_content)
        return browser
