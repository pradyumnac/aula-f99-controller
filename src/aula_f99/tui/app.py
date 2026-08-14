"""TUI entry point. See main_screen.py for the shell layout."""

from __future__ import annotations

from dataclasses import replace

from textual.app import App
from textual.binding import Binding

from aula_f99.errors import ConfigLoadError
from aula_f99.tui.actions import load_keymap
from aula_f99.tui.main_screen import MainScreen
from aula_f99.tui.settings_store import AppSettings, load_settings, save_settings


class AulaF99App(App[None]):
    TITLE = "aula-f99-controller"
    BINDINGS = [Binding("q", "quit", "Quit", id="f99.app.quit")]

    def on_mount(self) -> None:
        self._settings: AppSettings | None = None

        settings, settings_error = self._load_settings_safely()
        if settings.theme not in self.available_themes:
            settings = replace(settings, theme=AppSettings().theme)
        self.theme = settings.theme
        self._settings = settings

        keymap, keymap_error, keymap_warnings = self._load_keymap_safely()
        self.set_keymap(keymap)

        self.push_screen(MainScreen())

        # Notify after the screen is up -- a broken config file falls back
        # to defaults rather than blocking launch, but the user still needs
        # to know their edit was ignored and why.
        for error in (settings_error, keymap_error):
            if error is not None:
                self.notify(str(error), title="Config file ignored", severity="warning", timeout=8)
        for warning in keymap_warnings:
            self.notify(warning, title="Keybinding override ignored", severity="warning", timeout=8)

    @staticmethod
    def _load_settings_safely() -> tuple[AppSettings, ConfigLoadError | None]:
        try:
            return load_settings(), None
        except ConfigLoadError as exc:
            return AppSettings(), exc

    @staticmethod
    def _load_keymap_safely() -> tuple[dict[str, str], ConfigLoadError | None, list[str]]:
        warnings: list[str] = []
        try:
            return load_keymap(warnings=warnings), None, warnings
        except ConfigLoadError as exc:
            return {}, exc, []

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
