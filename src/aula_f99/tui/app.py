"""TUI entry point. See main_screen.py for the shell layout."""

from __future__ import annotations

from dataclasses import replace

from textual.app import App
from textual.binding import Binding

from aula_f99.tui.actions import load_keymap
from aula_f99.tui.main_screen import MainScreen
from aula_f99.tui.settings_store import AppSettings, load_settings, save_settings


class AulaF99App(App[None]):
    TITLE = "aula-f99-controller"
    BINDINGS = [Binding("q", "quit", "Quit", id="f99.app.quit")]

    def on_mount(self) -> None:
        self._settings: AppSettings | None = None
        settings = load_settings()
        if settings.theme not in self.available_themes:
            settings = replace(settings, theme=AppSettings().theme)
        self.theme = settings.theme
        self._settings = settings
        self.set_keymap(load_keymap())
        self.push_screen(MainScreen())

    def watch_theme(self, theme: str) -> None:
        # Fires once on the initial `on_mount` assignment too -- harmless, it
        # just re-saves the value that was just loaded from disk.
        if self._settings is None or theme == self._settings.theme:
            return
        self._settings = replace(self._settings, theme=theme)
        save_settings(self._settings)


def main() -> None:
    AulaF99App().run()


if __name__ == "__main__":
    main()
