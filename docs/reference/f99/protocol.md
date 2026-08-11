# AULA F99 USB protocol

This page records what is known about the keyboard's USB interface: how to
address it, and which commands are confirmed.

## Device identifiers

Each connection mode presents a different USB device.

| Mode | VID | PID | Usage page | Usage |
| --- | --- | --- | --- | --- |
| Wireless (2.4G dongle) | `0x3554` | `0xfa09` | `0xff02` | `0x0002` |
| Wired (USB cable) | `0x258a` | `0x010c` | `0xff00` | `0x0001` |

A cable and a dongle can be plugged in at the same time. Each is a
separate physical connection. The dongle stays enumerated even when the
keyboard's radio is off, so enumeration alone cannot tell you which link
the keyboard uses. The keyboard's own mode switch decides that. See
[hardware.md](hardware.md).

Bluetooth mode presents no USB device. This project cannot reach the
keyboard over Bluetooth.

## Protocol origin

The protocol is the Sinowealth wireless keyboard protocol. The OpenRGB
project documented it first.

- [OpenRGB issue #5166](https://gitlab.com/CalcProgrammer1/OpenRGB/-/issues/5166)
- [OpenRGB MR !3026](https://gitlab.com/CalcProgrammer1/OpenRGB/-/merge_requests/3026)
- [OpenRGB MR !3027](https://gitlab.com/CalcProgrammer1/OpenRGB/-/merge_requests/3027)

## Vendor control channel

Control commands go through the vendor-defined HID collection listed
above. Each report is 20 bytes.

| Byte | Meaning |
| --- | --- |
| 0 | Fixed header byte: `0x13` |
| 1 | Command ID |
| 2-18 | Command payload |
| 19 | Checksum: sum of bytes 0-18, masked to 8 bits |

### Confirmed commands

| Command | Byte 1 | Payload | Status |
| --- | --- | --- | --- |
| Model query | `0x05` | none | Implemented |
| LED control (solid colour) | `0x88` | byte 2 = `0x01`, byte 3 = `0x00`, byte 4 = `0x23`, bytes 5-7 = R, G, B | Implemented |

Model IDs arrive at response byte 10: `0xA4` = F99, `0xCD` = F75.

### Not captured yet

The OEM software offers many more features. None of their commands are
captured. See [gui-features.md](gui-features.md) for the full list. The
largest gaps are:

- Per-key RGB
- The 15 lighting effects, and their speed and brightness values
- The RGB ambient light bar
- Key remapping across the 4 layers
- Macros

The wired vendor channel (`0xff00`) also rejects writes today. The `hid`
write call returns `-1`. Three collections share the same usage page and
usage, so the correct one is not identified. The wired report format may
also differ from the wireless one. This needs its own capture.

### Capturing new commands

Use this method to identify a command that is not in this page yet.

1. Install Wireshark and USBPcap. The Wireshark Windows installer bundles
   USBPcap.
2. Start a capture on the USBPcap interface for the keyboard's USB bus.
3. Perform one action in the OEM software. Stop the capture right after.
4. Filter on `usb.dst == "host"` or the device address. Look for
   `URB_INTERRUPT out` or `URB_CONTROL` transfers with a 20-byte payload
   that starts with `0x13`.
5. Repeat for a similar action, for example red against blue. Compare the
   two captures. The bytes that differ carry the setting you changed.

The OEM software may print colours in `BBGGRR` byte order. See
[gui-features.md](gui-features.md#hex-field-byte-order). Keep this in mind
when you match a captured payload to a colour.

## Windows HID read restriction

Windows blocks raw HID reads from the standard keyboard usage page (usage
page `0x0001`, usage `0x0006`). This applies to every keyboard, not just
this one. It is a built-in anti-keylogger measure. `open()` on that
collection succeeds. `read()` on it always fails with `OSError`.

The Consumer Control usage page (`0x000C`) has no such restriction. This
project listens there instead.

## Consumer Control reports

The Consumer Control collection carries the media keys and the volume
keys. Reading it is the only way this project can observe key activity on
Windows.

| Property | Value |
| --- | --- |
| Usage page | `0x000C` |
| Usage | `0x0001` |
| Report length read | 64 bytes |

A report with all-zero bytes is a key-release event. It carries no usage
code.

The report layout is not confirmed. It is not known whether a report-ID
byte comes first. Code that reads these reports tries both byte offsets
and prefers the offset that matches an already-known usage code.

Because both links can be read at once, a report proves which link is
live. This is the only reliable active-link test this project has.
