from aula_f99 import config
from aula_f99.tui.actions import (
    ACTIONS,
    ACTIONS_BY_ID,
    SECTIONS,
    Action,
    conflicting_action,
    current_key,
    load_keymap,
    save_keymap,
)


def test_keymap_path_follows_xdg(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert config.tui_keymap_path() == tmp_path / "aula-f99" / "tui_keymap.toml"


def test_keymap_round_trip():
    assert load_keymap() == {}
    save_keymap({"f99.app.refresh": "z"})
    assert load_keymap() == {"f99.app.refresh": "z"}


def test_load_keymap_drops_unknown_ids():
    save_keymap({"f99.app.refresh": "z", "not.a.real.action": "y"})
    assert load_keymap() == {"f99.app.refresh": "z"}


def test_current_key_prefers_the_override():
    action = ACTIONS_BY_ID["f99.app.refresh"]
    assert current_key(action, {}) == "r"
    assert current_key(action, {"f99.app.refresh": "z"}) == "z"


def test_conflicting_action_finds_the_holder():
    clash = conflicting_action("m", {}, exclude_id="f99.app.refresh")
    assert clash is not None
    assert clash.id == "f99.app.key_monitor"


def test_conflicting_action_ignores_the_excluded_action():
    assert conflicting_action("r", {}, exclude_id="f99.app.refresh") is None


def test_conflicting_action_respects_overrides():
    keymap = {"f99.app.key_monitor": "z"}
    assert conflicting_action("m", keymap, exclude_id="f99.app.refresh") is None
    clash = conflicting_action("z", keymap, exclude_id="f99.app.refresh")
    assert clash is not None
    assert clash.id == "f99.app.key_monitor"


def test_default_keys_do_not_collide():
    keys = [action.default_key for action in ACTIONS]
    assert len(keys) == len(set(keys))


def test_every_section_has_an_action():
    ids = {action.id for action in ACTIONS}
    for section in SECTIONS:
        assert section.binding_id in ids


def test_actions_are_unique_by_id():
    assert len(ACTIONS) == len(ACTIONS_BY_ID)


def test_action_is_hashable_and_frozen():
    action = Action("x", "y", "desc", "group")
    assert action == Action("x", "y", "desc", "group")
