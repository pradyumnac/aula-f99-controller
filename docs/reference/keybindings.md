# Default key bindings (vendor manual)

This page lists the keyboard's built-in FN shortcuts. The keyboard's own
firmware handles these. They work with no driver and no software from this
project.

Source: AULA F99 product manual (kept locally at
`docs/AULA_F99_Manual.pdf`, not committed — see
[Protocol origin](../spec.md#protocol-origin) for why). The manual's text
layer has OCR errors. Combos marked "Unconfirmed" need a hands-on check
against the real keyboard before you rely on them.

## Physical connection switch

The keyboard has a 3-position switch on the top-left edge. It picks the
connection mode. Software cannot change this switch.

| Switch position | Mode |
| --- | --- |
| Left | 2.4G wireless (dongle) |
| Middle | Bluetooth |
| Right | Wired (USB-C) |

## Connection setup

| Shortcut | Effect |
| --- | --- |
| `FN` + `` ` `` (hold 3s), switch set to 2.4G | Enter 2.4G pairing mode. Plug in the receiver to finish pairing. |
| `FN` + `1` | Connect Bluetooth slot 1 |
| `FN` + `2` | Connect Bluetooth slot 2 |
| `FN` + `3` | Connect Bluetooth slot 3 |
| `FN` + `Esc` (hold 3s) | Restore factory defaults. Saved Bluetooth pairings are kept. |

## OS mode

OS mode changes what the F-row keys do. Each mode flashes its key red for
3 seconds when selected.

| Shortcut | OS mode |
| --- | --- |
| `FN` + `Q` | Android |
| `FN` + `W` | Windows |
| `FN` + `E` | Mac |
| `FN` + `R` | iOS |

## Lighting

| Shortcut | Effect |
| --- | --- |
| `FN` + `Shift` + `R` | Cycle lighting effect (15 effects total, including a music-reactive mode) |
| `FN` + `/` | Cycle lighting color (Unconfirmed — OCR unclear) |
| `FN` + `Alt` + `R` | Cycle brightness level |
| `FN` + `Ctrl` + `R` | Cycle animation speed |
| `FN` + `↑` | Brightness up |
| `FN` + `↓` | Brightness down |
| `FN` + `←` / `FN` + `→` | Speed down / up (Unconfirmed — OCR unclear) |
| `FN` + `Tab` | Toggle lighting color scheme (Unconfirmed — OCR unclear) |
| `FN` + `B` | Show battery level on the light bar (green segments = charge, all red = low) |

## Utility

| Shortcut | Effect |
| --- | --- |
| `FN` + left `Win` | Lock or unlock the left Windows key |

When OS mode is Mac or iOS, this shortcut swaps to `Alt` instead of `Win`.

## Not covered here

- Per-key remapping and macro definitions. These need the OEM driver
  software; this project does not implement them yet.
- The exact HID reports these shortcuts send. See
  [../spec.md](../spec.md) for what this project has confirmed on the
  wire.
