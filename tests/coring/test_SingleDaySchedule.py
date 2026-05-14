"""Tests for coring.SingleDaySchedule."""

import datetime

import pytest

from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.utilizing.timing.Duration import Duration


# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_single_day_all_day():
    s = SingleDaySchedule(day=datetime.date(2026, 6, 15))
    assert s.day == datetime.date(2026, 6, 15)
    assert s.start_time is None
    assert s.duration is None


def test_single_day_timed_with_duration():
    s = SingleDaySchedule(
        day=datetime.date(2026, 6, 15),
        start_time=datetime.time(14, 0),
        duration=Duration.from_string("2h"),
    )
    assert s.start_time == datetime.time(14, 0)
    assert s.duration == Duration.from_string("2h")


def test_single_day_timed_no_end():
    s = SingleDaySchedule(
        day=datetime.date(2026, 6, 15),
        start_time=datetime.time(9, 30),
    )
    assert s.start_time == datetime.time(9, 30)
    assert s.duration is None


def test_single_day_is_frozen():
    s = SingleDaySchedule(day=datetime.date(2026, 1, 1))
    with pytest.raises((AttributeError, TypeError)):
        s.day = datetime.date(2026, 2, 1)  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_single_day_midnight_start():
    s = SingleDaySchedule(
        day=datetime.date(2026, 1, 1),
        start_time=datetime.time(0, 0),
        duration=Duration.from_string("30m"),
    )
    assert s.start_time == datetime.time(0, 0)


def test_single_day_duration_only_no_start_time():
    # Semantically unusual but coring stores it; backending validates
    s = SingleDaySchedule(
        day=datetime.date(2026, 6, 15),
        duration=Duration.from_string("4h"),
    )
    assert s.start_time is None
    assert s.duration == Duration.from_string("4h")


def test_single_day_long_duration():
    s = SingleDaySchedule(
        day=datetime.date(2026, 6, 15),
        start_time=datetime.time(0),
        duration=Duration.from_string("23h59m"),
    )
    assert s.duration == Duration.from_string("23h59m")


def test_single_day_last_day_of_year():
    s = SingleDaySchedule(day=datetime.date(2026, 12, 31))
    assert s.day == datetime.date(2026, 12, 31)
