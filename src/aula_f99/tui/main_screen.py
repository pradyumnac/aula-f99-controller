"""The shell: sidebar, content switcher, header, footer."""

from __future__ import annotations

from collections.abc import Callable

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import ContentSwitcher, Footer, Header, Label, ListItem, ListView

from aula_f99.detect import detect_connection, probe_active_link
from aula_f99.tui.actions import SECTIONS, SECTIONS_BY_ID, Section
from aula_f99.tui.app_keybindings import AppKeybindingsScreen
from aula_f99.tui.key_monitor import KeyMonitorScreen
from aula_f99.tui.panels import (
    KeyboardKeybindingsPanel,
    NotImplementedPanel,
    Refreshable,
    SettingsPanel,
    StatusPanel,
)


def _panel_factory(section: Section) -> Callable[[], Widget]:
    if section.id == "status":
        return StatusPanel
    if section.id == "keybindings":
        return KeyboardKeybindingsPanel
    if section.id == "settings":
        return SettingsPanel
    return lambda: NotImplementedPanel(section.title)


class SectionList(ListView):
    """Sidebar list. Adds vim-style j/k alongside the default up/down."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", id="f99.nav.down"),
        Binding("k", "cursor_up", "Up", id="f99.nav.up"),
    ]


class ContentPane(Container):
    """Wraps the content switcher so it has something to focus onto."""

    can_focus = True


class MainScreen(Screen[None]):
    DEFAULT_CSS = """
    SectionList {
        width: 20;
        border: round $panel;
    }
    SectionList:focus {
        border: round $primary;
    }
    #content-pane {
        border: round $panel;
    }
    #content-pane:focus-within {
        border: round $primary;
    }
    """

    # Section hotkeys stay out of the footer -- the sidebar underlines each
    # mnemonic letter, and seven more entries would push the rest off an
    # 80-column footer. Alias keys carry no id, so a rebind cannot strand them.
    BINDINGS = [
        *[
            Binding(
                section.hotkey,
                f"select_section('{section.id}')",
                section.title,
                show=False,
                id=section.binding_id,
            )
            for section in SECTIONS
        ],
        Binding("h", "focus_sidebar", "Sidebar", id="f99.nav.sidebar"),
        Binding("left", "focus_sidebar", "Sidebar", show=False),
        Binding("l", "focus_content", "Content", id="f99.nav.content"),
        Binding("right,tab,shift+tab", "focus_content", "Content", show=False),
        Binding("f", "toggle_sidebar", "Fold", id="f99.view.toggle_sidebar"),
        Binding("r", "refresh", "Refresh", id="f99.app.refresh"),
        Binding("m", "key_monitor", "Monitor", id="f99.app.key_monitor"),
        Binding("question_mark", "app_keybindings", "Keys", id="f99.app.keybindings"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            sidebar = SectionList(
                *[ListItem(Label(section.label_markup), id=f"nav-{section.id}") for section in SECTIONS]
            )
            sidebar.border_title = "Sections"
            yield sidebar
            with ContentPane(id="content-pane"), ContentSwitcher(initial=SECTIONS[0].id):
                for section in SECTIONS:
                    panel = _panel_factory(section)()
                    panel.id = section.id
                    yield panel
        yield Footer()

    def on_mount(self) -> None:
        self._set_content_title(SECTIONS[0])
        self._refresh_header()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        # Lists inside a panel (Settings) bubble here too -- only the sidebar switches sections.
        if not isinstance(event.list_view, SectionList):
            return
        if event.item is None or event.item.id is None:
            return
        self._show_section(event.item.id.removeprefix("nav-"))

    def action_select_section(self, section_id: str) -> None:
        self.query_one(SectionList).index = SECTIONS.index(SECTIONS_BY_ID[section_id])
        self._show_section(section_id)

    def action_focus_sidebar(self) -> None:
        sidebar = self.query_one(SectionList)
        if sidebar.display:
            sidebar.focus()

    def action_focus_content(self) -> None:
        self.query_one(ContentPane).focus()

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one(SectionList)
        sidebar.display = not sidebar.display
        if not sidebar.display:
            self.action_focus_content()  # don't strand focus on a hidden pane
        else:
            sidebar.focus()

    def action_refresh(self) -> None:
        switcher = self.query_one(ContentSwitcher)
        if switcher.current is not None:
            panel = switcher.get_child_by_id(switcher.current)
            if isinstance(panel, Refreshable):
                panel.refresh_content()
        # Every section, refreshable or not, at least re-proves the live link.
        self.app.sub_title = "probing link -- press a media/volume key"
        self._probe_link()

    def action_key_monitor(self) -> None:
        self.app.push_screen(KeyMonitorScreen())

    def action_app_keybindings(self) -> None:
        self.app.push_screen(AppKeybindingsScreen())

    @work(thread=True, exclusive=True)
    def _probe_link(self) -> None:
        link = probe_active_link()
        self.app.call_from_thread(self._set_link, f"active link: {link}")

    def _set_link(self, text: str) -> None:
        self.app.sub_title = text

    def _show_section(self, section_id: str) -> None:
        self.query_one(ContentSwitcher).current = section_id
        self._set_content_title(SECTIONS_BY_ID[section_id])

    def _set_content_title(self, section: Section) -> None:
        self.query_one(ContentPane).border_title = section.title

    def _refresh_header(self) -> None:
        self.app.sub_title = detect_connection().guessed_mode
