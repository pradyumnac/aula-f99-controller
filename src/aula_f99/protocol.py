"""Sinowealth wireless keyboard HID protocol, as used by the AULA F99.

Protocol details documented by the OpenRGB project (GitLab issue #5166,
MRs !3026/!3027): https://gitlab.com/CalcProgrammer1/OpenRGB/-/issues/5166
"""

from __future__ import annotations

PACKET_LEN = 20

# Wireless-mode identifiers (2.4G dongle)
VID_WIRELESS = 0x3554
PID_WIRELESS = 0xFA09
USAGE_PAGE_WIRELESS = 0xFF02
USAGE_WIRELESS = 0x0002

# Wired-mode identifiers (USB cable)
VID_WIRED = 0x258A
PID_WIRED = 0x010C
USAGE_PAGE_WIRED = 0xFF00
USAGE_WIRED = 0x0001

CMD_MODEL_QUERY = 0x05
CMD_LED_CONTROL = 0x88

MODEL_IDS = {
    0xA4: "F99",
    0xCD: "F75",
}


def crc(packet: bytearray) -> int:
    """Checksum is the sum of all preceding bytes, masked to 8 bits."""
    return sum(packet[: PACKET_LEN - 1]) & 0xFF


def validate_rgb(r: int, g: int, b: int) -> None:
    for name, value in (("r", r), ("g", g), ("b", b)):
        if not 0 <= value <= 255:
            raise ValueError(f"{name}={value} is out of range -- each colour channel must be 0-255")


def build_solid_color_packet(r: int, g: int, b: int) -> bytearray:
    validate_rgb(r, g, b)
    packet = bytearray(PACKET_LEN)
    packet[0] = 0x13
    packet[1] = CMD_LED_CONTROL
    packet[2] = 0x01
    packet[3] = 0x00
    packet[4] = 0x23
    packet[5] = r & 0xFF
    packet[6] = g & 0xFF
    packet[7] = b & 0xFF
    packet[19] = crc(packet)
    return packet


def build_model_query_packet() -> bytearray:
    packet = bytearray(PACKET_LEN)
    packet[0] = 0x13
    packet[1] = CMD_MODEL_QUERY
    packet[2] = 0x01
    packet[3] = 0x00
    packet[19] = crc(packet)
    return packet
