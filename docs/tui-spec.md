# TUI specification

This page specifies the terminal interface. It records decisions, not
current behaviour. Items marked "Open" are not decided yet.

For what the code does today, see [spec.md](spec.md). For the full
feature list and its build status, see
[feature-tracking.md](feature-tracking.md). That page owns the per-feature
status and CLI columns; this page owns UI structure only.

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
| Say why | A failure never shows a traceback or a silent no-op. It names what failed and why. See [Error handling](#error-handling). |

## Error handling

Two kinds of thing can fail: a config file the user hand-edited, and the
keyboard itself. Each has one fixed rule.

| Failure | Rule |
| --- | --- |
| A config file will not parse | Fall back to that file's defaults, keep running, and warn once, naming the file and the parse error. A bad edit must never lock the user out of the program that fixes it. |
| A config file parses but breaks a rule | Drop only the offending entry and warn, naming it and why -- a hand-edited `tui_keymap.toml` skips the checks the rebind screen enforces live (reserved key, unrecognised key, a key another action already holds), so loading is the only place left to enforce them. Valid entries in the same file are kept. |
| A config file will not save | Keep the old value, and say so. The setting does not silently appear to have changed. |
| A config write is interrupted | The previous file survives intact. Every save writes to a temp file in the same directory first, then renames it over the target -- never truncate-then-write. |
| Two threads write the same file at once | Serialized behind a lock. The key monitor runs one listener thread per link, and both can log an unrecognised code to the same file at once; without a lock, the second write silently overwrites the first's change. |
| The keyboard is absent or unreadable | Say which device was looked for and why the attempt failed. On the CLI: one line to stderr, exit 1. In the TUI: the panel or header states it, and the app stays up. |
| A background worker raises | Report it and leave the interface usable. A dead worker never fails silently. |

Every config load collapses its failure modes into one exception,
`ConfigLoadError`, carrying the path and the cause. Callers catch that one
type, choose the fallback, and show the user the reason.

A genuine bug is not caught. Only the failures above are turned into
messages; anything else still raises, so it gets found rather than hidden.

## Layout

The main screen holds four regions.

| Region | Position | Contents |
| --- | --- | --- |
| Header | Top | Program name and the connected device. |
| Sidebar | Left, fixed width | The section list. Selecting a section swaps the content area. |
| Content | Right, fills the rest | The active section's panel. |
| Footer | Bottom | The keys available in the active section. |

The sidebar is 20 columns wide, enough for the longest section name.

### Borders

The sidebar and the content area each sit in a round border. Every border
colour is a theme variable, so the "Theme, not colour" rule holds.

| Element | Rule |
| --- | --- |
| Border title | The sidebar reads "Sections". The content area reads the active section's name. |
| Unfocused border | `$panel`. |
| Focused border | `$primary`. Only the focused pane uses it, so `h`, `l`, and `Tab` produce a visible change. |

## Sections

The sidebar mirrors the OEM software, plus three sections of this
project's own. For what each section contains and its status, see
[feature-tracking.md](feature-tracking.md).

| Section | Source |
| --- | --- |
| Status | This project |
| Lighting | OEM "Light effect" |
| Music | OEM "Effect" |
| Keys | OEM "Key assignment" |
| Macros | OEM "Macro edit panel" |
| Keybindings | This project |
| Settings | This project |

Keybindings shows the keyboard's factory `FN` shortcuts, and nothing
else. It needs no captured protocol -- the list is static reference text.

The app's own keys are a separate screen, reached from Settings or with
`?`. See [App keybindings](#app-keybindings). Keeping the two apart
matters: one list is the keyboard's, the other is this program's, and
mixing them in one section invites confusion about which is which.

A section with no captured protocol shows a short "not implemented" note.
It does not list the OEM features it cannot deliver. This keeps the
interface lean and avoids implying that a feature exists.

## Modals

Modals open over the main screen. `Escape` closes each one.

| Modal | Opened by | Purpose |
| --- | --- | --- |
| Key monitor | A key binding, from any section | Streams media and volume key presses as notifications. Proves which link is live. |
| Rebind | Selecting a row in [App keybindings](#app-keybindings) | Captures one key press, and assigns it to that action. |
| Confirm write | Any action that writes to the keyboard | States the exact command and asks for confirmation. |

The key monitor has no sidebar entry. It is a tool, not a section.

## Theme

The interface uses `textual-dark`, a Textual built-in theme. The project
defines no custom theme. Built-in themes bring accessible variants (high
contrast, monochrome) at no cost.

The user can pick another built-in theme in Settings. The choice is
saved.

## Settings

Settings is a list of panes. Selecting one opens it.

| Setting | Effect |
| --- | --- |
| App keybindings | Open the [App keybindings](#app-keybindings) screen. |
| Theme | Opens Textual's own command-palette theme picker (the same one `ctrl+p` -> "Change theme" reaches). Saved. |
| Default link | Which link commands target: wired or wireless. Toggled in place. Removes the need for `--wired`. |
| Confirm before write | Turn the write-confirmation dialog off. Default is on. Toggled in place. |
| Config paths | Show where each config and data file lives. Read-only. |

Default link and confirm-before-write are saved, but nothing reads them
yet -- there is no write action in the TUI until Lighting (slice 5)
lands. `--wired` still does the job on the CLI in the meantime.

### App keybindings

A screen listing every key this program uses: the key, what it does, and
its group. It opens from Settings, or with `?` from anywhere.

Selecting a row rebinds it. The screen asks for the new key, then:

| Case | Result |
| --- | --- |
| The key is free | Saved, and live at once. No restart. |
| The key already has an action | Refused, naming the action that holds it. |
| The key is the action's own default | The override is dropped, not stored as a no-op. |
| `Escape`, `Tab`, `Shift+Tab`, `Enter` | Refused. These are reserved, so a rebind can never strand the user. |

Overrides are saved by binding id, so a renamed key never orphans a
setting. They live in `tui_keymap.toml`; see
[Configuration storage](#configuration-storage). Only the primary key of
an action is rebindable -- alias keys (`Left`, `Right`, `Tab`) stay put.

## Configuration storage

These rules apply to every file the program writes.

| Rule | Detail |
| --- | --- |
| XDG layout | Config goes under `XDG_CONFIG_HOME`. Data goes under `XDG_DATA_HOME`. Both fall back to `~/.config` and `~/.local/share` when unset, on every platform including Windows. |
| Customisable | The user can override each location. |
| Text only | Every saved file is plain text. No binary formats, no databases. |
| Stow-friendly | The layout suits GNU stow, so the user can keep these files in a dotfiles repository. |

| File | Path | Holds |
| --- | --- | --- |
| `tui_keymap.toml` | `$XDG_CONFIG_HOME/aula-f99/` | App keybinding overrides, as binding id to key. Absent until the first rebind. |
| `settings.toml` | `$XDG_CONFIG_HOME/aula-f99/` | Theme, default link, confirm-before-write. Absent until the first change; each setting falls back to its default. |

`config/f99_keybindings.toml` currently lives inside the repository. It
must move to the XDG config path. The move needs a fallback so an existing
in-repo file still loads.

## Key bindings

The scheme follows nvim conventions: `hjkl` motion, plus a mnemonic
letter per section. Do not reuse a binding that the keyboard itself uses.
See [reference/f99/keybindings.md](reference/f99/keybindings.md).

`h`, `j`, `k`, `l`, `r`, `m`, and `q` are reserved for navigation and
actions. Every section takes a mnemonic letter from within its own name
that avoids those seven.

| Section | Hotkey | Mnemonic |
| --- | --- | --- |
| Status | `s` | **S**tatus |
| Lighting | `i` | l**i**ghting |
| Music | `u` | m**u**sic |
| Keys | `e` | k**e**ys |
| Macros | `a` | m**a**cros |
| Keybindings | `b` | key**b**indings |
| Settings | `g` | settin**g**s |

The sidebar underlines each mnemonic letter in place, so the hotkey is
visible on screen rather than only documented here.

| Key | Scope | Effect |
| --- | --- | --- |
| The hotkeys above | Global | Jump straight to that section. |
| `j` / `k`, `Down` / `Up` | Sidebar | Move the highlight. The content switches at once; no `Enter` needed. |
| `h`, `Left` | Global | Focus the sidebar. |
| `l`, `Right`, `Tab` | Global | Focus the content pane. |
| `f` | Global | Fold or unfold the sidebar. |
| `r` | Global | Refresh. See [Refresh](#refresh). |
| `m` | Global | Open the key monitor. |
| `?` | Global | Open [App keybindings](#app-keybindings). |
| `Escape` | Modal | Close the modal. Never quits. |
| `q` | Global | Quit. |

Every key above is rebindable, and the table gives the defaults. Folding
the sidebar gives the content the full width, which the wider tables want.

The footer omits the section hotkeys. Seven more entries would push the
action keys off an 80-column footer, and the sidebar already shows them.

### Refresh

`r` does two things, in every section:

1. Refreshes the active section, if it has anything to refresh.
2. Proves the live link, and shows the result in the header.

The second half runs everywhere, so `r` is useful even in a section that
has nothing of its own to reload. Proving the link needs a key press on
the keyboard, so the header asks for one while the probe runs. The probe
runs in a worker; the interface stays responsive.

## Vertical slices

Work proceeds one slice at a time. A slice is complete when it has code,
tests, and documentation.

| Slice | Content | State |
| --- | --- | --- |
| 1 | Deepen Status: live link state, model identity, and whatever else is readable without a write. | Next |
| 2 | The shell: sidebar, theme, content switcher, footer, key-monitor modal. | Done |
| 3 | Keybindings: the factory `FN` shortcuts. This project's own bindings became the App keybindings screen, which also rebinds them. | Done |
| 4 | Settings, including XDG storage and the saved theme. | Done |
| 5 | Lighting: solid colour, with the confirm-write modal. | Planned |
| 6+ | Any section whose protocol gets captured. | Blocked |

Slices 5 and later depend on captured commands. See
[reference/f99/protocol.md](reference/f99/protocol.md#not-captured-yet).

For the status of individual features within a slice's section, see
[feature-tracking.md](feature-tracking.md).

## Open questions

1. Does Status poll the link continuously, or refresh on demand?
