import pytest

from aula_f99 import config
from aula_f99.errors import ConfigLoadError
from aula_f99.tui.settings_store import AppSettings, load_settings, save_settings


def test_settings_path_follows_xdg(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert config.settings_path() == tmp_path / "aula-f99" / "settings.toml"


def test_load_settings_defaults_when_absent():
    assert load_settings() == AppSettings()


def test_settings_round_trip():
    save_settings(AppSettings(theme="nord", default_link="wired", confirm_writes=False))
    assert load_settings() == AppSettings(theme="nord", default_link="wired", confirm_writes=False)


def test_load_settings_rejects_an_unknown_link_mode(tmp_path):
    path = tmp_path / "settings.toml"
    path.write_text('theme = "nord"\ndefault_link = "bluetooth"\n')
    settings = load_settings(path)
    assert settings.default_link == AppSettings().default_link
    assert settings.theme == "nord"


def test_load_settings_invalid_toml_raises_config_load_error(tmp_path):
    path = tmp_path / "settings.toml"
    path.write_text("not valid toml [[[")
    with pytest.raises(ConfigLoadError) as excinfo:
        load_settings(path)
    assert excinfo.value.path == path


def test_save_settings_is_atomic_on_write_failure(tmp_path, monkeypatch):
    path = tmp_path / "settings.toml"
    save_settings(AppSettings(theme="nord"), path=path)
    before = path.read_bytes()

    def boom(*args, **kwargs):
        raise RuntimeError("simulated crash mid-write")

    monkeypatch.setattr("aula_f99.config.tomli_w.dump", boom)
    with pytest.raises(RuntimeError):
        save_settings(AppSettings(theme="gruvbox"), path=path)

    assert path.read_bytes() == before  # untouched, not truncated
    assert list(path.parent.glob(".*.tmp")) == []  # no stray temp file left behind
