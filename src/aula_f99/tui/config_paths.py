"""Read-only display of where this project's config and data files live."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from aula_f99.config import config_dir, data_dir, settings_path, tui_keymap_path


class ConfigPathsScreen(Screen[None]):
    """Lists the XDG directories and files this project writes."""

    BINDINGS = [("escape", "back", "Back")]

    DEFAULT_CSS = """
    ConfigPathsScreen #config-paths-body {
        border: round $primary;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="config-paths-body") as body:
            body.border_title = "Config paths"
            yield Static(self._format_paths())
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()

    def _format_paths(self) -> str:
        return "\n".join(
            [
                f"[b]Config directory[/b]  {config_dir()}",
                f"[b]Data directory[/b]    {data_dir()}",
                "",
                f"[b]App keybindings[/b]   {tui_keymap_path()}",
                f"[b]App settings[/b]      {settings_path()}",
            ]
        )
