from pathlib import Path

import pytest

from aula_f99 import keybindings, usage_codes


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    path = tmp_path / "f99_keybindings.toml"
    keybindings.save_keybindings(
        [
            keybindings.Shortcut(
                category="Consumer Control code",
                shortcut="",
                effect="Volume Increment",
                detectable=True,
                code=0x00E9,
                short="Vol+",
            ),
            keybindings.Shortcut(
                category="Consumer Control code",
                shortcut="",
                effect="Volume Decrement",
                detectable=True,
                code=0x00EA,
                short="Vol-",
            ),
        ],
        path=path,
    )
    return path


def test_is_release_report():
    assert usage_codes.is_release_report(b"")
    assert usage_codes.is_release_report(bytes([0, 0, 0]))
    assert not usage_codes.is_release_report(bytes([0xE9, 0x00]))


def test_extract_code_prefers_known_offset():
    known = {0x00EA}
    # code at offset 1 (as if byte 0 were a report ID) matches a known code
    raw = bytes([0x01, 0xEA, 0x00])
    assert usage_codes.extract_code(raw, known) == 0x00EA


def test_extract_code_falls_back_to_first_offset_when_none_known():
    raw = bytes([0xE9, 0x00])
    assert usage_codes.extract_code(raw, known_codes=set()) == 0x00E9


def test_format_event_release_report_is_none(config_path: Path):
    assert usage_codes.format_event(bytes([0, 0, 0]), path=config_path) is None


def test_format_event_known_code(config_path: Path):
    text = usage_codes.format_event(bytes([0xE9, 0x00]), path=config_path)
    assert text == "Vol+ (Raw: 0x00E9)"


def test_format_event_unknown_code_records_stub(config_path: Path):
    text = usage_codes.format_event(bytes([0x34, 0x12]), path=config_path)
    assert text == "0x1234 (Raw: 0x1234)"

    reloaded = keybindings.lookup_by_code(0x1234, path=config_path)
    assert reloaded is not None
    assert reloaded.effect == "Unknown"
