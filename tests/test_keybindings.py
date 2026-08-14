import threading
from pathlib import Path

import pytest

from aula_f99 import keybindings
from aula_f99.errors import ConfigLoadError


def test_load_keybindings_reads_the_real_config_file():
    # Exercises the actual config/f99_keybindings.toml shipped with the repo.
    entries = keybindings.load_keybindings()
    assert entries
    for entry in entries:
        assert entry.category
        assert entry.effect
        assert isinstance(entry.detectable, bool)


def test_detectable_reference_rows_have_a_backing_code():
    entries = keybindings.load_keybindings()
    code_shortcuts = [e.shortcut for e in entries if e.category == "Consumer Control code"]
    for entry in entries:
        if entry.category == "Consumer Control code" or not entry.detectable:
            continue
        key = entry.shortcut.removeprefix("FN + ")
        assert any(key in s for s in code_shortcuts), (
            f"{entry.category}/{entry.shortcut} marked detectable but no Consumer "
            "Control code row references it"
        )


def test_load_keybindings_missing_file_returns_empty(tmp_path: Path):
    assert keybindings.load_keybindings(tmp_path / "does_not_exist.toml") == []


def test_load_keybindings_invalid_toml_raises_config_load_error(tmp_path: Path):
    path = tmp_path / "f99_keybindings.toml"
    path.write_text("this is not valid toml [[[")
    with pytest.raises(ConfigLoadError) as excinfo:
        keybindings.load_keybindings(path)
    assert excinfo.value.path == path


def test_load_keybindings_missing_key_raises_config_load_error(tmp_path: Path):
    path = tmp_path / "f99_keybindings.toml"
    path.write_text('[[shortcut]]\nshortcut = "FN + Q"\n')  # missing required "category"/"effect"
    with pytest.raises(ConfigLoadError):
        keybindings.load_keybindings(path)


def test_save_and_load_roundtrip(tmp_path: Path):
    path = tmp_path / "f99_keybindings.toml"
    original = [
        keybindings.Shortcut(
            category="Connection",
            shortcut="FN + `",
            effect="Select 2.4G wireless mode",
            detectable=False,
        ),
        keybindings.Shortcut(
            category="Consumer Control code",
            shortcut="",
            effect="Volume Increment",
            detectable=True,
            code=0x00E9,
            short="Vol+",
        ),
    ]
    keybindings.save_keybindings(original, path=path)
    reloaded = keybindings.load_keybindings(path)
    assert reloaded == original


def test_lookup_by_code_finds_match(tmp_path: Path):
    path = tmp_path / "f99_keybindings.toml"
    keybindings.save_keybindings(
        [
            keybindings.Shortcut(
                category="Consumer Control code",
                shortcut="",
                effect="Mute",
                detectable=True,
                code=0x00E2,
                short="Mute",
            )
        ],
        path=path,
    )
    entry = keybindings.lookup_by_code(0x00E2, path=path)
    assert entry is not None
    assert entry.effect == "Mute"


def test_lookup_by_code_no_match_returns_none(tmp_path: Path):
    path = tmp_path / "f99_keybindings.toml"
    keybindings.save_keybindings([], path=path)
    assert keybindings.lookup_by_code(0x1234, path=path) is None


def test_record_unknown_code_appends_stub(tmp_path: Path):
    path = tmp_path / "f99_keybindings.toml"
    keybindings.save_keybindings([], path=path)

    entry = keybindings.record_unknown_code(0x1234, path=path)
    assert entry.effect == "Unknown"
    assert entry.code == 0x1234

    reloaded = keybindings.load_keybindings(path)
    assert len(reloaded) == 1
    assert reloaded[0].code == 0x1234


def test_record_unknown_code_survives_concurrent_listener_threads(tmp_path: Path):
    # The key monitor runs one listener thread per link (wired, wireless).
    # An unrecognised code on either one calls record_unknown_code(), a
    # read-modify-write of the same file -- without the lock, two threads
    # racing this drop each other's update (last write wins on a stale read).
    path = tmp_path / "f99_keybindings.toml"
    keybindings.save_keybindings([], path=path)

    def hammer(base: int) -> None:
        for i in range(60):
            keybindings.record_unknown_code(base + i, path=path)

    threads = [
        threading.Thread(target=hammer, args=(0x1000,)),
        threading.Thread(target=hammer, args=(0x2000,)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    codes = {e.code for e in keybindings.load_keybindings(path)}
    assert len(codes) == 120


def test_save_keybindings_is_atomic_on_write_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    path = tmp_path / "f99_keybindings.toml"
    original = [keybindings.Shortcut(category="Connection", shortcut="FN + `", effect="x", detectable=False)]
    keybindings.save_keybindings(original, path=path)
    before = path.read_bytes()

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("simulated crash mid-write")

    monkeypatch.setattr("aula_f99.config.tomli_w.dump", boom)
    with pytest.raises(RuntimeError):
        keybindings.save_keybindings([], path=path)

    assert path.read_bytes() == before  # untouched, not truncated
    assert list(path.parent.glob(".*.tmp")) == []  # no stray temp file left behind


def test_record_unknown_code_does_not_duplicate(tmp_path: Path):
    path = tmp_path / "f99_keybindings.toml"
    keybindings.save_keybindings(
        [
            keybindings.Shortcut(
                category="Consumer Control code",
                shortcut="",
                effect="Mute",
                detectable=True,
                code=0x00E2,
                short="Mute",
            )
        ],
        path=path,
    )
    before = path.read_text()
    entry = keybindings.record_unknown_code(0x00E2, path=path)
    assert entry.effect == "Mute"
    assert path.read_text() == before
