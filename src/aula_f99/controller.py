from __future__ import annotations

import contextlib

import hid

from aula_f99 import protocol


class AulaF99:
    """HID handle to an AULA F99 keyboard (wireless dongle or wired)."""

    def __init__(self, wired: bool = False):
        self._wired = wired
        self._dev = hid.device()
        vid, pid = (
            (protocol.VID_WIRED, protocol.PID_WIRED)
            if wired
            else (
                protocol.VID_WIRELESS,
                protocol.PID_WIRELESS,
            )
        )
        usage_page = protocol.USAGE_PAGE_WIRED if wired else protocol.USAGE_PAGE_WIRELESS
        usage = protocol.USAGE_WIRED if wired else protocol.USAGE_WIRELESS

        path = self._find_path(vid, pid, usage_page, usage)
        if path is None:
            raise RuntimeError(
                f"No HID interface found for VID=0x{vid:04x} PID=0x{pid:04x} "
                f"usage_page=0x{usage_page:04x} usage=0x{usage:04x}. "
                "Is the keyboard connected in the expected mode?"
            )
        self._dev.open_path(path)

    @staticmethod
    def _find_path(vid: int, pid: int, usage_page: int, usage: int) -> bytes | None:
        for info in hid.enumerate(vid, pid):
            if info["usage_page"] == usage_page and info["usage"] == usage:
                return info["path"]
        return None

    def set_solid_color(self, r: int, g: int, b: int) -> None:
        packet = protocol.build_solid_color_packet(r, g, b)
        self._dev.write(bytes(packet))

    def query_model(self) -> int | None:
        packet = protocol.build_model_query_packet()
        self._dev.write(bytes(packet))
        response = self._dev.read(protocol.PACKET_LEN, timeout_ms=1000)
        if not response or len(response) < 11:
            return None
        return response[10]

    def close(self) -> None:
        # A close failure is never actionable -- the device is going away
        # either way -- and letting it raise here would mask a command that
        # already completed (its result already printed/returned) behind a
        # misleading "Error: ..." from teardown, not the command itself.
        with contextlib.suppress(OSError):
            self._dev.close()

    def __enter__(self) -> AulaF99:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
