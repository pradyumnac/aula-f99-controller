"""Read/write mapping of Consumer-page (0x0C) HID usage codes to names.

Backed by config/consumer_usage.toml at the repo root -- a human-editable,
growable table rather than a hardcoded dict. Unknown codes encountered at
runtime get auto-appended as "Unknown" stubs so they show up for later
identification instead of silently vanishing.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "consumer_usage.toml"


def _code_key(code: int) -> str:
    return f"0x{code:04X}"


def load_usage_map(path: Path = CONFIG_PATH) -> dict[int, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        raw = tomllib.load(f)
    result: dict[int, dict[str, str]] = {}
    for key, entry in raw.items():
        try:
            code = int(key, 16)
        except ValueError:
            continue
        result[code] = {"name": entry.get("name", "Unknown"), "short": entry.get("short", key)}
    return result


def save_usage_map(mapping: dict[int, dict[str, str]], path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = {_code_key(code): entry for code, entry in sorted(mapping.items())}
    with path.open("wb") as f:
        tomli_w.dump(raw, f)


def get_or_record(code: int, path: Path = CONFIG_PATH) -> dict[str, str]:
    """Look up a usage code; if unseen, append an "Unknown" stub to the
    config file (write-through) so it's there to identify/edit later.
    """
    mapping = load_usage_map(path)
    entry = mapping.get(code)
    if entry is not None:
        return entry

    stub = {"name": "Unknown", "short": _code_key(code)}
    mapping[code] = stub
    save_usage_map(mapping, path)
    return stub


def is_release_report(raw: bytes) -> bool:
    """Consumer-control array reports go all-zero on key release."""
    return not raw or all(b == 0 for b in raw)


def extract_code(raw: bytes, known_codes: set[int]) -> int | None:
    """Pull the 2-byte usage code out of a report.

    The report layout (report-ID prefix or not) isn't confirmed for this
    device, so this tries both plausible byte offsets and prefers whichever
    one matches an already-known code.
    """
    candidates: list[int] = []
    if len(raw) >= 2:
        candidates.append(int.from_bytes(raw[0:2], "little"))
    if len(raw) >= 3:
        candidates.append(int.from_bytes(raw[1:3], "little"))
    if not candidates:
        return None
    for code in candidates:
        if code in known_codes:
            return code
    return candidates[0]


def format_event(raw: bytes, path: Path = CONFIG_PATH) -> str | None:
    """Display string for a consumer-control report, e.g. "Vol- (Raw: 0x00EA)".

    Returns None for release/no-op (all-zero) reports, which shouldn't be
    shown as separate events from the keypress that preceded them.
    """
    if is_release_report(raw):
        return None
    mapping = load_usage_map(path)
    code = extract_code(raw, set(mapping.keys()))
    if code is None:
        return None
    entry = mapping.get(code) or get_or_record(code, path)
    return f"{entry['short']} (Raw: 0x{code:04X})"
