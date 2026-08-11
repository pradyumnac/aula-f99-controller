import threading

from aula_f99.detect import ConnectionStatus, detect_connection, stream_consumer_events


def test_detect_connection_returns_status():
    # Read-only: exercises real hid.enumerate() but never opens/writes a device.
    status = detect_connection()
    assert isinstance(status, ConnectionStatus)
    assert status.guessed_mode in {
        "wired (guess)",
        "wireless (guess -- dongle present; keyboard pairing unconfirmed)",
        "not connected",
    }


def test_guessed_mode_prefers_wired():
    status = ConnectionStatus(wired_present=True, wireless_dongle_present=True)
    assert status.guessed_mode == "wired (guess)"


def test_guessed_mode_wireless_only():
    status = ConnectionStatus(wired_present=False, wireless_dongle_present=True)
    assert "wireless" in status.guessed_mode


def test_guessed_mode_none():
    status = ConnectionStatus(wired_present=False, wireless_dongle_present=False)
    assert status.guessed_mode == "not connected"


def test_probe_active_link_no_device_returns_prompt():
    # With no real device args this should short-circuit fast, not hang.
    from aula_f99.detect import probe_active_link

    result = probe_active_link(timeout_s=0.1)
    assert isinstance(result, str)


def test_stream_consumer_events_returns_when_stopped_immediately():
    # With no real device present, both _loop threads exit immediately
    # (open fails), so join() returns right away regardless of stop_event.
    stop_event = threading.Event()
    events: list[tuple[str, bytes]] = []
    stop_event.set()
    stream_consumer_events(stop_event, lambda link, raw: events.append((link, raw)))
    assert events == []
