from pathlib import Path

from aula_f99 import keybindings


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
