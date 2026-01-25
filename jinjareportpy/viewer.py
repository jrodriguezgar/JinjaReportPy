"""Viewer utilities for opening reports in browser or PDF viewer."""

import os
import platform
import shutil
import subprocess
import tempfile
import webbrowser
from pathlib import Path

from .exceptions import ViewerError


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
        temp_dir = Path(tempfile.gettempdir()) / "jinjareportpy"
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
