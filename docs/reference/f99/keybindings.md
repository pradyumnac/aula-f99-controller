# AULA F99 key bindings

This page lists the keyboard's built-in FN shortcuts. The firmware handles
them. They work with no driver and no software from this project.

Source: the AULA F99 product manual. The manual is kept locally at
`docs/AULA_F99_Manual.pdf`. It is not committed. See
[hardware.md](hardware.md) for the physical controls these shortcuts use.

## Two lighting systems

The keyboard has two separate lighting systems. Each has its own
shortcuts. Do not confuse them.

| System | Location | Shortcut group |
| --- | --- | --- |
| Key backlight | Under the keys | `FN` + `\|`, `Tab`, arrow keys |
| RGB ambient light bar | Side of the case | `FN` + `Shift-R`, `/?`, `Alt-R`, `Ctrl-R`, `B` |

## Connection

| Shortcut | Effect |
| --- | --- |
| `FN` + `` ` `` | Select 2.4G wireless mode |
| `FN` + `1` | Select Bluetooth slot 1 |
| `FN` + `2` | Select Bluetooth slot 2 |
| `FN` + `3` | Select Bluetooth slot 3 |
| `FN` + `Esc` (hold 3s) | Restore factory defaults. Saved Bluetooth pairings stay. |

To pair, first set the physical switch to the matching mode. Then hold the
shortcut. See [hardware.md](hardware.md) for the pairing sequence.

## Operating system mode

The OS mode changes what the F-row does. See
[F-row behaviour](#f-row-behaviour). Each mode flashes its key red for 3
seconds when selected.

| Shortcut | OS mode |
| --- | --- |
| `FN` + `Q` | Android |
| `FN` + `W` | Windows |
| `FN` + `E` | Mac |
| `FN` + `R` | iOS |

## Key backlight

| Shortcut | Effect |
| --- | --- |
| `FN` + `\|` | Switch lighting mode. Cycles the 15 RGB light effects. |
| `FN` + `Tab` | Switch colour |
| `FN` + `↑` | Brightness up |
| `FN` + `↓` | Brightness down |
| `FN` + `←` | Speed down |
| `FN` + `→` | Speed up |

## RGB ambient light bar

| Shortcut | Effect |
| --- | --- |
| `FN` + `Shift-R` | Switch light bar mode |
| `FN` + `/?` | Switch light bar colour |
| `FN` + `Alt-R` | Cycle light bar brightness |
| `FN` + `Ctrl-R` | Cycle light bar speed |
| `FN` + `B` | Switch the light bar to power mode. It then shows the battery level. |

In power mode the bar shows 5 lights. Each green light means 20% charge. A
full charge shows solid green. A low battery shows all red. The bar shows a
streaming animation while charging.

## Missing keys

The layout has no dedicated Insert, Print Screen, Scroll Lock, or Pause
key. These shortcuts supply them.

| Shortcut | Sends |
| --- | --- |
| `FN` + `Del` | `Insert` |
| `FN` + `U` | `Print Screen` |
| `FN` + `I` | `Scroll Lock` |
| `FN` + `O` | `Pause` |

## Windows key lock

| Shortcut | Effect |
| --- | --- |
| `FN` + left `Win` | Lock or unlock the left Windows key |

The Lock WIN indicator stays on while the key is locked. This applies to
Windows mode only.

In Mac mode and iOS mode, the left `Win` and left `Alt` positions swap.
The lock does not apply in those modes.

## F-row behaviour

The F-row has two behaviours: a single press and an `FN` combination. The
OS mode decides which behaviour gives the F-keys.

### Windows mode

A single press gives the F-keys. `FN` gives the media and system actions.

| Key | Single press | `FN` combination |
| --- | --- | --- |
| F1 | `F1` | Home page |
| F2 | `F2` | Email |
| F3 | `F3` | Convert window |
| F4 | `F4` | Open Explorer |
| F5 | `F5` | Backlight brightness down |
| F6 | `F6` | Backlight brightness up |
| F7 | `F7` | Previous track |
| F8 | `F8` | Play / Pause |
| F9 | `F9` | Next track |
| F10 | `F10` | Mute |
| F11 | `F11` | Volume down |
| F12 | `F12` | Volume up |

### Android mode and Mac mode

The behaviour is reversed. A single press gives the media and system
actions. `FN` gives the F-keys. Both modes use the same table.

| Key | Single press | `FN` combination |
| --- | --- | --- |
| F1 | Screen brightness down | `F1` |
| F2 | Screen brightness up | `F2` |
| F3 | Convert window | `F3` |
| F4 | Return to desktop | `F4` |
| F5 | Backlight brightness down | `F5` |
| F6 | Backlight brightness up | `F6` |
| F7 | Previous track | `F7` |
| F8 | Play / Pause | `F8` |
| F9 | Next track | `F9` |
| F10 | Mute | `F10` |
| F11 | Volume down | `F11` |
| F12 | Volume up | `F12` |

### iOS mode

The same as Android mode and Mac mode, with one difference: `F3` has no
single-press action.

| Key | Single press | `FN` combination |
| --- | --- | --- |
| F1 | Screen brightness down | `F1` |
| F2 | Screen brightness up | `F2` |
| F3 | None | `F3` |
| F4 | Return to desktop | `F4` |
| F5 | Backlight brightness down | `F5` |
| F6 | Backlight brightness up | `F6` |
| F7 | Previous track | `F7` |
| F8 | Play / Pause | `F8` |
| F9 | Next track | `F9` |
| F10 | Mute | `F10` |
| F11 | Volume down | `F11` |
| F12 | Volume up | `F12` |

## Notes

The manual labels F5 and F6 as "Brightness-" and "Brightness+", next to F1
and F2 which it labels "Screen brightness". This page reads F5 and F6 as
the key backlight. That reading is not confirmed against the hardware.

Remapping through the OEM software can change any of these actions. This
page lists the factory defaults only. See
[gui-features.md](gui-features.md) for the remapping features.
