from collections.abc import Sequence

import pytest

from aula_f99 import cli


class _Boom:
    """Stands in for AulaF99 when the device cannot be opened."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def __call__(self, wired: bool = False) -> None:
        raise self._exc


def _run(monkeypatch: pytest.MonkeyPatch, argv: Sequence[str], controller: _Boom) -> int:
    monkeypatch.setattr("sys.argv", ["aula-f99", *argv])
    monkeypatch.setattr(cli, "AulaF99", controller)
    return cli.main()


def test_missing_device_reports_the_reason_and_exits_nonzero(monkeypatch, capsys):
    boom = _Boom(RuntimeError("No HID interface found for VID=0x3554 PID=0xfa09"))
    assert _run(monkeypatch, ["model"], boom) == 1
    assert "No HID interface found" in capsys.readouterr().err


def test_device_io_error_reports_the_reason_and_exits_nonzero(monkeypatch, capsys):
    boom = _Boom(OSError("Access is denied."))
    assert _run(monkeypatch, ["color", "255", "0", "0"], boom) == 1
    assert "Access is denied." in capsys.readouterr().err


def test_unexpected_error_is_not_swallowed(monkeypatch):
    # Only device errors are turned into a message -- a genuine bug must
    # still surface as a traceback rather than a misleading "Error:" line.
    boom = _Boom(ValueError("a real bug"))
    with pytest.raises(ValueError):
        _run(monkeypatch, ["model"], boom)


def test_out_of_range_color_is_rejected_before_touching_the_device(monkeypatch, capsys):
    # A color command that will never reach the keyboard must never even
    # try to open it.
    never_called = _Boom(AssertionError("the device should not have been opened"))
    assert _run(monkeypatch, ["color", "999", "-1", "0"], never_called) == 1
    assert "out of range" in capsys.readouterr().err
