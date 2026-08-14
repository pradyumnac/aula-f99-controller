import pytest

from aula_f99 import config
from aula_f99.errors import ConfigLoadError
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


def test_load_keymap_invalid_toml_raises_config_load_error(tmp_path):
    path = tmp_path / "tui_keymap.toml"
    path.write_text("not valid toml [[[")
    with pytest.raises(ConfigLoadError) as excinfo:
        load_keymap(path)
    assert excinfo.value.path == path


def test_load_keymap_drops_a_reserved_key_and_warns():
    save_keymap({"f99.app.quit": "escape"})
    warnings: list[str] = []
    assert load_keymap(warnings=warnings) == {}
    assert len(warnings) == 1
    assert "escape" in warnings[0] and "reserved" in warnings[0]


def test_load_keymap_drops_an_unrecognised_key_and_warns():
    # A hand edit, not something a live rebind (which captures a real key
    # press) could ever produce -- without this check it would silently
    # strand the action on a key that will never fire.
    save_keymap({"f99.app.quit": "notarealkey"})
    warnings: list[str] = []
    assert load_keymap(warnings=warnings) == {}
    assert len(warnings) == 1
    assert "notarealkey" in warnings[0]


def test_load_keymap_drops_a_key_that_clashes_with_another_actions_default():
    # "m" is the key monitor's default key -- binding quit to it too would
    # silently steal the key monitor's binding.
    save_keymap({"f99.app.quit": "m"})
    warnings: list[str] = []
    assert load_keymap(warnings=warnings) == {}
    assert len(warnings) == 1
    assert "m" in warnings[0] and "key monitor" in warnings[0].lower()


def test_load_keymap_keeps_valid_overrides_alongside_a_dropped_one():
    save_keymap({"f99.app.quit": "notarealkey", "f99.app.refresh": "z"})
    warnings: list[str] = []
    assert load_keymap(warnings=warnings) == {"f99.app.refresh": "z"}
    assert len(warnings) == 1


def test_load_keymap_without_warnings_param_still_sanitizes():
    save_keymap({"f99.app.quit": "escape"})
    assert load_keymap() == {}


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
