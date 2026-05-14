"""Tests for coring.Layout: BackgroundStyle, BorderStyle, IconStyle, Layout."""

import pytest

from yasched.coring.Layout import BackgroundStyle, BorderStyle, IconStyle, Layout
from yasched.utilizing.coloring.Color import Color

_RED = Color(r=1.0, g=0.0, b=0.0)
_BLUE = Color(r=0.0, g=0.0, b=1.0)


# ---------------------------------------------------------------------------
# BackgroundStyle — sweet path
# ---------------------------------------------------------------------------


def test_background_solid_type():
    bg = BackgroundStyle(type="solid", color=_RED)
    assert bg.type == "solid"
    assert bg.color == _RED
    assert bg.colors is None


def test_background_gradient_type():
    bg = BackgroundStyle(type="gradient", colors=[_RED, _BLUE])
    assert bg.type == "gradient"
    assert bg.colors == [_RED, _BLUE]
    assert bg.color is None


def test_background_all_none_is_valid():
    bg = BackgroundStyle(type="solid")
    assert bg.color is None
    assert bg.colors is None


def test_background_is_frozen():
    bg = BackgroundStyle(type="solid", color=_RED)
    with pytest.raises((AttributeError, TypeError)):
        bg.type = "gradient"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# BackgroundStyle — corner cases
# ---------------------------------------------------------------------------


def test_background_unknown_type_stored_as_is():
    # coring stores data; backending validates type values
    bg = BackgroundStyle(type="radial")
    assert bg.type == "radial"


def test_background_empty_gradient_list():
    bg = BackgroundStyle(type="gradient", colors=[])
    assert bg.colors == []


# ---------------------------------------------------------------------------
# BorderStyle — sweet path
# ---------------------------------------------------------------------------


def test_border_solid():
    b = BorderStyle(type="solid", width="2px", color=_RED)
    assert b.type == "solid"
    assert b.width == "2px"
    assert b.color == _RED


def test_border_is_frozen():
    b = BorderStyle(type="solid", width="1px", color=_RED)
    with pytest.raises((AttributeError, TypeError)):
        b.width = "3px"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# BorderStyle — corner cases
# ---------------------------------------------------------------------------


def test_border_zero_width_string():
    b = BorderStyle(type="solid", width="0px", color=_RED)
    assert b.width == "0px"


def test_border_unusual_width_unit():
    b = BorderStyle(type="solid", width="0.5em", color=_RED)
    assert b.width == "0.5em"


# ---------------------------------------------------------------------------
# IconStyle — sweet path
# ---------------------------------------------------------------------------


def test_icon_emoji():
    icon = IconStyle(type="emoji", value="📝")
    assert icon.type == "emoji"
    assert icon.value == "📝"


def test_icon_image():
    icon = IconStyle(type="image", value="/assets/logo.png")
    assert icon.type == "image"
    assert icon.value == "/assets/logo.png"


def test_icon_is_frozen():
    icon = IconStyle(type="emoji", value="📝")
    with pytest.raises((AttributeError, TypeError)):
        icon.value = "🎓"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# IconStyle — corner cases
# ---------------------------------------------------------------------------


def test_icon_empty_value_stored():
    icon = IconStyle(type="emoji", value="")
    assert icon.value == ""


# ---------------------------------------------------------------------------
# Layout — sweet path
# ---------------------------------------------------------------------------


def test_layout_all_none():
    layout = Layout()
    assert layout.id is None
    assert layout.background is None
    assert layout.border is None
    assert layout.icon is None


def test_layout_with_id_only():
    layout = Layout(id="primary")
    assert layout.id == "primary"


def test_layout_fully_specified():
    bg = BackgroundStyle(type="solid", color=_RED)
    border = BorderStyle(type="solid", width="1px", color=_BLUE)
    icon = IconStyle(type="emoji", value="🏫")
    layout = Layout(id="school", background=bg, border=border, icon=icon)
    assert layout.background == bg
    assert layout.border == border
    assert layout.icon == icon


def test_layout_is_frozen():
    layout = Layout(id="x")
    with pytest.raises((AttributeError, TypeError)):
        layout.id = "y"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Layout — corner cases
# ---------------------------------------------------------------------------


def test_layout_anonymous_inline():
    bg = BackgroundStyle(type="gradient", colors=[_RED, _BLUE])
    layout = Layout(background=bg)
    assert layout.id is None
    assert layout.background is not None


def test_layout_equality_all_none():
    assert Layout() == Layout()


def test_layout_with_only_icon():
    layout = Layout(icon=IconStyle(type="emoji", value="⭐"))
    assert layout.icon is not None
    assert layout.background is None
    assert layout.border is None
