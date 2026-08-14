"""Where this project's files live. XDG layout on every platform."""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

import tomli_w

APP_DIR_NAME = "aula-f99"


def config_home() -> Path:
    """`XDG_CONFIG_HOME`, or `~/.config` when it is unset."""
    override = os.environ.get("XDG_CONFIG_HOME")
    return Path(override) if override else Path.home() / ".config"


def data_home() -> Path:
    """`XDG_DATA_HOME`, or `~/.local/share` when it is unset."""
    override = os.environ.get("XDG_DATA_HOME")
    return Path(override) if override else Path.home() / ".local" / "share"


def config_dir() -> Path:
    return config_home() / APP_DIR_NAME


def data_dir() -> Path:
    return data_home() / APP_DIR_NAME


def tui_keymap_path() -> Path:
    return config_dir() / "tui_keymap.toml"


def settings_path() -> Path:
    return config_dir() / "settings.toml"


def atomic_write_toml(path: Path, data: dict[str, object]) -> None:
    """Write `data` as TOML to `path`, atomically.

    Writes to a temp file in the same directory first, then renames it
    over the target. A crash or power loss mid-write leaves the previous
    file intact instead of a truncated, unparseable one -- `path.open("wb")`
    alone truncates to 0 bytes before a single byte of the new content is
    written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            tomli_w.dump(data, f)
        os.replace(tmp_name, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise
