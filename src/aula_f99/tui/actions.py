"""Every rebindable TUI action, and the saved keymap that overrides it.

The registry here is the single source of truth for the sidebar, the
screen's bindings, and the Keybindings screen. Textual applies an override
by binding id, so a saved keymap needs no code change to take effect.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from textual.keys import Keys, key_to_character

from aula_f99.config import atomic_write_toml, tui_keymap_path
from aula_f99.errors import ConfigLoadError

_MODIFIERS = frozenset({"ctrl", "shift", "alt", "meta"})
_KNOWN_KEY_NAMES = frozenset(k.value for k in Keys)


def _is_known_key(key: str) -> bool:
    """Whether Textual would recognise `key` as a key identifier at all.

    A live rebind can never produce anything else -- it captures a real key
    press, so whatever comes out is valid by construction. A hand-edited
    keymap file has no such guarantee.
    """
    *modifiers, base = key.split("+")
    if not all(m in _MODIFIERS for m in modifiers):
        return False
    return base in _KNOWN_KEY_NAMES or key_to_character(base) is not None


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    hotkey: str
    label_markup: str

    @property
    def binding_id(self) -> str:
        return f"f99.section.{self.id}"


SECTIONS = [
    Section("status", "Status", "s", "[u]S[/u]tatus"),
    Section("lighting", "Lighting", "i", "L[u]i[/u]ghting"),
    Section("music", "Music", "u", "M[u]u[/u]sic"),
    Section("keys", "Keys", "e", "K[u]e[/u]ys"),
    Section("macros", "Macros", "a", "M[u]a[/u]cros"),
    Section("keybindings", "Keybindings", "b", "Key[u]b[/u]indings"),
    Section("settings", "Settings", "g", "Settin[u]g[/u]s"),
]

SECTIONS_BY_ID = {section.id: section for section in SECTIONS}


@dataclass(frozen=True)
class Action:
    id: str
    default_key: str
    description: str
    group: str


# Groups order the Keybindings screen. Section actions are generated from
# SECTIONS so a new section brings its hotkey along automatically.
ACTIONS = [
    *[
        Action(section.binding_id, section.hotkey, f"Go to {section.title}", "Sections")
        for section in SECTIONS
    ],
    Action("f99.nav.sidebar", "h", "Focus the sidebar", "Navigation"),
    Action("f99.nav.content", "l", "Focus the content pane", "Navigation"),
    Action("f99.nav.down", "j", "Next section (sidebar)", "Navigation"),
    Action("f99.nav.up", "k", "Previous section (sidebar)", "Navigation"),
    Action("f99.view.toggle_sidebar", "f", "Fold or unfold the sidebar", "View"),
    Action("f99.app.refresh", "r", "Refresh, and prove the live link", "Actions"),
    Action("f99.app.key_monitor", "m", "Open the key monitor", "Actions"),
    Action("f99.app.keybindings", "question_mark", "Open app keybindings", "Actions"),
    Action("f99.app.quit", "q", "Quit", "Actions"),
]

ACTIONS_BY_ID = {action.id: action for action in ACTIONS}

# Escape always leaves a mode, so it can never be claimed by an action.
UNBINDABLE_KEYS = frozenset({"escape", "tab", "shift+tab", "enter"})


def load_keymap(path: Path | None = None, warnings: list[str] | None = None) -> dict[str, str]:
    """Saved overrides, as binding id -> key. Unknown ids are dropped.

    An override that breaks a rebind rule -- a reserved key, or a key
    another action already holds -- is dropped too. The rebind screen
    enforces those rules on a live rebind, but a hand-edited file skips the
    screen entirely, so this is the only place left to catch it. Silently
    keeping a broken override is worse than the rules being pointless: it
    can strand the user on a key that no longer does what they expect (see
    docs/tui-spec.md#error-handling). Pass `warnings` to learn what was
    dropped and why.
    """
    path = path or tui_keymap_path()
    if not path.exists():
        return {}
    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
        entries = raw.get("keymap", {})
        candidate = {str(k): str(v) for k, v in entries.items() if str(k) in ACTIONS_BY_ID}
    except Exception as exc:
        raise ConfigLoadError(path, exc) from exc

    cleaned, problems = _sanitize_keymap(candidate)
    if warnings is not None:
        warnings.extend(problems)
    return cleaned


def _sanitize_keymap(candidate: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    cleaned: dict[str, str] = {}
    warnings: list[str] = []
    for action_id, key in candidate.items():
        action = ACTIONS_BY_ID[action_id]
        if key in UNBINDABLE_KEYS:
            warnings.append(f"{action.description}: {key!r} is reserved, ignoring this override")
            continue
        if not _is_known_key(key):
            warnings.append(f"{action.description}: {key!r} is not a recognised key, ignoring this override")
            continue
        clash = conflicting_action(key, cleaned, exclude_id=action_id)
        if clash is not None:
            warnings.append(
                f"{action.description}: {key!r} already used by {clash.description}, ignoring this override"
            )
            continue
        cleaned[action_id] = key
    return cleaned, warnings


def save_keymap(keymap: dict[str, str], path: Path | None = None) -> None:
    path = path or tui_keymap_path()
    atomic_write_toml(path, {"keymap": keymap})


def current_key(action: Action, keymap: dict[str, str]) -> str:
    return keymap.get(action.id, action.default_key)


def conflicting_action(key: str, keymap: dict[str, str], exclude_id: str) -> Action | None:
    """The action already using `key`, if any, ignoring `exclude_id`."""
    for action in ACTIONS:
        if action.id != exclude_id and current_key(action, keymap) == key:
            return action
    return None
