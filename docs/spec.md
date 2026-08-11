# Specification

This page is a reference. It lists facts about the AULA F99 protocol and the
code that talks to it. For an introduction, read the [README](../README.md).

## Device identifiers

The keyboard can connect two ways. Each way uses a different USB ID.

| Mode | VID | PID | Usage page | Usage |
|---|---|---|---|---|
| Wireless (2.4G dongle) | `0x3554` | `0xfa09` | `0xff02` | `0x0002` |
| Wired (USB cable) | `0x258a` | `0x010c` | `0xff00` | `0x0001` |

Both a cable and a dongle can be plugged in at the same time. Each is a
separate physical connection. The dongle stays enumerated even when the
keyboard's radio is off. Enumeration alone cannot tell you which link the
keyboard actually uses.

Source: [`src/aula_f99/protocol.py`](../src/aula_f99/protocol.py).

## Protocol origin

The protocol is the Sinowealth wireless keyboard protocol. The OpenRGB
project documented it first.

- [OpenRGB issue #5166](https://gitlab.com/CalcProgrammer1/OpenRGB/-/issues/5166)
- [OpenRGB MR !3026](https://gitlab.com/CalcProgrammer1/OpenRGB/-/merge_requests/3026)
- [OpenRGB MR !3027](https://gitlab.com/CalcProgrammer1/OpenRGB/-/merge_requests/3027)

## Vendor control channel

Control commands (LED color, model query) go through the vendor-defined HID
collection listed above. Each report is 20 bytes.

| Byte | Meaning |
|---|---|
| 0 | Fixed header byte: `0x13` |
| 1 | Command ID (see table below) |
| 2-18 | Command-specific payload |
| 19 | Checksum: sum of bytes 0-18, masked to 8 bits |

### Known commands

| Command | Byte 1 | Payload | Status |
|---|---|---|---|
| Model query | `0x05` | none | Implemented |
| LED control (solid color) | `0x88` | byte 2 = `0x01`, byte 3 = `0x00`, byte 4 = `0x23`, bytes 5-7 = R, G, B | Implemented |

Model IDs returned at response byte 10: `0xA4` = F99, `0xCD` = F75.

Source: [`src/aula_f99/protocol.py`](../src/aula_f99/protocol.py).

### Not yet implemented

These features are not documented yet:

- Per-key RGB
- Lighting effects (breathing, wave, etc.)
- Brightness and speed control
- Macro programming

The wired-mode vendor channel (`0xff00`) also rejects writes today (`hid`
write returns `-1`). Its report format may differ from the wireless one.
This needs its own capture and analysis.

### Capturing traffic for new commands

Use this method to identify a command that is not in this spec yet.

1. Install Wireshark and USBPcap (the Wireshark Windows installer bundles
   USBPcap).
2. Start a capture on the USBPcap interface for the keyboard's USB bus.
3. Perform one action in the AULA OEM software. Stop the capture right
   after.
4. Filter on `usb.dst == "host"` or the device address. Look for
   `URB_INTERRUPT out` or `URB_CONTROL` transfers with a 20-byte payload
   that starts with `0x13`.
5. Repeat for a similar action (for example, red vs. blue). Compare the two
   captures. The bytes that differ carry the setting you changed.

## Windows HID read restriction

Windows blocks raw HID reads from the standard keyboard usage page (usage
page `0x0001`, usage `0x0006`). This applies to every keyboard, not just
this one. It is a built-in anti-keylogger measure. `open()` on that
collection succeeds. `read()` on it always fails with `OSError`.

The Consumer Control usage page (`0x000C`, media/volume keys) has no such
restriction. This project listens there instead, to detect key presses and
to tell wired mode from wireless mode.

Source: [`src/aula_f99/detect.py`](../src/aula_f99/detect.py).

## Consumer-control key detection

`aula_f99.detect` listens on the Consumer Control collection to answer two
questions:

- `probe_active_link()`: one-shot check. Prompts a media-key press, returns
  `"wired"` or `"wireless"` for whichever link delivered a report first.
- `stream_consumer_events()`: continuous check. Calls a callback for every
  report until told to stop. Used by the TUI's listener mode.

Reports with all-zero bytes are key-release events. They carry no
information and are filtered out (`usage_codes.is_release_report()`).

### Usage code lookup

`aula_f99.usage_codes` maps a 2-byte Consumer Control usage code to a
display name. The mapping lives in
[`config/consumer_usage.toml`](../config/consumer_usage.toml), not in code.
The file is human-editable.

- `load_usage_map()` reads the file.
- `save_usage_map()` writes it back.
- `get_or_record()` looks up a code. If the code is new, it appends an
  `"Unknown"` stub entry and saves the file, so the code shows up for later
  naming instead of vanishing.
- `format_event()` turns a raw report into a display string, for example
  `"Vol+ (Raw: 0x00E9)"`.

The report layout (whether a report-ID byte comes first) is not confirmed
for this device. `extract_code()` tries both byte offsets and prefers
whichever one matches an already-known code.

## Module reference

| Module | Responsibility |
|---|---|
| [`protocol.py`](../src/aula_f99/protocol.py) | Packet layouts, device IDs, checksum |
| [`controller.py`](../src/aula_f99/controller.py) | Opens the vendor HID device, sends write commands (`set_solid_color`, `query_model`) |
| [`detect.py`](../src/aula_f99/detect.py) | Read-only connection detection and key-press listening |
| [`usage_codes.py`](../src/aula_f99/usage_codes.py) | Consumer usage code to name mapping, backed by TOML |
| [`cli.py`](../src/aula_f99/cli.py) | Command-line entry point (`aula-f99`) |
| [`tui/app.py`](../src/aula_f99/tui/app.py) | Textual TUI: main screen and listener screen |

## CLI reference

Entry point: `aula-f99` (see [`pyproject.toml`](../pyproject.toml) scripts).

| Command | Effect | Writes to device? |
|---|---|---|
| `aula-f99 model` | Query and print the model name | Yes |
| `aula-f99 color R G B` | Set a solid RGB color | Yes |
| `aula-f99 tui` | Launch the interactive TUI | No (read-only until you use TUI features that write) |

Add `--wired` to any command to use the USB cable path instead of the
wireless dongle.

## mise tasks

Defined in [`mise.toml`](../mise.toml).

| Task | Effect |
|---|---|
| `mise run tui` | Launch the TUI |
| `mise run test` | Run the test suite |
| `mise run lint` | Lint with ruff |
| `mise run format` | Format with ruff |
| `mise run format:check` | Check formatting, make no changes |
| `mise run typecheck` | Static type-check with mypy (`--strict`, no `Any`) |
| `mise run check` | Run lint, format:check, typecheck, and test together |
| `mise run precommit:install` | Install the pre-commit git hook |
| `mise run precommit:run` | Run all pre-commit hooks against the whole repo |
| `mise run secrets:baseline` | Regenerate the detect-secrets baseline |

## Toolchain

- [mise](https://mise.jdx.dev/) pins the Python version and the `uv` version
  (`mise.toml`).
- [uv](https://docs.astral.sh/uv/) manages Python dependencies
  (`pyproject.toml`, `uv.lock`).
- [ruff](https://docs.astral.sh/ruff/) lints and formats the code.
- [mypy](https://mypy-lang.org/) type-checks the code in strict mode.
  Explicit `Any` is not allowed (`disallow_any_explicit = true`).
- A local stub package ([`stubs/hid/`](../stubs/hid/__init__.pyi)) gives
  mypy real types for the untyped `hid` package.
- [pre-commit](https://pre-commit.com/) runs ruff, mypy, secret scanning
  (gitleaks, detect-secrets), and file-hygiene checks before each commit.
