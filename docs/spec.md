# Project specification

This page is a reference for the project: its modules, commands, and
tooling. For an introduction, read the [README](../README.md).

Facts about the keyboard itself live in
[reference/f99/](reference/f99/README.md). This page does not repeat them.

## Feature status

[feature-tracking.md](feature-tracking.md) is the single list of every
feature: what is implemented, what is planned, and what is still waiting
for discussion. This page does not repeat that list. The module reference
below says where implemented code lives, not what is implemented.

## Module reference

| Module | Responsibility |
| --- | --- |
| [`protocol.py`](../src/aula_f99/protocol.py) | Packet layouts, device IDs, checksum |
| [`controller.py`](../src/aula_f99/controller.py) | Opens the vendor HID device. Sends write commands. |
| [`detect.py`](../src/aula_f99/detect.py) | Read-only connection detection and key-press listening |
| [`usage_codes.py`](../src/aula_f99/usage_codes.py) | Consumer usage code to name mapping, backed by TOML |
| [`cli.py`](../src/aula_f99/cli.py) | Command-line entry point |
| [`tui/app.py`](../src/aula_f99/tui/app.py) | The terminal interface |

### Detection functions

`detect.py` offers three entry points.

| Function | Behaviour |
| --- | --- |
| `detect_connection()` | Enumerates only. Returns which devices are present. Cannot prove which link is live. |
| `probe_active_link()` | Listens once. Returns the link that delivers a report first. Returns as soon as one arrives. |
| `stream_consumer_events()` | Listens continuously. Calls a callback per report until told to stop. |

### Usage code lookup

`usage_codes.py` maps a Consumer Control usage code to a display name. The
mapping lives in
[`config/consumer_usage.toml`](../config/consumer_usage.toml), not in
code. The file is meant to be edited by hand.

| Function | Behaviour |
| --- | --- |
| `load_usage_map()` | Reads the file. |
| `save_usage_map()` | Writes the file. |
| `get_or_record()` | Looks up a code. Appends an `"Unknown"` stub for a new code, so it is not lost. |
| `format_event()` | Turns a raw report into a display string, for example `"Vol+ (Raw: 0x00E9)"`. |
| `is_release_report()` | Reports whether a report is a key release. |

## CLI reference

Entry point: `aula-f99`.

| Command | Effect |
| --- | --- |
| `aula-f99 tui` | Launch the terminal interface |

Add `--wired` to any command to use the cable instead of the dongle.
Writes over the cable fail today. See
[reference/f99/protocol.md](reference/f99/protocol.md#not-captured-yet).

Each feature's own CLI switch, if it has one, is listed in
[feature-tracking.md](feature-tracking.md).

## Terminal interface

The interface design is specified in
[reference/tui-spec.md](tui-spec.md).

## mise tasks

Defined in [`mise.toml`](../mise.toml).

| Task | Effect |
| --- | --- |
| `mise run tui` | Launch the terminal interface |
| `mise run test` | Run the test suite |
| `mise run lint` | Lint with ruff |
| `mise run format` | Format with ruff |
| `mise run format:check` | Check formatting, make no changes |
| `mise run typecheck` | Static type-check with mypy |
| `mise run lint:md` | Lint the Markdown files |
| `mise run check` | Run every check above, then the tests |
| `mise run precommit:install` | Install the pre-commit git hook |
| `mise run precommit:run` | Run all pre-commit hooks against the whole repo |
| `mise run secrets:baseline` | Regenerate the detect-secrets baseline |

## Toolchain

- [mise](https://mise.jdx.dev/) pins the Python version and the `uv`
  version (`mise.toml`).
- [uv](https://docs.astral.sh/uv/) manages Python dependencies
  (`pyproject.toml`, `uv.lock`).
- [ruff](https://docs.astral.sh/ruff/) lints and formats the code.
- [mypy](https://mypy-lang.org/) type-checks the code in strict mode.
  Explicit `Any` is not allowed (`disallow_any_explicit = true`).
- A local stub package ([`stubs/hid/`](../stubs/hid/__init__.pyi)) gives
  mypy real types for the untyped `hid` package.
- [pre-commit](https://pre-commit.com/) runs ruff, mypy, secret scanning
  (gitleaks, detect-secrets), Markdown lint, and file-hygiene checks
  before each commit.
