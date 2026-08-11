<div align="center">

# aula-f99-controller

**Custom control software for the AULA F99 keyboard — no OEM software needed.**

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-18%20passing-brightgreen)
![Lint](https://img.shields.io/badge/lint-ruff-red?logo=ruff&logoColor=white)
![Types](https://img.shields.io/badge/types-mypy%20strict-blue)

</div>

---

It talks straight to the keyboard's own USB interface.

## Features

| Feature | Status |
| --- | --- |
| Check the keyboard's connection status | Implemented |
| Detect which link (wired or wireless) is active | Implemented |
| Watch media-key and volume-knob presses live | Implemented |
| Set a solid RGB color | Implemented |
| Query the keyboard's model name | Implemented |

More features (per-key RGB, lighting effects, macros) are planned. See
[docs/spec.md](docs/spec.md) for the full list and technical details.

## Requirements

- Windows (Linux support is planned)
- [mise](https://mise.jdx.dev/) installed

mise installs the correct Python and [uv](https://docs.astral.sh/uv/)
version for you. You do not need to install Python yourself.

## Install

Run these commands in the project folder:

```bash
mise install
mise exec -- uv sync
```

This sets up the Python environment and installs all dependencies.

## Quick start

Launch the TUI (recommended way to start):

```bash
mise run tui
```

In the TUI:

| Key | Action |
| --- | --- |
| `r` | Refresh the connection status |
| `t` | Enter key-press listener mode (press a media key, a volume key, or turn the volume knob — each press pops a notification) |
| `Escape` | Leave listener mode |
| `q` | Quit |

## Command-line usage

You can also control the keyboard directly, without the TUI:

```bash
mise exec -- uv run aula-f99 model
mise exec -- uv run aula-f99 color 255 0 0
```

Add `--wired` if the keyboard is connected by USB cable, not the wireless
dongle.

## Quality checks

This project is linted with [ruff](https://docs.astral.sh/ruff/), type-checked
in mypy strict mode (no `Any`), covered by 18 unit tests, and scanned for
secrets on every commit (gitleaks, detect-secrets). Run the full suite
yourself:

```bash
mise run check
```

## Learn more

[docs/spec.md](docs/spec.md) has the full technical reference: protocol
details, device IDs, module structure, and the full list of mise tasks.
