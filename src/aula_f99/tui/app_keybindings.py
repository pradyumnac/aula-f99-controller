"""App keybindings: this project's own bindings, and the screen to edit them.

Distinct from the Keybindings section in the sidebar, which lists the
keyboard's factory FN shortcuts. These are the keys the TUI itself uses.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.keys import format_key
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from aula_f99.errors import ConfigLoadError
from aula_f99.tui.actions import (
    ACTIONS,
    ACTIONS_BY_ID,
    UNBINDABLE_KEYS,
    Action,
    conflicting_action,
    current_key,
    load_keymap,
    save_keymap,
)
from aula_f99.tui.rebind import RebindScreen


class AppKeybindingsScreen(Screen[None]):
    """Lists every app binding. Enter rebinds the selected row."""

    BINDINGS = [("escape", "back", "Back")]

    DEFAULT_CSS = """
    AppKeybindingsScreen #app-keys-body {
        border: round $primary;
        padding: 0 1;
    }
    AppKeybindingsScreen DataTable {
        height: 1fr;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._keymap: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="app-keys-body") as body:
            body.border_title = "App keybindings"
            yield Static("Enter rebinds the selected row. Escape goes back.", id="app-keys-hint")
            yield DataTable[str](id="app-keys", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#app-keys", DataTable)
        table.add_columns("Key", "Action", "Group")
        self.reload()
        table.focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    def reload(self) -> None:
        try:
            self._keymap = load_keymap()
        except ConfigLoadError as exc:
            self._keymap = {}
            self.notify(str(exc), title="Keybindings file ignored", severity="warning", timeout=8)
        table = self.query_one("#app-keys", DataTable)
        cursor = table.cursor_row
        table.clear()
        for action in ACTIONS:
            table.add_row(
                format_key(current_key(action, self._keymap)),
                action.description,
                action.group,
                key=action.id,
            )
        if 0 < cursor < table.row_count:
            table.move_cursor(row=cursor)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key.value is None:
            return
        action = ACTIONS_BY_ID.get(event.row_key.value)
        if action is not None:
            self.app.push_screen(RebindScreen(action), lambda key: self._apply(action, key))

    def _apply(self, action: Action, key: str | None) -> None:
        if key is None:
            return
        if key in UNBINDABLE_KEYS:
            self.notify(f"{format_key(key)} is reserved and cannot be rebound.", severity="error")
            return
        clash = conflicting_action(key, self._keymap, exclude_id=action.id)
        if clash is not None:
            self.notify(f"{format_key(key)} is already bound to {clash.description}.", severity="error")
            return

        keymap = dict(self._keymap)
        if key == action.default_key:
            keymap.pop(action.id, None)  # back to default -- don't persist a no-op
        else:
            keymap[action.id] = key
        try:
            save_keymap(keymap)
        except OSError as exc:
            self.notify(f"Could not save keybindings: {exc}", title="Rebind not saved", severity="error")
            return
        self.app.update_keymap(keymap)
        self.reload()
        self.notify(f"{action.description} is now {format_key(key)}.")
