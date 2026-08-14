import contextlib

from aula_f99 import config


def test_atomic_write_toml_round_trip(tmp_path):
    path = tmp_path / "nested" / "file.toml"  # parent doesn't exist yet
    config.atomic_write_toml(path, {"a": 1, "b": "two"})
    assert path.read_text() == 'a = 1\nb = "two"\n'


def test_atomic_write_toml_leaves_no_temp_file_on_success(tmp_path):
    path = tmp_path / "file.toml"
    config.atomic_write_toml(path, {"a": 1})
    assert list(tmp_path.iterdir()) == [path]


def test_atomic_write_toml_does_not_truncate_on_failure(tmp_path, monkeypatch):
    path = tmp_path / "file.toml"
    config.atomic_write_toml(path, {"a": 1})
    before = path.read_bytes()

    def boom(*args, **kwargs):
        raise RuntimeError("simulated crash mid-write")

    monkeypatch.setattr("aula_f99.config.tomli_w.dump", boom)
    with contextlib.suppress(RuntimeError):
        config.atomic_write_toml(path, {"a": 2})

    assert path.read_bytes() == before
    assert list(tmp_path.iterdir()) == [path]  # no stray .tmp file left behind
