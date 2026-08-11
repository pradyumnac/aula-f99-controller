# Unresolved issues

This page tracks known bugs and gaps that are not fixed yet. Each row
states the issue, where it lives, and why it is still open. When an issue
is fixed, remove its row -- do not mark it "fixed" here.

| Issue | Location | Why open |
| --- | --- | --- |
| `record_unknown_code()` does an unlocked read-modify-write on the config file. Two processes reading the same file at once can lose one process's update. | [`keybindings.py`](../src/aula_f99/keybindings.py) | Safe today: one process, one listener thread. Needs a lock or an append-only write strategy before a second concurrent listener is possible. |
| `format_event()` reads and parses the config file up to three times per key event. | [`usage_codes.py`](../src/aula_f99/usage_codes.py) | Not a real cost at human keypress rates. Fix by threading one `load_keybindings()` result through the call instead of three separate loads. |
