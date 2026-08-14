from aula_f99 import config
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
