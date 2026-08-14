import asyncio
from collections.abc import Awaitable, Callable

from textual.widgets import ContentSwitcher, DataTable, ListView

from aula_f99.tui.actions import ACTIONS, ACTIONS_BY_ID, load_keymap
from aula_f99.tui.app import AulaF99App
from aula_f99.tui.app_keybindings import AppKeybindingsScreen
from aula_f99.tui.config_paths import ConfigPathsScreen
from aula_f99.tui.key_monitor import KeyMonitorScreen
from aula_f99.tui.main_screen import MainScreen, SectionList
from aula_f99.tui.panels import NotImplementedPanel
from aula_f99.tui.rebind import RebindScreen
from aula_f99.tui.settings_store import load_settings


def run_async(coro: Callable[[], Awaitable[None]], timeout: float = 5) -> None:
    asyncio.run(asyncio.wait_for(coro(), timeout=timeout))


async def _enter_key_monitor_then_quit() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("m")
        await pilot.pause()
        await pilot.press("q")
        await pilot.pause()


def test_quit_from_key_monitor_does_not_hang():
    run_async(_enter_key_monitor_then_quit)


async def _hotkey_switches_section() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("b")
        await pilot.pause()
        assert app.screen.query_one(ContentSwitcher).current == "keybindings"
        assert app.screen.query_one(SectionList).index == 5


def test_hotkey_switches_section():
    run_async(_hotkey_switches_section)


async def _unimplemented_section_shows_placeholder() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        panel = app.screen.query_one(ContentSwitcher).get_child_by_id("music")
        assert isinstance(panel, NotImplementedPanel)
        assert "not implemented yet" in str(panel.content)


def test_unimplemented_section_shows_placeholder():
    run_async(_unimplemented_section_shows_placeholder)


async def _key_monitor_opens_and_escape_returns() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("m")
        await pilot.pause()
        assert isinstance(app.screen, KeyMonitorScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainScreen)


def test_key_monitor_opens_and_escape_returns():
    run_async(_key_monitor_opens_and_escape_returns)


async def _refresh_probes_the_link_on_a_section_without_its_own_refresh() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("r")
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert app.screen.query_one(ContentSwitcher).current == "macros"
        assert app.sub_title == "active link: wired"


def test_refresh_probes_the_link_on_a_section_without_its_own_refresh(monkeypatch):
    monkeypatch.setattr("aula_f99.tui.main_screen.probe_active_link", lambda: "wired")
    run_async(_refresh_probes_the_link_on_a_section_without_its_own_refresh)


async def _sidebar_navigation_switches_content() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("h")
        await pilot.pause()
        await pilot.press("j")
        await pilot.pause()
        assert app.screen.query_one(ContentSwitcher).current == "lighting"


def test_sidebar_navigation_switches_content():
    run_async(_sidebar_navigation_switches_content)


async def _sidebar_folds_and_unfolds() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        sidebar = app.screen.query_one(SectionList)
        assert sidebar.display
        await pilot.press("f")
        await pilot.pause()
        assert not sidebar.display
        await pilot.press("f")
        await pilot.pause()
        assert sidebar.display


def test_sidebar_folds_and_unfolds():
    run_async(_sidebar_folds_and_unfolds)


async def _question_mark_opens_app_keybindings() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("question_mark")
        await pilot.pause()
        assert isinstance(app.screen, AppKeybindingsScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainScreen)


def test_question_mark_opens_app_keybindings():
    run_async(_question_mark_opens_app_keybindings)


async def _settings_opens_app_keybindings() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("g")  # Settings section
        await pilot.pause()
        settings_list = app.screen.query_one("#settings-list", ListView)
        settings_list.focus()
        await pilot.pause()
        settings_list.index = 0
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, AppKeybindingsScreen)


def test_settings_opens_app_keybindings():
    run_async(_settings_opens_app_keybindings)


async def _rebinding_takes_effect_and_persists() -> None:
    """Drives the whole path: table row -> rebind modal -> keymap -> live binding."""
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("question_mark")
        await pilot.pause()
        assert isinstance(app.screen, AppKeybindingsScreen)
        table = app.screen.query_one("#app-keys", DataTable)
        table.move_cursor(row=ACTIONS.index(ACTIONS_BY_ID["f99.app.key_monitor"]))
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, RebindScreen)
        await pilot.press("z")
        await pilot.pause()
        assert load_keymap() == {"f99.app.key_monitor": "z"}
        await pilot.press("escape")
        await pilot.pause()
        # The new key works, the old one no longer does.
        await pilot.press("m")
        await pilot.pause()
        assert isinstance(app.screen, MainScreen)
        await pilot.press("z")
        await pilot.pause()
        assert isinstance(app.screen, KeyMonitorScreen)


def test_rebinding_takes_effect_and_persists():
    run_async(_rebinding_takes_effect_and_persists)


async def _rebinding_rejects_a_key_already_in_use() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("question_mark")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, AppKeybindingsScreen)
        screen._apply(ACTIONS_BY_ID["f99.app.refresh"], "m")  # m is the key monitor
        await pilot.pause()
        assert load_keymap() == {}


def test_rebinding_rejects_a_key_already_in_use():
    run_async(_rebinding_rejects_a_key_already_in_use)


async def _rebinding_back_to_default_clears_the_override() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("question_mark")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, AppKeybindingsScreen)
        action = ACTIONS_BY_ID["f99.app.key_monitor"]
        screen._apply(action, "z")
        await pilot.pause()
        assert load_keymap() == {"f99.app.key_monitor": "z"}
        screen._apply(action, "m")
        await pilot.pause()
        assert load_keymap() == {}


def test_rebinding_back_to_default_clears_the_override():
    run_async(_rebinding_back_to_default_clears_the_override)


async def _settings_toggles_default_link_and_confirm_writes() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("g")  # Settings section
        await pilot.pause()
        settings_list = app.screen.query_one("#settings-list", ListView)
        settings_list.focus()
        await pilot.pause()

        settings_list.index = 2  # default-link
        await pilot.press("enter")
        await pilot.pause()
        assert load_settings().default_link == "wired"

        settings_list.index = 3  # confirm-writes
        await pilot.press("enter")
        await pilot.pause()
        assert load_settings().confirm_writes is False


def test_settings_toggles_default_link_and_confirm_writes():
    run_async(_settings_toggles_default_link_and_confirm_writes)


async def _settings_opens_config_paths() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("g")  # Settings section
        await pilot.pause()
        settings_list = app.screen.query_one("#settings-list", ListView)
        settings_list.focus()
        await pilot.pause()
        settings_list.index = 4  # config-paths
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfigPathsScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainScreen)


def test_settings_opens_config_paths():
    run_async(_settings_opens_config_paths)


async def _theme_choice_persists_across_launches() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        app.theme = "nord"
        await pilot.pause()

    assert load_settings().theme == "nord"

    reloaded = AulaF99App()
    async with reloaded.run_test() as pilot:
        assert reloaded.theme == "nord"
        await pilot.pause()


def test_theme_choice_persists_across_launches():
    run_async(_theme_choice_persists_across_launches)
