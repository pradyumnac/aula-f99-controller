# AULA F99 hardware

This page describes the physical keyboard: its layout, controls, ports,
and indicators.

Source: the AULA F99 product manual. The manual is kept locally at
`docs/AULA_F99_Manual.pdf`. It is not committed.

## Layout

The keyboard uses a compact layout with a number pad. It keeps the F-row,
the arrow cluster, and a 4-key navigation block above the number pad. It
drops the dedicated Insert, Print Screen, Scroll Lock, and Pause keys.
`FN` shortcuts supply those. See [keybindings.md](keybindings.md).

| Property | Value |
| --- | --- |
| Keys | 99 |
| Construction | Gasket mount |
| Switches | Mechanical, hot-swap (pluggable) |
| Keycaps | Pluggable |
| Dimensions | 390.63 x 146.78 x 42.57 mm, +/- 0.5 mm |
| Weight | 1183 g |

The manual's own specification list states 99 keys. An earlier text
extract of the same manual read "89 keys". 99 is correct.

## Rear edge

Three items sit on the rear edge of the case, in this order:

| Item | Purpose |
| --- | --- |
| USB receiver slot | Holds the 2.4G dongle when it is not in use |
| Mode switch | Selects the connection mode |
| Type-C port | Wired data and charging |

The mode switch has three positions.

| Position | Mode |
| --- | --- |
| 1 | 2.4G wireless |
| 2 (centre) | Wired |
| 3 | Bluetooth |

Software cannot read or change this switch. The manual calls it the "upper
left" switch in its text, and shows it on the rear edge in its diagram.
Both refer to the same slider.

## Indicators

| Indicator | Location | Shows |
| --- | --- | --- |
| Caps Lock | Left edge, by the Caps Lock key | Caps Lock state |
| RGB light / power | Above the arrow cluster | Lighting and power state |
| NUM | Above the number pad | Num Lock state |
| RGB ambient light bar | Side of the case | Lighting effect, or battery level in power mode |

The keyboard also uses individual key lights as status signals. See
[Connection modes](#connection-modes).

## Connection modes

The keyboard supports three links. The mode switch picks one. Only one
link is active at a time.

| Mode | Transport | Device name |
| --- | --- | --- |
| Wired | USB Type-C | -- |
| 2.4G wireless | USB dongle | -- |
| Bluetooth | BLE 5.0 or BLE 3.0 | `AULA-F99 5.0` or `AULA-F99 3.0` |

Bluetooth holds three device slots. Switch between them with `FN` + `1`,
`FN` + `2`, or `FN` + `3`.

### Signals

| Mode | Signal |
| --- | --- |
| Wired | The `4` key lights white for 2 seconds. |
| 2.4G, not paired | The `` ` `` key blinks cyan slowly. |
| 2.4G, pairing | Hold `FN` + `` ` `` for 3 seconds, then plug in the receiver. |
| 2.4G, connected | The `` ` `` key lights cyan for 2 seconds. |
| Bluetooth, pairing | The slot key blinks blue fast. |
| Bluetooth, reconnecting | The slot key blinks blue slowly. |
| Bluetooth, connected | The slot key lights blue for 2 seconds. |

The 2.4G link is paired at the factory. Re-pairing is only needed if the
link is lost.

## Power

| Property | Value |
| --- | --- |
| Battery | 2 x 4000 mAh lithium, rechargeable |
| Rated voltage | DC 3.7 V |
| Charging | DC 5 V, up to 830 mA |
| Battery life, default lighting | 53 hours or more |
| Battery life, lights off | 400 hours or more |

The keyboard has a power switch. To read the battery level, press
`FN` + `B`. The ambient light bar then shows 5 lights. Each green light
means 20% charge. All red means the battery is low.

## Supported systems

Windows XP, 7, 8, and 10. Android. iOS. macOS.

Set the matching OS mode after you connect. See
[keybindings.md](keybindings.md).
