"""Tests for XymlKeyRegistry."""

import pytest

from yasched.utilizing.xyml.XymlKeyBehavior import XymlKeyBehavior
from yasched.utilizing.xyml.XymlKeyRegistry import XymlKeyRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    XymlKeyRegistry._reset_instance()
    yield
    XymlKeyRegistry._reset_instance()


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


def test_get_instance_returns_registry():
    assert isinstance(XymlKeyRegistry.get_instance(), XymlKeyRegistry)


def test_get_instance_returns_same_object():
    a = XymlKeyRegistry.get_instance()
    b = XymlKeyRegistry.get_instance()
    assert a is b


# ---------------------------------------------------------------------------
# Pre-registered keys
# ---------------------------------------------------------------------------


def test_file_key_is_registered():
    reg = XymlKeyRegistry.get_instance()
    assert reg.is_directive("__file__")


def test_ext_key_is_registered():
    reg = XymlKeyRegistry.get_instance()
    assert reg.is_directive("__ext__")


def test_file_key_has_replace_behavior():
    reg = XymlKeyRegistry.get_instance()
    assert reg.get_behavior("__file__") is XymlKeyBehavior.REPLACE


def test_ext_key_has_extend_behavior():
    reg = XymlKeyRegistry.get_instance()
    assert reg.get_behavior("__ext__") is XymlKeyBehavior.EXTEND


# ---------------------------------------------------------------------------
# is_directive
# ---------------------------------------------------------------------------


def test_is_directive_true_for_registered_key():
    reg = XymlKeyRegistry.get_instance()
    assert reg.is_directive("__file__") is True


def test_is_directive_false_for_unknown_key():
    reg = XymlKeyRegistry.get_instance()
    assert reg.is_directive("title") is False


def test_is_directive_false_for_empty_string():
    reg = XymlKeyRegistry.get_instance()
    assert reg.is_directive("") is False


# ---------------------------------------------------------------------------
# get_behavior
# ---------------------------------------------------------------------------


def test_get_behavior_returns_none_for_unknown_key():
    reg = XymlKeyRegistry.get_instance()
    assert reg.get_behavior("nope") is None


def test_get_behavior_never_raises_for_unknown_key():
    reg = XymlKeyRegistry.get_instance()
    result = reg.get_behavior("whatever")
    assert result is None


# ---------------------------------------------------------------------------
# register_key
# ---------------------------------------------------------------------------


def test_register_key_custom_replace():
    reg = XymlKeyRegistry.get_instance()
    reg.register_key("__include__", XymlKeyBehavior.REPLACE)
    assert reg.is_directive("__include__")
    assert reg.get_behavior("__include__") is XymlKeyBehavior.REPLACE


def test_register_key_custom_extend():
    reg = XymlKeyRegistry.get_instance()
    reg.register_key("__merge__", XymlKeyBehavior.EXTEND)
    assert reg.get_behavior("__merge__") is XymlKeyBehavior.EXTEND


def test_register_key_duplicate_raises_by_default():
    reg = XymlKeyRegistry.get_instance()
    with pytest.raises(KeyError):
        reg.register_key("__file__", XymlKeyBehavior.EXTEND)


def test_register_key_duplicate_replace():
    reg = XymlKeyRegistry.get_instance()
    reg.register_key("__file__", XymlKeyBehavior.EXTEND, on_duplicate="replace")
    assert reg.get_behavior("__file__") is XymlKeyBehavior.EXTEND


def test_register_key_duplicate_ignore_keeps_original():
    reg = XymlKeyRegistry.get_instance()
    reg.register_key("__file__", XymlKeyBehavior.EXTEND, on_duplicate="ignore")
    assert reg.get_behavior("__file__") is XymlKeyBehavior.REPLACE


def test_register_key_invalid_behavior_raises_type_error():
    reg = XymlKeyRegistry.get_instance()
    with pytest.raises(TypeError):
        reg.register_key("__bad__", "REPLACE")  # type: ignore[arg-type]


def test_register_key_invalid_behavior_int_raises_type_error():
    reg = XymlKeyRegistry.get_instance()
    with pytest.raises(TypeError):
        reg.register_key("__bad__", 1)  # type: ignore[arg-type]
