# How to build screens with Textual

This page gives the rules this project follows when it builds terminal
screens. Apply them to every new screen.

For what the interface must contain, see [tui-spec.md](../tui-spec.md).

## Confirm the API first

Textual changes between versions. Do not trust memory of an API. Write a
short script, run it, and read the result. Then build on the API.

Keep such a script out of the repository.

## Layout and focus

| Rule | Detail |
| --- | --- |
| Set `can_focus` as a class attribute | The constructor rejects `can_focus`. Subclass the container, then set `can_focus = True`. |
| Give a container focus before you style focus | A container that cannot take focus never matches a focus rule. |
| Match a widget with `:focus` | The widget itself holds the focus. |
| Match a container with `:focus-within` | A child of the container holds the focus. |
| Put the rules in `DEFAULT_CSS` | The rules then stay with the widget that needs them. |
| Set `border_title` on the widget object | It is an attribute. The constructor does not accept it. |
| Take colour from a theme variable | Use `$panel` or `$primary`. Never write a colour value. |

## Content switching

Give every child of a `ContentSwitcher` an id. The switcher finds a child
by id, and raises `NoMatches` when the id is absent.

Switch the pane with `ContentSwitcher.current = "<child id>"`.

## Events

An event travels from the child widget up to the screen. A list inside a
panel sends the same message class as a list in the sidebar. The screen
receives both.

Check the sender before you act on an event:

```python
if not isinstance(event.list_view, SectionList):
    return
```

Call `event.stop()` to hold an event inside the panel that owns it.

## Key bindings

| Need | Use |
| --- | --- |
| A plain binding | A tuple: `("h", "focus_sidebar", "Sidebar")` |
| An id, or a hidden binding | A `Binding` object |
| One action, several keys | One binding: `"l,right,tab"` |

Keep the footer short. Set `show=False` on a binding the footer does not
need. The footer truncates at the width of the terminal.

Use the Textual name of a key. The name of `?` is `question_mark`. Call
`format_key()` to show a key name to the user.

## Rebinding

Give every rebindable binding an `id`.

Call `App.set_keymap()` at start. Call `App.update_keymap()` after a
change. A change applies at once. The user does not restart the program.

An override replaces the full key string of the binding. Put the primary
key in a binding with an id. Put the alias keys in a second binding with
no id. An alias then survives a rebind.

Do not build a key list from `Screen.active_bindings`. It holds framework
bindings, and it holds only the bindings of the widgets that have focus.
Keep a registry of your own instead.

## Modals

Use `ModalScreen` for a screen that covers the main screen.

Return a result with `dismiss(value)`. Read the result in the callback of
`push_screen()`.

To capture one raw key press, handle `on_key`. Call `event.stop()` and
`event.prevent_default()` first. The bindings then cannot claim the key.

## Workers and threads

Run every device read in a thread worker. Mark it `@work(thread=True)`.

Change the interface only through `call_from_thread()`.

Give a long worker a `threading.Event`. Set the event in `on_unmount()`.

A report can arrive while the program closes. Check the stop event first.
Then suppress `RuntimeError` around `call_from_thread()`.

Textual does not wait for a thread worker when the program quits.

## Tests

`pytest-asyncio` is not a dependency. Wrap each test:

```python
asyncio.run(asyncio.wait_for(coro(), timeout=5))
```

| Task | Method |
| --- | --- |
| Drive the app | `async with app.run_test() as pilot:` |
| Send a key | `await pilot.press("r")` |
| Let the app settle | `await pilot.pause()` |
| Wait for a worker | `await app.workers.wait_for_complete()` |
| Read the text of a `Static` | `.content` |

An exception in a handler fails the test. Trust that signal.

Replace a device call with `monkeypatch`. A real read blocks for seconds.

Point `XDG_CONFIG_HOME` at a temporary directory. A test must never write
to the config directory of the user.

## Check the layout

Render the screen to text with
`app.screen._compositor.render_strips()`.

Write the text to a UTF-8 file. `print()` fails on the Windows console.

Check every layout at 80 columns by 24 rows.
