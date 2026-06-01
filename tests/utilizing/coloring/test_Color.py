"""Tests for Color."""

import pytest

from yasched.utilizing.coloring.Color import Color

# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_color_default_alpha():
    c = Color(r=1.0, g=0.0, b=0.0)
    assert c.a == 1.0


def test_color_explicit_alpha():
    c = Color(r=0.0, g=0.5, b=1.0, a=0.5)
    assert c.a == 0.5


def test_color_stores_channels_correctly():
    c = Color(r=0.2, g=0.4, b=0.6, a=0.8)
    assert c.r == pytest.approx(0.2)
    assert c.g == pytest.approx(0.4)
    assert c.b == pytest.approx(0.6)
    assert c.a == pytest.approx(0.8)


def test_color_zero_values():
    c = Color(r=0.0, g=0.0, b=0.0, a=0.0)
    assert c.r == 0.0 and c.g == 0.0 and c.b == 0.0 and c.a == 0.0


def test_color_max_values():
    c = Color(r=1.0, g=1.0, b=1.0, a=1.0)
    assert c.r == 1.0 and c.g == 1.0 and c.b == 1.0 and c.a == 1.0


# ---------------------------------------------------------------------------
# Construction — out-of-range validation
# ---------------------------------------------------------------------------


def test_color_r_above_1_raises():
    with pytest.raises(ValueError):
        Color(r=1.1, g=0.0, b=0.0)


def test_color_r_below_0_raises():
    with pytest.raises(ValueError):
        Color(r=-0.1, g=0.0, b=0.0)


def test_color_g_above_1_raises():
    with pytest.raises(ValueError):
        Color(r=0.0, g=1.5, b=0.0)


def test_color_b_above_1_raises():
    with pytest.raises(ValueError):
        Color(r=0.0, g=0.0, b=2.0)


def test_color_a_above_1_raises():
    with pytest.raises(ValueError):
        Color(r=0.0, g=0.0, b=0.0, a=1.01)


def test_color_a_below_0_raises():
    with pytest.raises(ValueError):
        Color(r=0.0, g=0.0, b=0.0, a=-0.5)


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


def test_color_is_frozen():
    c = Color(r=1.0, g=0.0, b=0.0)
    with pytest.raises((AttributeError, TypeError)):
        c.r = 0.5  # type: ignore[misc]


# ---------------------------------------------------------------------------
# from_name
# ---------------------------------------------------------------------------


def test_from_name_red():
    c = Color.from_name("red")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_from_name_white():
    c = Color.from_name("white")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(1.0)
    assert c.b == pytest.approx(1.0)


