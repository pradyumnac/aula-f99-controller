"""Minimal local type stub for the `hidapi` package's `hid` module.

Only covers the surface this project actually uses. Extend as needed.
"""

from typing import TypedDict

class DeviceInfo(TypedDict):
    path: bytes
    vendor_id: int
    product_id: int
    serial_number: str
    release_number: int
    manufacturer_string: str
    product_string: str
    usage_page: int
    usage: int
    interface_number: int

def enumerate(vid: int = ..., pid: int = ...) -> list[DeviceInfo]: ...

class device:
    def open_path(self, path: bytes) -> None: ...
    def open(self, vendor_id: int = ..., product_id: int = ..., serial_number: str = ...) -> None: ...
    def write(self, data: bytes) -> int: ...
    def read(self, max_length: int, timeout_ms: int = ...) -> list[int]: ...
    def close(self) -> None: ...
    def set_nonblocking(self, value: int) -> int: ...
