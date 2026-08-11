from aula_f99 import protocol


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
