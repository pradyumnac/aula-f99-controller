"""Read-only detection of how the AULA F99 is currently connected.

Uses hid.enumerate() only -- never opens or writes to the device.
"""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Callable
from dataclasses import dataclass, field

import hid

from aula_f99 import protocol

# NOTE: usage page 0x0001 (Generic Desktop -- Keyboard usage 0x0006, System
# Control usage 0x0080) is blocked for raw HID reads by Windows itself, as an
# anti-keylogger measure -- open() succeeds but read() always errors, on any
# keyboard, not just this one. Consumer Control (page 0x000C: media/volume
# keys) is NOT restricted, so that's what we listen on instead.
CONSUMER_USAGE_PAGE = 0x000C
CONSUMER_USAGE = 0x0001


@dataclass
class ConnectionStatus:
    wired_present: bool
    wireless_dongle_present: bool
    wired_product: str | None = None
    wireless_product: str | None = None
    wired_interfaces: list[hid.DeviceInfo] = field(default_factory=list)
    wireless_interfaces: list[hid.DeviceInfo] = field(default_factory=list)

    @property
    def guessed_mode(self) -> str:
        # NOTE: this is only a guess from enumeration -- both a wired cable
        # and a wireless dongle can be plugged in at once (they're separate
        # physical connections), and the dongle stays enumerated even if the
        # keyboard's radio is off. Use probe_active_link() for a real answer.
        if self.wired_present:
            return "wired (guess)"
        if self.wireless_dongle_present:
            return "wireless (guess -- dongle present; keyboard pairing unconfirmed)"
        return "not connected"


def detect_connection() -> ConnectionStatus:
    wired = hid.enumerate(protocol.VID_WIRED, protocol.PID_WIRED)
    wireless = hid.enumerate(protocol.VID_WIRELESS, protocol.PID_WIRELESS)

    return ConnectionStatus(
        wired_present=bool(wired),
        wireless_dongle_present=bool(wireless),
        wired_product=wired[0]["product_string"] if wired else None,
        wireless_product=wireless[0]["product_string"] if wireless else None,
        wired_interfaces=wired,
        wireless_interfaces=wireless,
    )


def _find_consumer_path(vid: int, pid: int) -> bytes | None:
    """Path to the consumer-control collection (media/volume keys)."""
    for d in hid.enumerate(vid, pid):
        if d["usage_page"] == CONSUMER_USAGE_PAGE and d["usage"] == CONSUMER_USAGE:
            return d["path"]
    return None


def _listen_for_report(
    path: bytes, timeout_ms: int, result: dict[str, bool], key: str, found: threading.Event
) -> None:
    dev = hid.device()
    try:
        dev.open_path(path)
        data = dev.read(64, timeout_ms=timeout_ms)
        if data:
            result[key] = True
            found.set()
    except OSError:
        pass
    finally:
        with contextlib.suppress(OSError):
            dev.close()


def probe_active_link(timeout_s: float = 5.0) -> str:
    """Passively listen on both wired and wireless consumer-control (media
    key) collections and report whichever one delivers an input report first.

    Returns as soon as either side reports data -- does not wait out the
    full timeout unless nothing is pressed at all.

    Read-only: opens the Consumer Control HID collection and reads reports
    the device already sends when a media/volume key is pressed. No
    output/feature report is ever written. (We listen on the consumer page
    rather than the keyboard page because Windows blocks raw reads of the
    standard keyboard usage page for any device, as an anti-keylogger
    measure -- open() succeeds but read() always errors there.)

    Caller should prompt the user to press a media/volume key (or turn the
    volume knob, if the keyboard has one) while this runs.
    """
    wired_path = _find_consumer_path(protocol.VID_WIRED, protocol.PID_WIRED)
    wireless_path = _find_consumer_path(protocol.VID_WIRELESS, protocol.PID_WIRELESS)

    result: dict[str, bool] = {}
    found = threading.Event()
    timeout_ms = int(timeout_s * 1000)
    threads = []
    if wired_path:
        t = threading.Thread(
            target=_listen_for_report, args=(wired_path, timeout_ms, result, "wired", found), daemon=True
        )
        t.start()
        threads.append(t)
    if wireless_path:
        t = threading.Thread(
            target=_listen_for_report,
            args=(wireless_path, timeout_ms, result, "wireless", found),
            daemon=True,
        )
        t.start()
        threads.append(t)

    if not threads:
        return "no keyboard/dongle found to listen on"

    # Unblocks as soon as one side reports data, instead of always waiting
    # out the full timeout. The other (unmatched) thread keeps blocking on
    # its own read() up to timeout_ms in the background -- harmless, since
    # it's a daemon thread and we no longer care about its result.
    detected = found.wait(timeout_s)
    if not detected:
        return "no keypress detected -- run again and press a key promptly"

    if result.get("wired"):
        return "wired"
    if result.get("wireless"):
        return "wireless"
    return "no keypress detected -- run again and press a key promptly"


def stream_consumer_events(
    stop_event: threading.Event,
    on_event: Callable[[str, bytes], None],
    poll_timeout_s: float = 0.2,
    on_ready: Callable[[list[str]], None] | None = None,
) -> None:
    """Continuously listen on both wired/wireless consumer-control
    collections, calling on_event(link, raw_bytes) for every report received,
    until stop_event is set. Blocks the calling thread until then.

    Read-only: same Consumer Control collection as probe_active_link(), just
    read in a loop instead of once.

    `on_ready`, if given, is called once with the links actually being
    listened on (e.g. `["wired"]`, or `[]` if neither is present) before
    the blocking wait -- the only way a caller can tell "found nothing to
    listen on" apart from "listening, but idle so far", since both look
    identical from the outside otherwise.
    """
    wired_path = _find_consumer_path(protocol.VID_WIRED, protocol.PID_WIRED)
    wireless_path = _find_consumer_path(protocol.VID_WIRELESS, protocol.PID_WIRELESS)
    poll_timeout_ms = int(poll_timeout_s * 1000)

    def _loop(path: bytes, link: str) -> None:
        dev = hid.device()
        try:
            dev.open_path(path)
        except OSError:
            return
        try:
            while not stop_event.is_set():
                try:
                    data = dev.read(64, timeout_ms=poll_timeout_ms)
                except OSError:
                    break
                if data:
                    on_event(link, bytes(data))
        finally:
            with contextlib.suppress(OSError):
                dev.close()

    threads = []
    links: list[str] = []
    if wired_path:
        threads.append(threading.Thread(target=_loop, args=(wired_path, "wired"), daemon=True))
        links.append("wired")
    if wireless_path:
        threads.append(threading.Thread(target=_loop, args=(wireless_path, "wireless"), daemon=True))
        links.append("wireless")

    if on_ready is not None:
        on_ready(links)

    for t in threads:
        t.start()
    for t in threads:
        t.join()
