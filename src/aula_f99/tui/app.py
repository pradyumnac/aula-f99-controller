"""TUI shell. Each keyboard feature gets its own vertical slice/screen here."""

from __future__ import annotations

import threading

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from aula_f99.detect import detect_connection, stream_consumer_events
from aula_f99.usage_codes import format_event


class ConnectionStatusWidget(Static):
    def on_mount(self) -> None:
        self.refresh_status()

    def refresh_status(self) -> None:
        status = detect_connection()
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
            "Press 't' to enter key-press listener mode.",
        ]
        self.update("\n".join(lines))


class MainScreen(Screen[None]):
    BINDINGS = [
        ("r", "refresh", "Refresh enumeration"),
        ("t", "listen", "Key-press listener"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield ConnectionStatusWidget(id="connection-status")
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(ConnectionStatusWidget).refresh_status()

    def action_listen(self) -> None:
        self.app.push_screen(ListenerScreen())


class ListenerScreen(Screen[None]):
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
            text = format_event(raw)
            if text is None:
                return  # release/no-op report -- don't double-notify
            self.app.call_from_thread(
                self.app.notify,
                f"[{link}] {text}",
                title="Key detected",
                timeout=1,
            )

        stream_consumer_events(stop_event, on_event)


class AulaF99App(App[None]):
    TITLE = "aula-f99-controller"
    BINDINGS = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())


def main() -> None:
    AulaF99App().run()


if __name__ == "__main__":
    main()
