"""Parses raw Consumer-page (0x0C) HID reports; lookup lives in aula_f99.keybindings."""

from __future__ import annotations

from pathlib import Path

from aula_f99 import keybindings

CONFIG_PATH = keybindings.CONFIG_PATH


def is_release_report(raw: bytes) -> bool:
    """Consumer-control array reports go all-zero on key release."""
    return not raw or all(b == 0 for b in raw)


def extract_code(raw: bytes, known_codes: set[int]) -> int | None:
    """Report-ID prefix presence is unconfirmed; tries both byte offsets."""
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
    """E.g. "Vol- (Raw: 0x00EA)". None for release/no-op reports."""
    if is_release_report(raw):
        return None
    known_codes = {e.code for e in keybindings.load_keybindings(path) if e.code is not None}
    code = extract_code(raw, known_codes)
    if code is None:
        return None
    entry = keybindings.lookup_by_code(code, path) or keybindings.record_unknown_code(code, path)
    label = entry.short or entry.effect
    return f"{label} (Raw: 0x{code:04X})"
