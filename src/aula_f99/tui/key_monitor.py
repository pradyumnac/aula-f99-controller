"""Key monitor modal: streams media/volume key presses as notifications."""

from __future__ import annotations

import contextlib
import threading

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Static

from aula_f99.detect import stream_consumer_events
from aula_f99.usage_codes import format_event


class KeyMonitorScreen(ModalScreen[None]):
    """Streams consumer-control key presses as toasts until Escape."""

    BINDINGS = [("escape", "back", "Back to main screen")]

    def __init__(self) -> None:
        super().__init__()
        self._stop_event = threading.Event()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static(
                "Listening for media/volume key presses (no time limit).\n"
                "Each press pops a notification. Press Escape to return to the main screen.",
                id="listener-status",
            )
        yield Footer()

    def on_mount(self) -> None:
        self._run_stream(self._stop_event)

    def on_unmount(self) -> None:
        self._stop_event.set()

    def action_back(self) -> None:
        self.app.pop_screen()

    @work(thread=True)
    def _run_stream(self, stop_event: threading.Event) -> None:
        def on_event(link: str, raw: bytes) -> None:
            if stop_event.is_set():
                return
            try:
                text = format_event(raw)
            except Exception as exc:
                # format_event reads (and can rewrite) the keybindings file
                # on every press -- a bad file must not kill the listener
                # thread, since that would silently stop all future reports.
                text = f"could not read this key press: {exc}"
            if text is None:
                return  # release/no-op report -- don't double-notify
            # A report can land while the app is tearing down; the loop
            # only stops between reads, so the target may already be gone.
            with contextlib.suppress(RuntimeError):
                self.app.call_from_thread(
                    self.app.notify,
                    f"[{link}] {text}",
                    title="Key detected",
                    timeout=1,
                )

        stream_consumer_events(stop_event, on_event)
