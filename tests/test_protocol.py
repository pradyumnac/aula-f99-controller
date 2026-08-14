import pytest

from aula_f99 import protocol


def test_validate_rgb_accepts_the_full_range():
    protocol.validate_rgb(0, 128, 255)  # must not raise


@pytest.mark.parametrize(
    ("r", "g", "b"),
    [(999, 0, 0), (0, -1, 0), (0, 0, 256), (-1, -1, -1)],
)
def test_validate_rgb_rejects_out_of_range_channels(r, g, b):
    with pytest.raises(ValueError):
        protocol.validate_rgb(r, g, b)


def test_build_solid_color_packet_rejects_out_of_range_input():
    # Previously this silently wrapped: 999 & 0xFF == 231, -1 & 0xFF == 255.
    with pytest.raises(ValueError):
        protocol.build_solid_color_packet(999, -1, 0)


def test_solid_color_packet_layout():
    packet = protocol.build_solid_color_packet(0xFF, 0x00, 0x00)
    assert len(packet) == protocol.PACKET_LEN
    assert packet[0:5] == bytes([0x13, 0x88, 0x01, 0x00, 0x23])
    assert packet[5:8] == bytes([0xFF, 0x00, 0x00])


def test_solid_color_checksum():
    packet = protocol.build_solid_color_packet(0xFF, 0x00, 0x00)
    assert packet[19] == sum(packet[:19]) & 0xFF


def test_model_query_packet_checksum():
    packet = protocol.build_model_query_packet()
    assert packet[0:2] == bytes([0x13, 0x05])
    assert packet[19] == sum(packet[:19]) & 0xFF
