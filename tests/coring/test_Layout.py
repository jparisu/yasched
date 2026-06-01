"""Tests for coring.Layout: background types, border, icon, shape, pin."""

import pytest

from yasched.coring.Layout import (
    BorderStyle,
    GradientBottomLeftBackground,
    GradientTopRightBackground,
    IconStyle,
    Layout,
    PinStyle,
    ShapeStyle,
    SolidBackground,
)
from yasched.utilizing.coloring.Color import Color

_RED = Color(r=1.0, g=0.0, b=0.0)
_BLUE = Color(r=0.0, g=0.0, b=1.0)


# ---------------------------------------------------------------------------
# SolidBackground
# ---------------------------------------------------------------------------


def test_solid_background_stores_color():
    bg = SolidBackground(color=_RED)
    assert bg.color == _RED


def test_solid_background_is_frozen():
    bg = SolidBackground(color=_RED)
    with pytest.raises((AttributeError, TypeError)):
        bg.color = _BLUE  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GradientTopRightBackground
# ---------------------------------------------------------------------------


def test_gradient_tr_stores_color():
    bg = GradientTopRightBackground(color=_RED)
    assert bg.color == _RED


def test_gradient_tr_is_frozen():
    bg = GradientTopRightBackground(color=_RED)
    with pytest.raises((AttributeError, TypeError)):
        bg.color = _BLUE  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GradientBottomLeftBackground
# ---------------------------------------------------------------------------


def test_gradient_bl_stores_color():
    bg = GradientBottomLeftBackground(color=_BLUE)
    assert bg.color == _BLUE


def test_gradient_bl_is_frozen():
    bg = GradientBottomLeftBackground(color=_BLUE)
    with pytest.raises((AttributeError, TypeError)):
        bg.color = _RED  # type: ignore[misc]


# ---------------------------------------------------------------------------
# BorderStyle
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


def test_border_zero_width_string():
    b = BorderStyle(type="solid", width="0px", color=_RED)
    assert b.width == "0px"


def test_border_unusual_width_unit():
    b = BorderStyle(type="solid", width="0.5em", color=_RED)
    assert b.width == "0.5em"


# ---------------------------------------------------------------------------
# IconStyle
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


def test_icon_empty_value_stored():
    icon = IconStyle(type="emoji", value="")
    assert icon.value == ""


# ---------------------------------------------------------------------------
# ShapeStyle
# ---------------------------------------------------------------------------


def test_shape_rectangle():
    s = ShapeStyle(type="rectangle")
    assert s.type == "rectangle"
    assert s.radius is None


def test_shape_rounded_with_radius():
    s = ShapeStyle(type="rounded", radius="8px")
    assert s.type == "rounded"
    assert s.radius == "8px"


def test_shape_is_frozen():
    s = ShapeStyle(type="pill")
    with pytest.raises((AttributeError, TypeError)):
        s.type = "trapezoid"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PinStyle
# ---------------------------------------------------------------------------


def test_pin_color_only():
    p = PinStyle(color=_RED)
    assert p.color == _RED
    assert p.icon is None


def test_pin_with_icon():
    p = PinStyle(color=_BLUE, icon="📌")
    assert p.icon == "📌"


def test_pin_is_frozen():
    p = PinStyle(color=_RED)
    with pytest.raises((AttributeError, TypeError)):
        p.color = _BLUE  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Layout — sweet path
# ---------------------------------------------------------------------------


def test_layout_all_empty():
    layout = Layout()
    assert layout.id is None
    assert layout.backgrounds == []
    assert layout.border is None
    assert layout.icon is None
    assert layout.shape is None
    assert layout.pin is None


def test_layout_with_id_only():
    layout = Layout(id="primary")
    assert layout.id == "primary"


def test_layout_fully_specified():
    bg = SolidBackground(color=_RED)
    border = BorderStyle(type="solid", width="1px", color=_BLUE)
    icon = IconStyle(type="emoji", value="🏫")
    shape = ShapeStyle(type="rounded", radius="4px")
    pin = PinStyle(color=_RED)
    layout = Layout(
        id="school",
        backgrounds=[bg],
        border=border,
        icon=icon,
        shape=shape,
        pin=pin,
    )
    assert layout.backgrounds == [bg]
    assert layout.border == border
    assert layout.icon == icon
    assert layout.shape == shape
    assert layout.pin == pin


def test_layout_is_frozen():
    layout = Layout(id="x")
    with pytest.raises((AttributeError, TypeError)):
        layout.id = "y"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Layout — multiple background layers
# ---------------------------------------------------------------------------


def test_layout_two_gradient_layers():
    tr = GradientTopRightBackground(color=_RED)
    bl = GradientBottomLeftBackground(color=_BLUE)
    layout = Layout(backgrounds=[tr, bl])
    assert len(layout.backgrounds) == 2
    assert isinstance(layout.backgrounds[0], GradientTopRightBackground)
    assert isinstance(layout.backgrounds[1], GradientBottomLeftBackground)


def test_layout_anonymous_inline():
    bg = SolidBackground(color=_RED)
    layout = Layout(backgrounds=[bg])
    assert layout.id is None
    assert len(layout.backgrounds) == 1


def test_layout_equality_all_empty():
    assert Layout() == Layout()


def test_layout_with_only_icon():
    layout = Layout(icon=IconStyle(type="emoji", value="⭐"))
    assert layout.icon is not None
    assert layout.backgrounds == []
    assert layout.border is None
