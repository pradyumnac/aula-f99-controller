"""Every rebindable TUI action, and the saved keymap that overrides it.

The registry here is the single source of truth for the sidebar, the
screen's bindings, and the Keybindings screen. Textual applies an override
by binding id, so a saved keymap needs no code change to take effect.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import tomli_w

from aula_f99.config import tui_keymap_path


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


def load_keymap(path: Path | None = None) -> dict[str, str]:
    """Saved overrides, as binding id -> key. Unknown ids are dropped."""
    path = path or tui_keymap_path()
    if not path.exists():
        return {}
    with path.open("rb") as f:
        raw = tomllib.load(f)
    entries = raw.get("keymap", {})
    return {str(k): str(v) for k, v in entries.items() if str(k) in ACTIONS_BY_ID}


def save_keymap(keymap: dict[str, str], path: Path | None = None) -> None:
    path = path or tui_keymap_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        tomli_w.dump({"keymap": keymap}, f)


def current_key(action: Action, keymap: dict[str, str]) -> str:
    return keymap.get(action.id, action.default_key)


def conflicting_action(key: str, keymap: dict[str, str], exclude_id: str) -> Action | None:
    """The action already using `key`, if any, ignoring `exclude_id`."""
    for action in ACTIONS:
        if action.id != exclude_id and current_key(action, keymap) == key:
            return action
    return None
