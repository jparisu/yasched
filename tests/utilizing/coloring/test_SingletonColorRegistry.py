"""Tests for SingletonColorRegistry."""

import threading

import pytest

from yasched.utilizing.coloring.Color import Color
from yasched.utilizing.coloring.ColorRegistry import ColorRegistry
from yasched.utilizing.coloring.SingletonColorRegistry import SingletonColorRegistry


@pytest.fixture(autouse=True)
def reset_singleton():
    SingletonColorRegistry._reset_instance()
    yield
    SingletonColorRegistry._reset_instance()


@pytest.fixture
def red() -> Color:
    return Color(r=1.0, g=0.0, b=0.0)


# ---------------------------------------------------------------------------
# Singleton contract
# ---------------------------------------------------------------------------


def test_get_instance_returns_singleton_color_registry():
    instance = SingletonColorRegistry.get_instance()
    assert isinstance(instance, SingletonColorRegistry)
    assert isinstance(instance, ColorRegistry)


def test_get_instance_same_object_on_repeated_calls():
    a = SingletonColorRegistry.get_instance()
    b = SingletonColorRegistry.get_instance()
    assert a is b


def test_get_instance_thread_safe():
    results: list[SingletonColorRegistry] = []

    def worker():
        results.append(SingletonColorRegistry.get_instance())

    threads = [threading.Thread(target=worker) for _ in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r is results[0] for r in results)


# ---------------------------------------------------------------------------
# CSS pre-loading happens once on first instantiation
# ---------------------------------------------------------------------------


def test_css_colors_available_on_first_get_instance():
    inst = SingletonColorRegistry.get_instance()
    assert inst.contains("red")
    assert inst.contains("blue")
    assert inst.contains("white")


def test_css_colors_available_on_subsequent_calls():
    SingletonColorRegistry.get_instance()
    inst = SingletonColorRegistry.get_instance()
    assert inst.contains("royalblue")


# ---------------------------------------------------------------------------
# Mutations are shared across all references
# ---------------------------------------------------------------------------


def test_registered_color_visible_from_all_references(red):
    inst1 = SingletonColorRegistry.get_instance()
    inst1.register_color("brand", red)
    inst2 = SingletonColorRegistry.get_instance()
    assert inst2.get_color("brand") == red


def test_alias_visible_from_all_references():
    inst = SingletonColorRegistry.get_instance()
    inst.register_alias("red", "primary")
    assert SingletonColorRegistry.get_instance().get_color("primary").r == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# _reset_instance
# ---------------------------------------------------------------------------


def test_reset_clears_singleton():
    first = SingletonColorRegistry.get_instance()
    SingletonColorRegistry._reset_instance()
    second = SingletonColorRegistry.get_instance()
    assert first is not second


def test_after_reset_css_colors_reloaded():
    inst = SingletonColorRegistry.get_instance()
    inst.remove("red")
    SingletonColorRegistry._reset_instance()
    assert SingletonColorRegistry.get_instance().contains("red")


def test_after_reset_custom_colors_are_gone(red):
    SingletonColorRegistry.get_instance().register_color("custom", red)
    SingletonColorRegistry._reset_instance()
    assert not SingletonColorRegistry.get_instance().contains("custom")


# ---------------------------------------------------------------------------
# Isolation from plain ColorRegistry instances
# ---------------------------------------------------------------------------


def test_singleton_does_not_share_state_with_plain_registry(red):
    plain = ColorRegistry()
    plain.register_color("isolated", red)
    singleton = SingletonColorRegistry.get_instance()
    assert not singleton.contains("isolated")


def test_singleton_mutations_do_not_affect_plain_registry(red):
    singleton = SingletonColorRegistry.get_instance()
    singleton.register_color("global_brand", red)
    plain = ColorRegistry()
    assert not plain.contains("global_brand")
