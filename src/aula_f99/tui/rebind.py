"""Modal that captures one key press, to rebind an action."""

from __future__ import annotations

from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from aula_f99.tui.actions import Action


class RebindScreen(ModalScreen[str | None]):
    """Dismisses with the captured key, or None when cancelled."""

    DEFAULT_CSS = """
    RebindScreen {
        align: center middle;
    }
    RebindScreen > Vertical {
        width: 60;
        height: auto;
        border: round $primary;
        padding: 1 2;
    }
    """

    def __init__(self, action: Action) -> None:
        super().__init__()
        self._action = action

    def compose(self) -> ComposeResult:
        with Vertical() as body:
            body.border_title = "Rebind"
            yield Static(
                f"Press the new key for [b]{self._action.description}[/b].\n\nEscape cancels.",
            )

    def on_key(self, event: events.Key) -> None:
        # Claim the key before any binding can act on it.
        event.stop()
        event.prevent_default()
        self.dismiss(None if event.key == "escape" else event.key)
