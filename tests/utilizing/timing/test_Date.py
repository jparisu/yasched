"""Tests for Date."""

import datetime

import pytest

from yasched.utilizing.timing.Date import Date
from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# from_string — sweet path
# ---------------------------------------------------------------------------


def test_from_string_iso():
    d = Date.from_string("2026-01-15")
    assert d.value == datetime.date(2026, 1, 15)


def test_from_string_dd_mm_yyyy():
    d = Date.from_string("15/01/2026")
    assert d.value == datetime.date(2026, 1, 15)


def test_from_string_mm_dd_yyyy():
    d = Date.from_string("01/15/2026")
    assert d.value == datetime.date(2026, 1, 15)


def test_from_string_long_form():
    d = Date.from_string("January 15, 2026")
    assert d.value == datetime.date(2026, 1, 15)


def test_from_string_short_month():
    d = Date.from_string("Jan 15 2026")
    assert d.value == datetime.date(2026, 1, 15)


def test_from_string_today_keyword():
    d = Date.from_string("today")
    assert d.value == datetime.date.today()


def test_from_string_tomorrow_keyword():
    d = Date.from_string("tomorrow")
    assert d.value == datetime.date.today() + datetime.timedelta(days=1)


def test_from_string_keywords_resolve_to_concrete_date():
    d = Date.from_string("today")
    assert isinstance(d.value, datetime.date)


# ---------------------------------------------------------------------------
# from_string — failure cases
# ---------------------------------------------------------------------------


def test_from_string_invalid_format_raises():
    with pytest.raises(ValueError):
        Date.from_string("not-a-date")


def test_from_string_empty_raises():
    with pytest.raises(ValueError):
        Date.from_string("")


def test_from_string_partial_date_raises():
    with pytest.raises(ValueError):
        Date.from_string("2026-01")


def test_from_string_wrong_separator_raises():
    with pytest.raises(ValueError):
        Date.from_string("2026.01.15")


# ---------------------------------------------------------------------------
# today / tomorrow
# ---------------------------------------------------------------------------


def test_today_returns_today():
    assert Date.today().value == datetime.date.today()


def test_tomorrow_returns_tomorrow():
    assert Date.tomorrow().value == datetime.date.today() + datetime.timedelta(days=1)


def test_today_and_tomorrow_differ_by_one_day():
    assert (Date.tomorrow().value - Date.today().value).days == 1


# ---------------------------------------------------------------------------
# to_iso / to_long
# ---------------------------------------------------------------------------


def test_to_iso_format():
    d = Date.from_string("2026-01-15")
    assert d.to_iso() == "2026-01-15"


def test_to_iso_zero_pads_month():
    d = Date(value=datetime.date(2026, 3, 5))
    assert d.to_iso() == "2026-03-05"


def test_to_long_format():
    d = Date.from_string("2026-01-15")
    assert d.to_long() == "January 15, 2026"


def test_to_long_december():
    d = Date(value=datetime.date(2025, 12, 31))
    assert d.to_long() == "December 31, 2025"


# ---------------------------------------------------------------------------
# year / month / day
# ---------------------------------------------------------------------------


def test_year():
    d = Date(value=datetime.date(2026, 6, 20))
    assert d.year() == 2026


def test_month():
    d = Date(value=datetime.date(2026, 6, 20))
    assert d.month() == 6


def test_day():
    d = Date(value=datetime.date(2026, 6, 20))
    assert d.day() == 20


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------


def test_str_same_as_to_iso():
    d = Date.from_string("2026-01-15")
    assert str(d) == d.to_iso()


# ---------------------------------------------------------------------------
# __lt__ / __eq__
# ---------------------------------------------------------------------------


def test_lt_earlier_date():
    a = Date(value=datetime.date(2026, 1, 1))
    b = Date(value=datetime.date(2026, 6, 1))
    assert a < b


def test_lt_later_date_is_false():
    a = Date(value=datetime.date(2026, 6, 1))
    b = Date(value=datetime.date(2026, 1, 1))
    assert not (a < b)


def test_lt_same_date_is_false():
    d = Date(value=datetime.date(2026, 3, 15))
    assert not (d < d)


def test_eq_same_date():
    a = Date(value=datetime.date(2026, 3, 15))
    b = Date(value=datetime.date(2026, 3, 15))
    assert a == b


def test_eq_different_date():
    a = Date(value=datetime.date(2026, 3, 15))
    b = Date(value=datetime.date(2026, 3, 16))
    assert a != b


# ---------------------------------------------------------------------------
# __add__ with Duration
# ---------------------------------------------------------------------------


def test_add_duration_whole_days():
    d = Date(value=datetime.date(2026, 1, 1))
    result = d + Duration.from_string("10d")
    assert result.value == datetime.date(2026, 1, 11)


def test_add_duration_zero_days_unchanged():
    d = Date(value=datetime.date(2026, 6, 15))
    result = d + Duration.zero()
    assert result == d


def test_add_duration_crosses_month_boundary():
    d = Date(value=datetime.date(2026, 1, 28))
    result = d + Duration.from_string("5d")
    assert result.value == datetime.date(2026, 2, 2)


def test_add_duration_crosses_year_boundary():
    d = Date(value=datetime.date(2025, 12, 30))
    result = d + Duration.from_string("3d")
    assert result.value == datetime.date(2026, 1, 2)


def test_add_sub_day_duration_is_truncated_to_whole_days():
    d = Date(value=datetime.date(2026, 1, 1))
    sub_day = Duration(value=datetime.timedelta(hours=23))
    result = d + sub_day
    assert result.value == datetime.date(2026, 1, 1)


def test_add_week_duration():
    d = Date(value=datetime.date(2026, 1, 1))
    result = d + Duration.from_string("1w")
    assert result.value == datetime.date(2026, 1, 8)


# ---------------------------------------------------------------------------
# __sub__ between two Dates
# ---------------------------------------------------------------------------


def test_sub_two_dates_returns_duration():
    a = Date(value=datetime.date(2026, 1, 11))
    b = Date(value=datetime.date(2026, 1, 1))
    diff = a - b
    assert isinstance(diff, Duration)
    assert diff.to_days() == pytest.approx(10.0)


def test_sub_same_date_returns_zero():
    d = Date(value=datetime.date(2026, 3, 15))
    assert (d - d) == Duration.zero()


def test_sub_roundtrip():
    d = Date(value=datetime.date(2026, 1, 1))
    delta = Duration.from_string("30d")
    assert (d + delta) - d == delta
