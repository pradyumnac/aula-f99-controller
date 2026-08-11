# Feature tracking

This page tracks every known feature of the AULA F99: what the OEM
software offers, and what the hardware offers on its own. It is the
single list this project works from. [spec.md](spec.md) and
[tui-spec.md](tui-spec.md) both link here instead of repeating this list.

Feature facts come from [reference/f99/](reference/f99/README.md). This
page does not repeat those facts. It tracks status only.

## How to read this page

Each row is one feature. A feature keeps its row even before we discuss
it. An undiscussed feature still gets a home in the TUI layout, but its
panel shows a short "not implemented yet" note instead of controls. This
lets the sidebar and screen list stay stable as slices land.

### Status values

| Status | Meaning |
| --- | --- |
| Implemented | Code exists. Tested. Documented. |
| Planned | We agreed to build it. A slice is assigned in [tui-spec.md](tui-spec.md#vertical-slices). |
| Waiting for discussion | The default. No decision made yet. |
| Flagged -- uncertain | Hardware-only. We do not know yet whether this project can read or change it at all. |

### Other columns

| Column | Meaning |
| --- | --- |
| Writes to device? | Yes, No, or Unknown (the read/write need is not settled yet). |
| TUI location | The sidebar section or modal that owns this feature. See [tui-spec.md](tui-spec.md#sections). |
| CLI | The `aula-f99` switch, if one exists. Blank means none is agreed yet. See [Open decision](#open-decision-cli-for-undiscussed-features). |

### Open decision: CLI for undiscussed features

The CLI column stays blank until a feature is discussed and its design
agreed. We do not pre-name a switch for a feature whose protocol is not
even captured yet.

## Status

Connection state, device identity, and other read-only facts.

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Enumeration-based connection guess | Implemented | No | Status | -- | `detect_connection()`. Guess only, not proof. |
| Active-link proof, from a key press | Implemented | No | Status | -- | `probe_active_link()`. One-shot. |
| Continuous key-press monitor | Implemented | No | Key monitor (modal) | -- | `stream_consumer_events()`. |
| Model query | Implemented | Yes | Status (planned, slice 1) | `aula-f99 model` | Returns F99 or F75. |
| Battery level readout | Flagged -- uncertain | Unknown | Status | -- | Keyboard shows it on the light bar (`FN+B`). No read command is known. |
| OS mode readout (Android/Windows/Mac/iOS) | Flagged -- uncertain | Unknown | Status | -- | Set by `FN+Q/W/E/R`. Whether it can be read back is not known. |
| Bluetooth connection state | Flagged -- uncertain | Unknown | Status | -- | BT mode presents no USB device. Likely unreachable by this project. |
| Mode-switch position (2.4G / Wired / BT) | Flagged -- uncertain | No | Status | -- | Confirmed unreadable by software. Physical switch only. |

## Lighting (key backlight)

The OEM "Light effect" screen. Lights the keys only, not the ambient bar.
See [gui-features.md](reference/f99/gui-features.md#light-effects).

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Fixed_on (solid colour) | Implemented | Yes | Lighting (planned, slice 5) | `aula-f99 color R G B` | Maps to the captured `0x88` command. |
| Respire | Waiting for discussion | Unknown | Lighting | -- | |
| Rainbow | Waiting for discussion | Unknown | Lighting | -- | |
| Flash_away | Waiting for discussion | Unknown | Lighting | -- | |
| Raindrops | Waiting for discussion | Unknown | Lighting | -- | |
| Ripples_shining | Waiting for discussion | Unknown | Lighting | -- | |
| Stars_twinkle | Waiting for discussion | Unknown | Lighting | -- | Only effect confirmed to show a Speed control. |
| Retro_snake | Waiting for discussion | Unknown | Lighting | -- | |
| Neon_stream | Waiting for discussion | Unknown | Lighting | -- | |
| Reaction | Waiting for discussion | Unknown | Lighting | -- | |
| Sine_wave | Waiting for discussion | Unknown | Lighting | -- | |
| Rotating windmill | Waiting for discussion | Unknown | Lighting | -- | |
| Colorful waterfall | Waiting for discussion | Unknown | Lighting | -- | |
| Blossoming | Waiting for discussion | Unknown | Lighting | -- | |
| Self-define (per-key colour) | Waiting for discussion | Unknown | Lighting | -- | Hardware confirms per-key RGB exists. Editing controls not captured. |
| OFF | Waiting for discussion | Unknown | Lighting | -- | |
| Colour wheel / picker | Waiting for discussion | -- | Lighting | -- | Input method. Terminal equivalent not decided. |
| Hex colour entry | Waiting for discussion | -- | Lighting | -- | Input method. |
| RGB numeric entry | Planned (slice 5) | -- | Lighting | `aula-f99 color R G B` (CLI exists) | TUI form for the same input not built yet. |
| Preset colour swatches | Waiting for discussion | -- | Lighting | -- | 8 fixed colours in the OEM software. |
| Custom colour slots | Waiting for discussion | Unknown | Lighting | -- | 10 saved slots in the OEM software. |
| "Colourful" multi-colour toggle | Flagged -- uncertain | Unknown | Lighting | -- | Unclear whether it overrides the picked colour. |
| Brightness control | Waiting for discussion | Unknown | Lighting | -- | Max value not confirmed. |
| Speed control | Waiting for discussion | Unknown | Lighting | -- | Max value not confirmed. Shown only for some effects. |

## Music (sound-reactive lighting)

The OEM "Effect" screen. See
[gui-features.md](reference/f99/gui-features.md#music-reactive-effects).
Needs the OEM software or driver to run; the firmware does not do this on
its own.

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Music-reactive mode, OFF/ON toggle | Waiting for discussion | Unknown | Music | -- | |
| Audio dance (soft) | Waiting for discussion | Unknown | Music | -- | |
| Dazzling (rock) | Waiting for discussion | Unknown | Music | -- | |
| Clouds rise and snow fly (routine) | Waiting for discussion | Unknown | Music | -- | |
| Light Field Change (voice) | Waiting for discussion | Unknown | Music | -- | |
| The gurgling stream (regular) | Waiting for discussion | Unknown | Music | -- | |
| Blooming (passion) | Waiting for discussion | Unknown | Music | -- | |
| Pearl falling jade plate (rock) | Waiting for discussion | Unknown | Music | -- | |
| Clouds follow the moon (passion) | Waiting for discussion | Unknown | Music | -- | |
| Mountains and Flowing Waters (regular) | Waiting for discussion | Unknown | Music | -- | Name unconfirmed, truncated in the source screenshot. |
| Raining like silk (regular) | Waiting for discussion | Unknown | Music | -- | |
| Gain factor control | Waiting for discussion | Unknown | Music | -- | |
| Smoothness control | Waiting for discussion | Unknown | Music | -- | |

The manual and the vendor listing both state 5 modes for this feature.
The software shows 10. This is unresolved. See
[gui-features.md](reference/f99/gui-features.md#open-questions).

## Keys (key assignment / remapping)

The OEM "Key assignment" screen. See
[gui-features.md](reference/f99/gui-features.md#key-assignment).

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Profile management (add/rename/delete/import/export) | Waiting for discussion | Unknown | Keys | -- | |
| Layer: Default | Waiting for discussion | Unknown | Keys | -- | |
| Layer: FN1 | Waiting for discussion | Unknown | Keys | -- | |
| Layer: FN2 | Waiting for discussion | Unknown | Keys | -- | |
| Layer: Tap | Flagged -- uncertain | Unknown | Keys | -- | What this layer does is not known. Open question. |
| Remap to a standard keycode (Keyboard tab) | Waiting for discussion | Unknown | Keys | -- | |
| Remap to a mouse action (Mouse tab) | Waiting for discussion | Unknown | Keys | -- | 5 actions. |
| Remap to a media/system key (Multimedia tab) | Waiting for discussion | Unknown | Keys | -- | 14 actions. Overlaps the Consumer Control keys this project already reads. |
| Remap to a macro (Macro tab) | Waiting for discussion | Unknown | Keys | -- | Includes a repeat rule: until released, until any key, or a fixed count. |
| Remap to an OS command (Commands tab) | Waiting for discussion | Unknown | Keys | -- | 13 actions. Names read from icons, unconfirmed. |
| Remap to a key combination (Key combination tab) | Waiting for discussion | Unknown | Keys | -- | Modifier plus a typed key. |

## Macros

The OEM "Macro edit panel" screen. See
[gui-features.md](reference/f99/gui-features.md#macros).

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Macro group management (add/rename/delete/import/export) | Waiting for discussion | Unknown | Macros | -- | |
| Macro recording | Waiting for discussion | Unknown | Macros | -- | Captures key presses live. |
| Macro event editing (press/release/delay) | Waiting for discussion | Unknown | Macros | -- | Each event: key, direction, delay in ms. |

## Keybindings

A screen of this project's own. Not an OEM screen. Agreed while scoping
this table: read-only reference, no protocol needed.

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Show the keyboard's factory FN shortcuts | Planned | No | Keybindings | -- | Source: [keybindings.md](reference/f99/keybindings.md). Fixed reference text, not read from the device. |
| Show this project's own TUI key bindings | Planned | No | Keybindings | -- | Depends on the binding set landing in slice 2. |

## Settings

A section of this project's own. See
[tui-spec.md](tui-spec.md#settings).

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Theme picker | Planned (slice 4) | No | Settings | -- | Any built-in Textual theme. |
| Default link (wired/wireless) | Planned (slice 4) | No | Settings | -- | Removes the need for `--wired` on every command. |
| Confirm-before-write toggle | Planned (slice 4) | No | Settings | -- | Default stays on. |
| Config file paths (read-only display) | Planned (slice 4) | No | Settings | -- | XDG paths. |

## Ambient light bar

A separate lighting system from the key backlight. No OEM software screen
manages it; the firmware handles it through `FN` shortcuts only. See
[keybindings.md](reference/f99/keybindings.md#rgb-ambient-light-bar).

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| Light bar mode cycle | Flagged -- uncertain | Unknown | Lighting (proposed sub-section) | -- | `FN+Shift-R` on the keyboard itself. No protocol captured. |
| Light bar colour cycle | Flagged -- uncertain | Unknown | Lighting (proposed sub-section) | -- | `FN+/?` on the keyboard itself. |
| Light bar brightness cycle | Flagged -- uncertain | Unknown | Lighting (proposed sub-section) | -- | `FN+Alt-R` on the keyboard itself. |
| Light bar speed cycle | Flagged -- uncertain | Unknown | Lighting (proposed sub-section) | -- | `FN+Ctrl-R` on the keyboard itself. |

## Hardware-only shortcuts

FN shortcuts that change device state but have no OEM software screen.
Flagged because we do not yet know whether this project can trigger them
in software, separately from the physical key combination. See
[keybindings.md](reference/f99/keybindings.md).

| Feature | Status | Writes to device? | TUI location | CLI | Notes |
| --- | --- | --- | --- | --- | --- |
| OS mode switch (Android/Windows/Mac/iOS) | Flagged -- uncertain | Unknown | Status | -- | `FN+Q/W/E/R` on the keyboard. |
| Bluetooth slot switch (1/2/3) | Flagged -- uncertain | Unknown | Status | -- | `FN+1/2/3` on the keyboard. BT mode is likely unreachable by USB. |
| 2.4G pairing | Flagged -- uncertain | Unknown | Status | -- | `FN+\`` (hold 3s) on the keyboard. |
| Restore factory defaults | Flagged -- uncertain | Unknown | Settings | -- | `FN+Esc` (hold 3s) on the keyboard. Destructive; would need extra confirmation if ever built. |
| Windows-key lock | Flagged -- uncertain | Unknown | Settings | -- | `FN+` left `Win` on the keyboard. Windows mode only. |

## Summary

| Area | Implemented | Planned | Waiting for discussion | Flagged -- uncertain |
| --- | --- | --- | --- | --- |
| Status | 4 | 0 | 0 | 4 |
| Lighting | 1 | 1 | 20 | 1 |
| Music | 0 | 0 | 13 | 0 |
| Keys | 0 | 0 | 10 | 1 |
| Macros | 0 | 0 | 3 | 0 |
| Keybindings | 0 | 2 | 0 | 0 |
| Settings | 0 | 4 | 0 | 0 |
| Ambient light bar | 0 | 0 | 0 | 4 |
| Hardware-only shortcuts | 0 | 0 | 0 | 5 |
