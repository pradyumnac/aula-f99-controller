"""Where this project's files live. XDG layout on every platform."""

from __future__ import annotations

import os
from pathlib import Path

APP_DIR_NAME = "aula-f99"


def config_home() -> Path:
    """`XDG_CONFIG_HOME`, or `~/.config` when it is unset."""
    override = os.environ.get("XDG_CONFIG_HOME")
    return Path(override) if override else Path.home() / ".config"


def config_dir() -> Path:
    return config_home() / APP_DIR_NAME


def tui_keymap_path() -> Path:
    return config_dir() / "tui_keymap.toml"