def test_from_name_black():
    c = Color.from_name("black")
    assert c.r == pytest.approx(0.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_from_name_case_insensitive():
    assert Color.from_name("Red") == Color.from_name("red")


def test_from_name_unknown_raises():
    with pytest.raises((KeyError, ValueError)):
        Color.from_name("notacolor")


def test_from_name_empty_string_raises():
    with pytest.raises((KeyError, ValueError)):
        Color.from_name("")


# ---------------------------------------------------------------------------
# from_hex
# ---------------------------------------------------------------------------


def test_from_hex_6_digit_with_hash():
    c = Color.from_hex("#ff0000")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_from_hex_6_digit_without_hash():
    c = Color.from_hex("ff0000")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_from_hex_3_digit():
    c = Color.from_hex("#f00")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_from_hex_uppercase():
    c = Color.from_hex("#FF0000")
    assert c.r == pytest.approx(1.0)


def test_from_hex_white():
    c = Color.from_hex("#ffffff")
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(1.0)
    assert c.b == pytest.approx(1.0)


def test_from_hex_black():
    c = Color.from_hex("#000000")
    assert c.r == pytest.approx(0.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_from_hex_default_alpha_is_1():
    c = Color.from_hex("#aabbcc")
    assert c.a == pytest.approx(1.0)


def test_from_hex_invalid_characters_raises():
    with pytest.raises(ValueError):
        Color.from_hex("#zzzzzz")


def test_from_hex_wrong_length_raises():
    with pytest.raises(ValueError):
        Color.from_hex("#12345")


def test_from_hex_empty_raises():
    with pytest.raises(ValueError):
        Color.from_hex("")


# ---------------------------------------------------------------------------
# from_rgb
# ---------------------------------------------------------------------------


def test_from_rgb_float_inputs():
    c = Color.from_rgb(0.5, 0.25, 0.75)
    assert c.r == pytest.approx(0.5)
    assert c.g == pytest.approx(0.25)
    assert c.b == pytest.approx(0.75)


def test_from_rgb_integer_inputs_normalized():
    c = Color.from_rgb(255, 0, 0)
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(0.0)
    assert c.b == pytest.approx(0.0)


def test_from_rgb_integer_midpoint():
    c = Color.from_rgb(128, 128, 128)
    assert c.r == pytest.approx(128 / 255, abs=1e-3)


def test_from_rgb_explicit_alpha():
    c = Color.from_rgb(255, 0, 0, 0.5)
    assert c.a == pytest.approx(0.5)


def test_from_rgb_default_alpha_is_1():
    c = Color.from_rgb(0, 128, 255)
    assert c.a == pytest.approx(1.0)


def test_from_rgb_out_of_range_raises():
    with pytest.raises(ValueError):
        Color.from_rgb(300, 0, 0)


def test_from_rgb_negative_raises():
    with pytest.raises(ValueError):
        Color.from_rgb(-1, 0, 0)


# ---------------------------------------------------------------------------
# to_hex
# ---------------------------------------------------------------------------


def test_to_hex_red():
    c = Color(r=1.0, g=0.0, b=0.0)
    assert c.to_hex().lower() in ("#ff0000", "ff0000")


def test_to_hex_black():
    c = Color(r=0.0, g=0.0, b=0.0)
    assert c.to_hex().lower() in ("#000000", "000000")


def test_to_hex_white():
    c = Color(r=1.0, g=1.0, b=1.0)
    assert c.to_hex().lower() in ("#ffffff", "ffffff")


def test_to_hex_roundtrip():
    original = Color.from_hex("#1a2b3c")
    assert Color.from_hex(original.to_hex()) == original


# ---------------------------------------------------------------------------
# to_rgba_tuple
# ---------------------------------------------------------------------------


def test_to_rgba_tuple_values():
    c = Color(r=0.2, g=0.4, b=0.6, a=0.8)
    t = c.to_rgba_tuple()
    assert t == pytest.approx((0.2, 0.4, 0.6, 0.8))


def test_to_rgba_tuple_length():
    c = Color(r=1.0, g=0.0, b=0.0)
    assert len(c.to_rgba_tuple()) == 4


def test_to_rgba_tuple_default_alpha():
    c = Color(r=0.5, g=0.5, b=0.5)
    assert c.to_rgba_tuple()[3] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# with_alpha
# ---------------------------------------------------------------------------


def test_with_alpha_returns_new_color():
    c = Color(r=1.0, g=0.0, b=0.0, a=1.0)
    c2 = c.with_alpha(0.5)
    assert c2 is not c


def test_with_alpha_sets_alpha():
    c = Color(r=1.0, g=0.0, b=0.0)
    c2 = c.with_alpha(0.3)
    assert c2.a == pytest.approx(0.3)


def test_with_alpha_preserves_rgb():
    c = Color(r=0.2, g=0.4, b=0.6)
    c2 = c.with_alpha(0.0)
    assert c2.r == pytest.approx(0.2)
    assert c2.g == pytest.approx(0.4)
    assert c2.b == pytest.approx(0.6)


def test_with_alpha_zero():
    c = Color(r=1.0, g=1.0, b=1.0)
    assert c.with_alpha(0.0).a == pytest.approx(0.0)


def test_with_alpha_out_of_range_raises():
    c = Color(r=1.0, g=0.0, b=0.0)
    with pytest.raises(ValueError):
        c.with_alpha(1.5)


def test_with_alpha_negative_raises():
    c = Color(r=1.0, g=0.0, b=0.0)
    with pytest.raises(ValueError):
        c.with_alpha(-0.1)


def test_with_alpha_does_not_mutate_original():
    c = Color(r=1.0, g=0.0, b=0.0, a=1.0)
    c.with_alpha(0.0)
    assert c.a == pytest.approx(1.0)
