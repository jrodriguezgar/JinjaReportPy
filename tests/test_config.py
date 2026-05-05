"""Tests for JinjaReportConfig multi-source priority resolution."""

from pathlib import Path

import pytest

from jinjareportpy.config import _DEFAULT_TEMPLATES_DIR, JinjaReportConfig


@pytest.fixture(autouse=True)
def _reset_config():
    """Reset JinjaReportConfig class state before and after each test."""
    JinjaReportConfig.reset()
    yield
    JinjaReportConfig.reset()


class TestConfigDefaults:
    """Verify default values when no env/programmatic/file is set."""

    def test_default_templates_dir(self) -> None:
        result = JinjaReportConfig.get_templates_dir()
        assert result == _DEFAULT_TEMPLATES_DIR

    def test_default_locale(self) -> None:
        result = JinjaReportConfig.get_locale()
        assert result == "es_ES"

    def test_default_page_size(self) -> None:
        result = JinjaReportConfig.get_page_size()
        assert result == "A4"

    def test_default_orientation(self) -> None:
        result = JinjaReportConfig.get_orientation()
        assert result == "portrait"

    def test_default_format(self) -> None:
        result = JinjaReportConfig.get_default_format()
        assert result == "default"

    def test_default_pdf_zoom(self) -> None:
        result = JinjaReportConfig.get_pdf_zoom()
        assert result == pytest.approx(1.0)


class TestConfigProgrammatic:
    """Verify programmatic set/get round-trip."""

    def test_set_templates_dir(self, tmp_path: Path) -> None:
        JinjaReportConfig.set_templates_dir(str(tmp_path))
        assert JinjaReportConfig.get_templates_dir() == tmp_path

    def test_set_locale(self) -> None:
        JinjaReportConfig.set_locale("en_US")
        assert JinjaReportConfig.get_locale() == "en_US"

    def test_set_page_size(self) -> None:
        JinjaReportConfig.set_page_size("LETTER")
        assert JinjaReportConfig.get_page_size() == "LETTER"

    def test_set_default_format(self) -> None:
        JinjaReportConfig.set_default_format("corporate")
        assert JinjaReportConfig.get_default_format() == "corporate"

    def test_set_pdf_zoom(self) -> None:
        JinjaReportConfig.set_pdf_zoom(1.5)
        assert JinjaReportConfig.get_pdf_zoom() == pytest.approx(1.5)


class TestConfigEnvOverride:
    """Verify environment variables take highest priority."""

    def test_env_overrides_programmatic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        JinjaReportConfig.set_locale("en_US")
        monkeypatch.setenv("JINJAREPORT_LOCALE", "fr_FR")
        assert JinjaReportConfig.get_locale() == "fr_FR"

    def test_env_override_page_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JINJAREPORT_PAGE_SIZE", "LEGAL")
        assert JinjaReportConfig.get_page_size() == "LEGAL"

    def test_env_override_templates_dir(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setenv("JINJAREPORT_TEMPLATES_DIR", str(tmp_path))
        result = JinjaReportConfig.get_templates_dir()
        assert result == tmp_path


class TestConfigReset:
    """Verify reset returns all settings to defaults."""

    def test_reset_clears_programmatic(self) -> None:
        JinjaReportConfig.set_locale("en_US")
        JinjaReportConfig.set_default_format("corporate")
        JinjaReportConfig.reset()
        assert JinjaReportConfig.get_locale() == "es_ES"
        assert JinjaReportConfig.get_default_format() == "default"

    def test_get_all_config_returns_dict(self) -> None:
        config = JinjaReportConfig.get_all_config()
        assert isinstance(config, dict)
        assert "templates_dir" in config
        assert "locale" in config


class TestConfigCwdDiscovery:
    """Verify config discovery checks CWD for jinjareportpy.toml."""

    def test_cwd_toml_loaded_when_present(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Config file in CWD should be picked up automatically."""
        config_file = tmp_path / "jinjareportpy.toml"
        config_file.write_text(
            '[report]\nlocale = "fr_FR"\n', encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        JinjaReportConfig.reset()
        assert JinjaReportConfig.get_locale() == "fr_FR"

    def test_env_var_takes_priority_over_cwd(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """JINJAREPORT_CONFIG_FILE env var must beat CWD config."""
        # CWD config
        cwd_config = tmp_path / "cwd" / "jinjareportpy.toml"
        cwd_config.parent.mkdir()
        cwd_config.write_text(
            '[report]\nlocale = "fr_FR"\n', encoding="utf-8",
        )
        monkeypatch.chdir(cwd_config.parent)

        # Env var config
        env_config = tmp_path / "env_config.toml"
        env_config.write_text(
            '[report]\nlocale = "de_DE"\n', encoding="utf-8",
        )
        monkeypatch.setenv("JINJAREPORT_CONFIG_FILE", str(env_config))
        JinjaReportConfig.reset()
        assert JinjaReportConfig.get_locale() == "de_DE"
