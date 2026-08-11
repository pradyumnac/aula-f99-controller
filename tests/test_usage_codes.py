from pathlib import Path

import pytest

from aula_f99 import usage_codes


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    path = tmp_path / "consumer_usage.toml"
    usage_codes.save_usage_map(
        {
            0x00E9: {"name": "Volume Increment", "short": "Vol+"},
            0x00EA: {"name": "Volume Decrement", "short": "Vol-"},
        },
        path=path,
    )
    return path


def test_load_usage_map_roundtrip(config_path: Path):
    mapping = usage_codes.load_usage_map(config_path)
    assert mapping[0x00E9] == {"name": "Volume Increment", "short": "Vol+"}
    assert mapping[0x00EA] == {"name": "Volume Decrement", "short": "Vol-"}


def test_load_usage_map_missing_file_returns_empty(tmp_path: Path):
    assert usage_codes.load_usage_map(tmp_path / "does_not_exist.toml") == {}


def test_get_or_record_known_code_does_not_rewrite(config_path: Path):
    before = config_path.read_text()
    entry = usage_codes.get_or_record(0x00E9, path=config_path)
    assert entry == {"name": "Volume Increment", "short": "Vol+"}
    assert config_path.read_text() == before


def test_get_or_record_unknown_code_appends_stub(config_path: Path):
    entry = usage_codes.get_or_record(0x1234, path=config_path)
    assert entry == {"name": "Unknown", "short": "0x1234"}

    reloaded = usage_codes.load_usage_map(config_path)
    assert reloaded[0x1234] == {"name": "Unknown", "short": "0x1234"}


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
