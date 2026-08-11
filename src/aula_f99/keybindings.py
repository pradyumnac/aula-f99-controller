"""F99 FN shortcut reference and Consumer Control usage-code lookup.
Backed by config/f99_keybindings.toml.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import tomli_w

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "f99_keybindings.toml"


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
    with path.open("rb") as f:
        raw = tomllib.load(f)
    return [_from_raw(entry) for entry in raw.get("shortcut", [])]


def save_keybindings(entries: list[Shortcut], path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = {"shortcut": [_to_raw(e) for e in entries]}
    with path.open("wb") as f:
        tomli_w.dump(raw, f)


def lookup_by_code(code: int, path: Path = CONFIG_PATH) -> Shortcut | None:
    for entry in load_keybindings(path):
        if entry.code == code:
            return entry
    return None


def record_unknown_code(code: int, path: Path = CONFIG_PATH) -> Shortcut:
    """Looks up code; appends an "Unknown" stub if unseen."""
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
