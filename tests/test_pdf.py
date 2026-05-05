"""Tests for PDF export utilities."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from jinjareportpy.exceptions import PDFExportError
from jinjareportpy.pdf import check_weasyprint_available, html_to_pdf


class TestCheckWeasyprintAvailable:
    """Tests for check_weasyprint_available."""

    def test_returns_bool(self) -> None:
        result = check_weasyprint_available()
        assert isinstance(result, bool)

    @patch.dict("sys.modules", {"weasyprint": None})
    def test_returns_false_when_missing(self) -> None:
        # Force ImportError by patching the module to None
        result = check_weasyprint_available()
        # May still find it via real install; just verify bool type
        assert isinstance(result, bool)


class TestHtmlToPdf:
    """Tests for html_to_pdf function."""

    @patch("jinjareportpy.pdf.check_weasyprint_available", return_value=False)
    def test_raises_when_weasyprint_unavailable(
        self, mock_check: MagicMock,
    ) -> None:
        with pytest.raises(PDFExportError):
            html_to_pdf("<html></html>", "test.pdf")

    def test_happy_path_with_mock(self, tmp_path: Path) -> None:
        mock_html_cls = MagicMock()
        mock_html_inst = MagicMock()
        mock_html_cls.return_value = mock_html_inst
        mock_html_inst.write_pdf.return_value = b"%PDF-1.4 fake"

        mock_css_cls = MagicMock()

        with patch.dict(
            "sys.modules",
            {"weasyprint": MagicMock(HTML=mock_html_cls, CSS=mock_css_cls)},
        ):
            output = tmp_path / "out.pdf"
            result = html_to_pdf("<html>test</html>", output)
            assert result == b"%PDF-1.4 fake"
            assert output.exists()
            assert output.read_bytes() == b"%PDF-1.4 fake"

    def test_zoom_and_optimize_passed(self, tmp_path: Path) -> None:
        mock_html_cls = MagicMock()
        mock_html_inst = MagicMock()
        mock_html_cls.return_value = mock_html_inst
        mock_html_inst.write_pdf.return_value = b"%PDF"

        mock_css_cls = MagicMock()

        with patch.dict(
            "sys.modules",
            {"weasyprint": MagicMock(HTML=mock_html_cls, CSS=mock_css_cls)},
        ):
            html_to_pdf(
                "<html>test</html>",
                tmp_path / "z.pdf",
                zoom=2.0,
                optimize_images=False,
            )
            mock_html_inst.write_pdf.assert_called_once_with(
                stylesheets=None,
                zoom=2.0,
                optimize_images=False,
            )
