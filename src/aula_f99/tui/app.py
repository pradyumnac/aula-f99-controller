"""TUI entry point. See main_screen.py for the shell layout."""

from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from aula_f99.tui.actions import load_keymap
from aula_f99.tui.main_screen import MainScreen


class AulaF99App(App[None]):
    TITLE = "aula-f99-controller"
    BINDINGS = [Binding("q", "quit", "Quit", id="f99.app.quit")]

    def on_mount(self) -> None:
        self.theme = "textual-dark"
        self.set_keymap(load_keymap())
        self.push_screen(MainScreen())


def main() -> None:
    AulaF99App().run()


if __name__ == "__main__":
    main()
