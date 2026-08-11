# AULA F99 device reference

This folder holds everything known about the AULA F99 keyboard itself. It
describes the device, not this project. Project documentation lives
outside this folder.

| Page | Contents |
| --- | --- |
| [hardware.md](hardware.md) | Layout, mode switch, ports, indicators, battery, connection signals |
| [keybindings.md](keybindings.md) | Factory `FN` shortcuts and the F-row behaviour per OS mode |
| [protocol.md](protocol.md) | USB identifiers, packet format, confirmed commands, capture method |
| [gui-features.md](gui-features.md) | What the OEM configuration software offers. A baseline for comparison. |

## Sources

| Source | Used for |
| --- | --- |
| AULA F99 product manual | Hardware and key bindings. Kept locally at `docs/AULA_F99_Manual.pdf`. Not committed. |
| OEM software screenshots | The feature baseline. |
| OpenRGB project | The USB protocol. Links in [protocol.md](protocol.md). |
| Direct observation | USB enumeration and Consumer Control reports from a real device. |

## Confidence

Each page marks facts that are not confirmed. Treat those as open
questions, not as settled. Facts taken from the manual are reliable for
behaviour, but the manual has errors and its English is imprecise.
