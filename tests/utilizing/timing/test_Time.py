"""Tests for Time."""

import datetime

import pytest

from yasched.utilizing.timing.Duration import Duration
from yasched.utilizing.timing.Time import Time


# ---------------------------------------------------------------------------
# from_string — sweet path
# ---------------------------------------------------------------------------


def test_from_string_hhmm_24h():
    t = Time.from_string("10:00")
    assert t.value == datetime.time(10, 0)


def test_from_string_hhmmss_24h():
    t = Time.from_string("10:00:30")
    assert t.value == datetime.time(10, 0, 30)


def test_from_string_12h_no_minutes():
    t = Time.from_string("10am")
    assert t.value == datetime.time(10, 0)


def test_from_string_12h_with_minutes_lowercase():
    t = Time.from_string("10:30am")
    assert t.value == datetime.time(10, 30)


def test_from_string_12h_with_space_and_uppercase():
    t = Time.from_string("10:30 AM")
    assert t.value == datetime.time(10, 30)


def test_from_string_24h_afternoon():
    t = Time.from_string("22:45")
    assert t.value == datetime.time(22, 45)


def test_from_string_midnight_24h():
    t = Time.from_string("00:00")
    assert t.value == datetime.time(0, 0)


def test_from_string_noon_24h():
    t = Time.from_string("12:00")
    assert t.value == datetime.time(12, 0)


def test_from_string_12pm_equals_noon():
    t = Time.from_string("12:00pm")
    assert t.value == datetime.time(12, 0)


def test_from_string_12am_equals_midnight():
    t = Time.from_string("12:00am")
    assert t.value == datetime.time(0, 0)


def test_from_string_pm_adds_12_hours():
    t = Time.from_string("3pm")
    assert t.value == datetime.time(15, 0)


def test_from_string_case_insensitive_am():
    assert Time.from_string("9AM") == Time.from_string("9am")


def test_from_string_case_insensitive_pm():
    assert Time.from_string("3PM") == Time.from_string("3pm")


# ---------------------------------------------------------------------------
# from_string — failure cases
# ---------------------------------------------------------------------------


def test_from_string_invalid_format_raises():
    with pytest.raises(ValueError):
        Time.from_string("not-a-time")


def test_from_string_empty_raises():
    with pytest.raises(ValueError):
        Time.from_string("")


def test_from_string_out_of_range_hour_raises():
    with pytest.raises(ValueError):
        Time.from_string("25:00")


def test_from_string_out_of_range_minute_raises():
    with pytest.raises(ValueError):
        Time.from_string("10:60")


def test_from_string_missing_minutes_24h_raises():
    with pytest.raises(ValueError):
        Time.from_string("10:")


# ---------------------------------------------------------------------------
# now
# ---------------------------------------------------------------------------


def test_now_returns_time_instance():
    t = Time.now()
    assert isinstance(t, Time)


def test_now_is_close_to_current_time():
    t = Time.now()
    now = datetime.datetime.now().time()
    delta = abs(
        datetime.timedelta(hours=t.hour(), minutes=t.minute(), seconds=t.second())
        - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    )
    assert delta.total_seconds() < 5


# ---------------------------------------------------------------------------
# to_hhmm / to_hhmmss
# ---------------------------------------------------------------------------


def test_to_hhmm_no_seconds():
    t = Time.from_string("14:30")
    assert t.to_hhmm() == "14:30"


def test_to_hhmm_omits_zero_seconds():
    t = Time(value=datetime.time(9, 5, 0))
    assert t.to_hhmm() == "09:05"


def test_to_hhmm_when_seconds_nonzero_still_omits_them():
    t = Time(value=datetime.time(10, 0, 30))
    assert t.to_hhmm() == "10:00"


def test_to_hhmmss_includes_seconds():
    t = Time(value=datetime.time(10, 0, 30))
    assert t.to_hhmmss() == "10:00:30"


def test_to_hhmmss_zero_seconds():
    t = Time.from_string("08:00")
    assert t.to_hhmmss() == "08:00:00"


def test_to_hhmm_zero_pads():
    t = Time(value=datetime.time(8, 5))
    assert t.to_hhmm() == "08:05"


# ---------------------------------------------------------------------------
# hour / minute / second
# ---------------------------------------------------------------------------


def test_hour():
    t = Time(value=datetime.time(14, 30, 45))
    assert t.hour() == 14


def test_minute():
    t = Time(value=datetime.time(14, 30, 45))
    assert t.minute() == 30


def test_second():
    t = Time(value=datetime.time(14, 30, 45))
    assert t.second() == 45


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------


def test_str_same_as_to_hhmm():
    t = Time.from_string("14:30")
    assert str(t) == t.to_hhmm()


# ---------------------------------------------------------------------------
# __lt__ / __eq__
# ---------------------------------------------------------------------------


def test_lt_earlier_is_less():
    a = Time(value=datetime.time(8, 0))
    b = Time(value=datetime.time(10, 0))
    assert a < b


def test_lt_later_is_not_less():
    a = Time(value=datetime.time(10, 0))
    b = Time(value=datetime.time(8, 0))
    assert not (a < b)


def test_lt_same_is_not_less():
    t = Time(value=datetime.time(10, 0))
    assert not (t < t)


def test_eq_same_time():
    a = Time(value=datetime.time(10, 30))
    b = Time(value=datetime.time(10, 30))
    assert a == b


def test_eq_different_time():
    a = Time(value=datetime.time(10, 30))
    b = Time(value=datetime.time(10, 31))
    assert a != b


# ---------------------------------------------------------------------------
# __add__ with Duration (wraps around midnight)
# ---------------------------------------------------------------------------


def test_add_duration_simple():
    t = Time(value=datetime.time(10, 0))
    result = t + Duration.from_string("2h")
    assert result.value == datetime.time(12, 0)


def test_add_duration_wraps_past_midnight():
    t = Time(value=datetime.time(22, 0))
    result = t + Duration.from_string("3h")
    assert result.value == datetime.time(1, 0)


def test_add_zero_duration_unchanged():
    t = Time(value=datetime.time(10, 0))
    assert (t + Duration.zero()) == t


def test_add_exactly_24h_wraps_to_same_time():
    t = Time(value=datetime.time(8, 0))
    result = t + Duration(value=datetime.timedelta(hours=24))
    assert result.value == datetime.time(8, 0)


def test_add_minutes_duration():
    t = Time(value=datetime.time(10, 45))
    result = t + Duration.from_string("30m")
    assert result.value == datetime.time(11, 15)


# ---------------------------------------------------------------------------
# __sub__ between two Times → Duration (absolute difference)
# ---------------------------------------------------------------------------


def test_sub_later_minus_earlier():
    a = Time(value=datetime.time(12, 0))
    b = Time(value=datetime.time(10, 0))
    diff = a - b
    assert isinstance(diff, Duration)
    assert diff.to_hours() == pytest.approx(2.0)


def test_sub_same_time_is_zero():
    t = Time(value=datetime.time(10, 0))
    assert (t - t) == Duration.zero()


def test_sub_is_absolute_difference():
    a = Time(value=datetime.time(8, 0))
    b = Time(value=datetime.time(10, 0))
    assert (a - b) == (b - a)


def test_sub_minutes():
    a = Time(value=datetime.time(10, 45))
    b = Time(value=datetime.time(10, 15))
    diff = a - b
    assert diff.to_minutes() == 30
