# TUI specification

This page specifies the terminal interface. It records decisions, not
current behaviour. Items marked "Open" are not decided yet.

For what the code does today, see [../spec.md](../spec.md). For the
feature baseline this interface targets, see
[f99/gui-features.md](f99/gui-features.md).

## Design rules

These rules come from common terminal-interface practice. They apply to
every screen.

| Rule | Effect |
| --- | --- |
| Show the keys | A footer lists the keys available right now. The list changes with the active panel. |
| Escape goes back | `Escape` closes a dialog or leaves a mode. It never quits the program. |
| One key, one meaning | A key keeps the same meaning across panels. |
| Theme, not colour | All colour comes from theme variables. No panel sets a fixed colour value. |
| Works at 80x24 | The layout stays usable at the minimum terminal size. Larger terminals get more room, not more panels. |
| Never block | Device reads and writes run in a worker. The interface stays responsive. |
| Friction before writes | Any action that writes to the keyboard needs a confirmation first. |

## Layout

The main screen holds four regions.

| Region | Position | Contents |
| --- | --- | --- |
| Header | Top | Program name and the connected device. |
| Sidebar | Left, fixed width | The section list. Selecting a section swaps the content area. |
| Content | Right, fills the rest | The active section's panel. |
| Footer | Bottom | The keys available in the active section. |

## Sections

The sidebar mirrors the OEM software, plus two sections of this project's
own.

| Section | Source | Purpose |
| --- | --- | --- |
| Status | This project | Connection state. Which link is active. Device identity. |
| Lighting | OEM "Light effect" | Pick an effect. Set colour, brightness, and speed. |
| Music | OEM "Effect" | Pick a sound-reactive effect. Set gain and smoothness. |
| Keys | OEM "Key assignment" | Remap keys, per layer and per profile. |
| Macros | OEM "Macro edit panel" | Record and edit macros. |
| Settings | This project | Interface and device preferences. |

A section with no captured protocol shows a short "not implemented" note.
It does not list the OEM features it cannot deliver. This keeps the
interface lean and avoids implying that a feature exists. The full OEM
list stays in [f99/gui-features.md](f99/gui-features.md).

## Modals

Modals open over the main screen. `Escape` closes each one.

| Modal | Opened by | Purpose |
| --- | --- | --- |
| Key monitor | A key binding, from any section | Streams media and volume key presses as notifications. Proves which link is live. |
| Confirm write | Any action that writes to the keyboard | States the exact command and asks for confirmation. |

The key monitor has no sidebar entry. It is a tool, not a section.

## Theme

The interface uses `textual-dark`, a Textual built-in theme. The project
defines no custom theme. Built-in themes bring accessible variants (high
contrast, monochrome) at no cost.

The user can pick another built-in theme in Settings. The choice is
saved.

## Settings

| Setting | Effect |
| --- | --- |
| Theme | Pick any built-in Textual theme. Saved. |
| Default link | Which link commands target: wired or wireless. Removes the need for `--wired`. |
| Confirm before write | Turn the write-confirmation dialog off. Default is on. |
| Config paths | Show where each config and data file lives. Read-only. |

## Configuration storage

These rules apply to every file the program writes.

| Rule | Detail |
| --- | --- |
| XDG layout | Config goes under `XDG_CONFIG_HOME`. Data goes under `XDG_DATA_HOME`. Both fall back to `~/.config` and `~/.local/share` when unset, on every platform including Windows. |
| Customisable | The user can override each location. |
| Text only | Every saved file is plain text. No binary formats, no databases. |
| Stow-friendly | The layout suits GNU stow, so the user can keep these files in a dotfiles repository. |

`config/consumer_usage.toml` currently lives inside the repository. It
must move to the XDG config path. The move needs a fallback so an existing
in-repo file still loads.

## Key bindings

Bindings are Open, except for the rules above. The set must cover:

- Move between sections.
- Open the key monitor.
- Refresh the current section.
- Quit.

Do not reuse a binding that the keyboard itself uses. See
[f99/keybindings.md](f99/keybindings.md).

## Vertical slices

Work proceeds one slice at a time. A slice is complete when it has code,
tests, and documentation.

| Slice | Content | State |
| --- | --- | --- |
| 1 | Deepen Status: live link state, model identity, and whatever else is readable without a write. | Next |
| 2 | The shell: sidebar, theme, content switcher, footer, key-monitor modal. | Planned |
| 3 | Settings, including XDG storage and the saved theme. | Planned |
| 4 | Lighting: solid colour, with the confirm-write modal. | Planned |
| 5+ | Any section whose protocol gets captured. | Blocked |

Slices 4 and later depend on captured commands. See
[f99/protocol.md](f99/protocol.md#not-captured-yet).

## Open questions

1. Which keys move between sections?
2. Does Status poll the link continuously, or refresh on demand?
3. Can Status read the battery level? The keyboard shows it on the light
   bar, but no read command is captured.
