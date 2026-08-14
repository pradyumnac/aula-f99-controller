"""Content-pane widgets for the shell's sections."""

from __future__ import annotations

from dataclasses import replace
from typing import Protocol, runtime_checkable

from textual.app import ComposeResult
from textual.widgets import DataTable, Label, ListItem, ListView, Static

from aula_f99.detect import detect_connection
from aula_f99.errors import ConfigLoadError
from aula_f99.keybindings import load_keybindings
from aula_f99.tui.app_keybindings import AppKeybindingsScreen
from aula_f99.tui.config_paths import ConfigPathsScreen
from aula_f99.tui.settings_store import LINK_MODES, AppSettings, load_settings, save_settings


@runtime_checkable
class Refreshable(Protocol):
    """A panel that can re-fetch its own content on demand (the `r` binding)."""

    def refresh_content(self) -> None: ...


class NotImplementedPanel(Static):
    def __init__(self, title: str) -> None:
        super().__init__(f"{title} is not implemented yet.\n\nSee docs/tui-spec.md for the plan.")


class StatusPanel(Static):
    def on_mount(self) -> None:
        self.refresh_content()

    def refresh_content(self) -> None:
        try:
            status = detect_connection()
        except OSError as exc:
            self.update(f"[b]Connection check failed:[/b] {exc}\n\nPress 'r' to try again.")
            return
        lines = [
            f"[b]Enumeration guess:[/b] {status.guessed_mode}",
            "",
            f"[b]Wired[/b] (VID_258A:PID_010C): "
            f"{'present' if status.wired_present else 'not present'}"
            + (f" -- {status.wired_product!r}" if status.wired_product else ""),
            f"[b]Wireless dongle[/b] (VID_3554:PID_FA09): "
            f"{'present' if status.wireless_dongle_present else 'not present'}"
            + (f" -- {status.wireless_product!r}" if status.wireless_product else ""),
            "",
            "Press 'r' to prove the live link, or 'm' to open the key monitor.",
        ]
        self.update("\n".join(lines))


class KeyboardKeybindingsPanel(Static):
    """The keyboard's factory FN shortcuts. Reference text, not editable.

    The TUI's own bindings live under Settings; see AppKeybindingsScreen.
    """

    DEFAULT_CSS = """
    KeyboardKeybindingsPanel {
        height: 1fr;
    }
    KeyboardKeybindingsPanel #kbd-hint {
        height: auto;
        padding: 0 0 1 0;
    }
    KeyboardKeybindingsPanel DataTable {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(
            "The keyboard's own FN shortcuts. The firmware handles these.\nFor this app's keys, press '?'.",
            id="kbd-hint",
        )
        yield DataTable[str](id="kbd-keys", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#kbd-keys", DataTable)
        table.add_columns("Shortcut", "Effect", "Category")
        try:
            shortcuts = load_keybindings()
        except ConfigLoadError as exc:
            self.notify(str(exc), title="Keybindings file ignored", severity="warning", timeout=8)
            return
        for shortcut in shortcuts:
            if shortcut.shortcut:
                table.add_row(shortcut.shortcut, shortcut.effect, shortcut.category)


class SettingsPanel(Static):
    """Navigable list of settings panes."""

    DEFAULT_CSS = """
    SettingsPanel {
        height: 1fr;
    }
    SettingsPanel #settings-hint {
        height: auto;
        padding: 0 0 1 0;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        try:
            self._settings = load_settings()
        except ConfigLoadError:
            # The app already warned about this file during startup, and
            # fell back to the same defaults -- don't tell the user twice.
            self._settings = AppSettings()

    def compose(self) -> ComposeResult:
        yield Static("Enter opens or toggles the selected setting.", id="settings-hint")
        yield ListView(
            *[ListItem(Label(""), id=f"set-{entry_id}") for entry_id, _, _ in self._entries()],
            id="settings-list",
        )

    def on_mount(self) -> None:
        self._reload()

    def refresh_content(self) -> None:
        self._reload()

    def _entries(self) -> list[tuple[str, str, str]]:
        settings = self._settings
        return [
            ("app-keybindings", "App keybindings", "Rebind this app's keys."),
            ("theme", "Theme", f"{self.app.theme} -- Enter opens the theme picker."),
            ("default-link", "Default link", f"{settings.default_link} -- Enter toggles."),
            (
                "confirm-writes",
                "Confirm before write",
                f"{'on' if settings.confirm_writes else 'off'} -- Enter toggles.",
            ),
            ("config-paths", "Config paths", "Read-only. Enter to view."),
        ]

    def _reload(self) -> None:
        # Update each row's label in place -- the rows themselves never change,
        # only their text, so there's no need to clear and rebuild the list
        # (which would also drop the cursor position).
        for entry_id, title, note in self._entries():
            self.query_one(f"#set-{entry_id} Label", Label).update(f"{title} -- {note}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item is None or event.item.id is None:
            return
        event.stop()  # don't let the sidebar's handler see this
        entry_id = event.item.id.removeprefix("set-")
        if entry_id == "app-keybindings":
            self.app.push_screen(AppKeybindingsScreen())
        elif entry_id == "theme":
            self.app.action_change_theme()
        elif entry_id == "default-link":
            self._toggle_default_link()
        elif entry_id == "confirm-writes":
            self._toggle_confirm_writes()
        elif entry_id == "config-paths":
            self.app.push_screen(ConfigPathsScreen())

    def _toggle_default_link(self) -> None:
        other = LINK_MODES[1 - LINK_MODES.index(self._settings.default_link)]
        self._save(replace(self._settings, default_link=other), f"Default link is now {other}.")

    def _toggle_confirm_writes(self) -> None:
        new_value = not self._settings.confirm_writes
        self._save(
            replace(self._settings, confirm_writes=new_value),
            f"Confirm before write is now {'on' if new_value else 'off'}.",
        )

    def _save(self, settings: AppSettings, success_message: str) -> None:
        try:
            save_settings(settings)
        except OSError as exc:
            self.notify(f"Could not save settings: {exc}", title="Settings not saved", severity="error")
            return
        self._settings = settings
        self._reload()
        self.notify(success_message)
