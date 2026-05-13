"""Tests for ColorRegistry."""

import pytest

from yasched.utilizing.coloring.Color import Color
from yasched.utilizing.coloring.ColorRegistry import ColorRegistry


@pytest.fixture
def reg() -> ColorRegistry:
    return ColorRegistry()


@pytest.fixture
def red() -> Color:
    return Color(r=1.0, g=0.0, b=0.0)


@pytest.fixture
def blue() -> Color:
    return Color(r=0.0, g=0.0, b=1.0)


@pytest.fixture
def green() -> Color:
    return Color(r=0.0, g=0.5, b=0.0)


# ---------------------------------------------------------------------------
# Initialization — CSS pre-loading
# ---------------------------------------------------------------------------


def test_css_red_preloaded(reg):
    c = reg.get_color("red")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_css_white_preloaded(reg):
    c = reg.get_color("white")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(1.0)
    assert c.b == pytest.approx(1.0)


def test_css_black_preloaded(reg):
    c = reg.get_color("black")
    assert c.r == pytest.approx(0.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_css_royalblue_preloaded(reg):
    assert reg.contains("royalblue")


def test_css_darkgreen_preloaded(reg):
    assert reg.contains("darkgreen")


def test_multiple_instances_are_independent(red):
    r1 = ColorRegistry()
    r2 = ColorRegistry()
    r1.register_color("custom", red)
    assert not r2.contains("custom")


# ---------------------------------------------------------------------------
# register_color — sweet path
# ---------------------------------------------------------------------------


def test_register_color_stores_value(reg, red):
    reg.register_color("myred", red)
    assert reg.get_color("myred") == red


def test_register_color_multiple(reg, red, blue):
    reg.register_color("myred", red)
    reg.register_color("myblue", blue)
    assert reg.get_color("myred") == red
    assert reg.get_color("myblue") == blue


# ---------------------------------------------------------------------------
# register_color — on_duplicate
# ---------------------------------------------------------------------------


def test_register_color_duplicate_raises_by_default(reg, red, blue):
    reg.register_color("custom", red)
    with pytest.raises(KeyError):
        reg.register_color("custom", blue)


def test_register_color_duplicate_replace(reg, red, blue):
    reg.register_color("custom", red)
    reg.register_color("custom", blue, on_duplicate="replace")
    assert reg.get_color("custom") == blue


def test_register_color_duplicate_ignore(reg, red, blue):
    reg.register_color("custom", red)
    reg.register_color("custom", blue, on_duplicate="ignore")
    assert reg.get_color("custom") == red


def test_register_color_invalid_on_duplicate_raises(reg, red):
    with pytest.raises(ValueError):
        reg.register_color("custom", red, on_duplicate="bad")


# ---------------------------------------------------------------------------
# CSS colors use on_duplicate="ignore" so user pre-registrations are kept
# ---------------------------------------------------------------------------


def test_user_color_not_overwritten_by_css_on_duplicate_ignore(red, blue):
    reg = ColorRegistry()
    custom_red = Color(r=0.9, g=0.1, b=0.1)
    reg.register_color("custom", custom_red)
    reg.register_color("custom", red, on_duplicate="ignore")
    assert reg.get_color("custom") == custom_red


# ---------------------------------------------------------------------------
# get_color — sweet path
# ---------------------------------------------------------------------------


def test_get_color_by_canonical_name(reg, red):
    reg.register_color("c", red)
    assert reg.get_color("c") == red


def test_get_color_by_alias(reg, blue):
    reg.register_color("primary", blue)
    reg.register_alias("primary", "main")
    assert reg.get_color("main") == blue


def test_get_color_css_name(reg):
    result = reg.get_color("blue")
    assert result.b == pytest.approx(1.0)
    assert result.r == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# get_color — failure cases
# ---------------------------------------------------------------------------


def test_get_color_unknown_raises(reg):
    with pytest.raises(KeyError):
        reg.get_color("notregistered")


def test_get_color_with_default_returns_default(reg, green):
    assert reg.get_color("notregistered", green) == green


def test_get_color_with_none_default(reg):
    assert reg.get_color("notregistered", None) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Inherited GenericRegistry methods still work
# ---------------------------------------------------------------------------


def test_contains_custom_color(reg, red):
    reg.register_color("c", red)
    assert reg.contains("c")


def test_len_includes_css_colors(reg):
    assert len(reg) > 100  # CSS has 140+ named colors


def test_canonical_keys_includes_css(reg):
    assert "red" in reg.canonical_keys()
    assert "blue" in reg.canonical_keys()


def test_remove_custom_color(reg, red):
    reg.register_color("custom", red)
    reg.remove("custom")
    assert not reg.contains("custom")


def test_register_alias_and_retrieve(reg):
    reg.register_alias("royalblue", "primary")
    assert reg.get_color("primary") == reg.get_color("royalblue")


def test_aliases_of_custom_color(reg, blue):
    reg.register_color("brand", blue)
    reg.register_alias("brand", "primary")
    assert "primary" in reg.aliases_of("brand")
