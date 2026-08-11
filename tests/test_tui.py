import asyncio

from aula_f99.tui.app import AulaF99App


async def _enter_listener_then_quit() -> None:
    app = AulaF99App()
    async with app.run_test() as pilot:
        await pilot.press("t")
        await pilot.pause()
        await pilot.press("q")
        await pilot.pause()


def test_quit_from_listener_screen_does_not_hang():
    asyncio.run(asyncio.wait_for(_enter_listener_then_quit(), timeout=5))
