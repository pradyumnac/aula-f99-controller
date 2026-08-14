"""F99 FN shortcut reference and Consumer Control usage-code lookup.
Backed by config/f99_keybindings.toml.
"""

from __future__ import annotations

import threading
import tomllib
from dataclasses import dataclass
from pathlib import Path

from aula_f99.config import atomic_write_toml
from aula_f99.errors import ConfigLoadError

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "f99_keybindings.toml"

# The key monitor runs one listener thread per link (wired, wireless), and
# an unrecognised code on either one triggers record_unknown_code()'s
# read-modify-write of this file. Without a lock, two presses landing at
# once silently drop one of the two updates (last write wins on a stale
# read). One lock is enough -- there is only ever one file in practice.
_write_lock = threading.Lock()


@dataclass(frozen=True)
class Shortcut:
    category: str
    shortcut: str
    effect: str
    detectable: bool
    code: int | None = None
    short: str | None = None


def _from_raw(entry: dict[str, object]) -> Shortcut:
    code_str = entry.get("code")
    return Shortcut(
        category=str(entry["category"]),
        shortcut=str(entry.get("shortcut", "")),
        effect=str(entry["effect"]),
        detectable=bool(entry["detectable"]),
        code=int(str(code_str), 16) if code_str else None,
        short=str(entry["short"]) if entry.get("short") else None,
    )


def _to_raw(entry: Shortcut) -> dict[str, str | bool]:
    raw: dict[str, str | bool] = {
        "category": entry.category,
        "shortcut": entry.shortcut,
        "effect": entry.effect,
        "detectable": entry.detectable,
    }
    if entry.code is not None:
        raw["code"] = f"0x{entry.code:04X}"
    if entry.short is not None:
        raw["short"] = entry.short
    return raw


def load_keybindings(path: Path = CONFIG_PATH) -> list[Shortcut]:
    if not path.exists():
        return []
    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
        return [_from_raw(entry) for entry in raw.get("shortcut", [])]
    except Exception as exc:
        # Anything from a bad TOML parse to a missing/mistyped key -- this
        # file is hand-editable, so any of it is plausible. The caller
        # decides the fallback and tells the user; we just name the cause.
        raise ConfigLoadError(path, exc) from exc


def save_keybindings(entries: list[Shortcut], path: Path = CONFIG_PATH) -> None:
    atomic_write_toml(path, {"shortcut": [_to_raw(e) for e in entries]})


def lookup_by_code(code: int, path: Path = CONFIG_PATH) -> Shortcut | None:
    for entry in load_keybindings(path):
        if entry.code == code:
            return entry
    return None


def record_unknown_code(code: int, path: Path = CONFIG_PATH) -> Shortcut:
    """Looks up code; appends an "Unknown" stub if unseen.

    Read-modify-write, so it needs the lock: two listener threads (wired,
    wireless) can both call this for a different unseen code at once.
    """
    with _write_lock:
        entries = load_keybindings(path)
        for entry in entries:
            if entry.code == code:
                return entry

        stub = Shortcut(
            category="Consumer Control code",
            shortcut="",
            effect="Unknown",
            detectable=True,
            code=code,
            short=f"0x{code:04X}",
        )
        entries.append(stub)
        save_keybindings(entries, path)
        return stub
