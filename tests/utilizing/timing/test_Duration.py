"""Tests for Duration."""

import datetime

import pytest

from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _td(**kwargs) -> datetime.timedelta:
    return datetime.timedelta(**kwargs)


# ---------------------------------------------------------------------------
# from_string — sweet path
# ---------------------------------------------------------------------------


def test_from_string_minutes():
    d = Duration.from_string("30m")
    assert d.value == _td(minutes=30)


def test_from_string_hours():
    d = Duration.from_string("1h")
    assert d.value == _td(hours=1)


def test_from_string_days():
    d = Duration.from_string("3d")
    assert d.value == _td(days=3)


def test_from_string_weeks():
    d = Duration.from_string("1w")
    assert d.value == _td(weeks=1)


def test_from_string_hours_and_minutes():
    d = Duration.from_string("2h30m")
    assert d.value == _td(hours=2, minutes=30)


def test_from_string_all_units():
    d = Duration.from_string("1w2d3h4m")
    assert d.value == _td(weeks=1, days=2, hours=3, minutes=4)


def test_from_string_weeks_and_days():
    d = Duration.from_string("2w3d")
    assert d.value == _td(weeks=2, days=3)


def test_from_string_single_minute():
    d = Duration.from_string("1m")
    assert d.value == _td(minutes=1)


def test_from_string_large_hours():
    d = Duration.from_string("48h")
    assert d.value == _td(hours=48)


# ---------------------------------------------------------------------------
# from_string — failure cases
# ---------------------------------------------------------------------------


def test_from_string_units_out_of_order_raises():
    with pytest.raises(ValueError):
        Duration.from_string("30m1h")


def test_from_string_unknown_unit_raises():
    with pytest.raises(ValueError):
        Duration.from_string("5s")


def test_from_string_empty_raises():
    with pytest.raises(ValueError):
        Duration.from_string("")


def test_from_string_no_unit_raises():
    with pytest.raises(ValueError):
        Duration.from_string("60")


def test_from_string_invalid_string_raises():
    with pytest.raises(ValueError):
        Duration.from_string("abc")


def test_from_string_mixed_valid_invalid_raises():
    with pytest.raises(ValueError):
        Duration.from_string("1h30s")


# ---------------------------------------------------------------------------
# zero
# ---------------------------------------------------------------------------


def test_zero_value_is_timedelta_zero():
    assert Duration.zero().value == _td()


def test_zero_bool_is_false():
    assert not Duration.zero()


# ---------------------------------------------------------------------------
# to_minutes / to_hours / to_days
# ---------------------------------------------------------------------------


def test_to_minutes_exact():
    d = Duration.from_string("2h")
    assert d.to_minutes() == 120


def test_to_minutes_truncates():
    d = Duration(value=_td(minutes=90))
    assert d.to_minutes() == 90


def test_to_hours_exact():
    d = Duration.from_string("3h")
    assert d.to_hours() == pytest.approx(3.0)


def test_to_hours_fractional():
    d = Duration.from_string("1h30m")
    assert d.to_hours() == pytest.approx(1.5)


def test_to_days_exact():
    d = Duration.from_string("2d")
    assert d.to_days() == pytest.approx(2.0)


def test_to_days_fractional():
    d = Duration(value=_td(hours=36))
    assert d.to_days() == pytest.approx(1.5)


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------


def test_str_minutes_only():
    assert str(Duration.from_string("30m")) == "30m"


def test_str_hours_only():
    assert str(Duration.from_string("2h")) == "2h"


def test_str_days_only():
    assert str(Duration.from_string("3d")) == "3d"


def test_str_normalizes_120_minutes_to_2h():
    d = Duration(value=_td(minutes=120))
    assert str(d) == "2h"


def test_str_combined():
    assert str(Duration.from_string("1h30m")) == "1h30m"


def test_str_zero_units_omitted():
    d = Duration(value=_td(hours=2, minutes=0))
    assert "0m" not in str(d)
    assert str(d) == "2h"


def test_str_zero_duration():
    assert str(Duration.zero()) == "0m"


# ---------------------------------------------------------------------------
# __add__
# ---------------------------------------------------------------------------


def test_add_two_durations():
    a = Duration.from_string("1h")
    b = Duration.from_string("30m")
    assert (a + b).value == _td(hours=1, minutes=30)


def test_add_zero():
    a = Duration.from_string("2h")
    assert (a + Duration.zero()) == a


def test_add_returns_new_instance():
    a = Duration.from_string("1h")
    b = Duration.from_string("1h")
    c = a + b
    assert c is not a and c is not b


# ---------------------------------------------------------------------------
# __sub__
# ---------------------------------------------------------------------------


def test_sub_two_durations():
    a = Duration.from_string("2h")
    b = Duration.from_string("30m")
    assert (a - b).value == _td(hours=1, minutes=30)


def test_sub_same_duration_gives_zero():
    a = Duration.from_string("1h")
    assert (a - a) == Duration.zero()


def test_sub_negative_raises():
    a = Duration.from_string("30m")
    b = Duration.from_string("1h")
    with pytest.raises(ValueError):
        _ = a - b


# ---------------------------------------------------------------------------
# __mul__
# ---------------------------------------------------------------------------


def test_mul_by_integer():
    d = Duration.from_string("30m")
    assert (d * 3).value == _td(minutes=90)


def test_mul_by_one_is_equal():
    d = Duration.from_string("1h")
    assert (d * 1) == d


def test_mul_by_zero_gives_zero():
    d = Duration.from_string("2h")
    assert (d * 0) == Duration.zero()


# ---------------------------------------------------------------------------
# __lt__ / __eq__
# ---------------------------------------------------------------------------


def test_lt_smaller_is_less():
    a = Duration.from_string("30m")
    b = Duration.from_string("1h")
    assert a < b


def test_lt_equal_is_not_less():
    a = Duration.from_string("1h")
    b = Duration.from_string("1h")
    assert not (a < b)


def test_eq_same_value():
    a = Duration.from_string("2h")
    b = Duration(value=_td(hours=2))
    assert a == b


def test_eq_different_value():
    a = Duration.from_string("1h")
    b = Duration.from_string("2h")
    assert a != b


# ---------------------------------------------------------------------------
# __bool__
# ---------------------------------------------------------------------------


def test_bool_false_for_zero():
    assert not Duration.zero()


def test_bool_true_for_nonzero():
    assert Duration.from_string("1m")
