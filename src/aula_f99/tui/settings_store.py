"""Persisted app settings: theme, default link, confirm-before-write.

Distinct from tui_keymap.toml, which holds key-binding overrides. See
docs/tui-spec.md#settings.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from aula_f99.config import atomic_write_toml, settings_path
from aula_f99.errors import ConfigLoadError

LINK_MODES = ("wireless", "wired")


@dataclass(frozen=True)
class AppSettings:
    theme: str = "textual-dark"
    default_link: str = "wireless"
    confirm_writes: bool = True


def load_settings(path: Path | None = None) -> AppSettings:
    path = path or settings_path()
    if not path.exists():
        return AppSettings()
    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
        defaults = AppSettings()
        default_link = str(raw.get("default_link", defaults.default_link))
        if default_link not in LINK_MODES:
            default_link = defaults.default_link
        return AppSettings(
            theme=str(raw.get("theme", defaults.theme)),
            default_link=default_link,
            confirm_writes=bool(raw.get("confirm_writes", defaults.confirm_writes)),
        )
    except Exception as exc:
        raise ConfigLoadError(path, exc) from exc


def save_settings(settings: AppSettings, path: Path | None = None) -> None:
    path = path or settings_path()
    atomic_write_toml(
        path,
        {
            "theme": settings.theme,
            "default_link": settings.default_link,
            "confirm_writes": settings.confirm_writes,
        },
    )
