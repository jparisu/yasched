"""Tests for coring.MonthlySchedule."""

import datetime

import pytest

from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_monthly_schedule_minimal():
    ms = MonthlySchedule(
        day_of_month=15,
        start_time=datetime.time(10),
        duration=Duration.from_string("1h"),
    )
    assert ms.day_of_month == 15
    assert ms.start_date is None
    assert ms.end_date is None


def test_monthly_schedule_day_1():
    ms = MonthlySchedule(
        day_of_month=1,
        start_time=datetime.time(8),
        duration=Duration.from_string("30m"),
    )
    assert ms.day_of_month == 1


def test_monthly_schedule_day_28():
    ms = MonthlySchedule(
        day_of_month=28,
        start_time=datetime.time(9),
        duration=Duration.from_string("2h"),
    )
    assert ms.day_of_month == 28


def test_monthly_schedule_with_date_range():
    ms = MonthlySchedule(
        day_of_month=10,
        start_time=datetime.time(10),
        duration=Duration.from_string("1h"),
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 12, 31),
    )
    assert ms.start_date == datetime.date(2026, 1, 1)
    assert ms.end_date == datetime.date(2026, 12, 31)


def test_monthly_schedule_is_frozen():
    ms = MonthlySchedule(
        day_of_month=15,
        start_time=datetime.time(10),
        duration=Duration.from_string("1h"),
    )
    with pytest.raises((AttributeError, TypeError)):
        ms.day_of_month = 20  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_monthly_schedule_only_start_date():
    ms = MonthlySchedule(
        day_of_month=5,
        start_time=datetime.time(9),
        duration=Duration.from_string("45m"),
        start_date=datetime.date(2026, 6, 1),
    )
    assert ms.start_date is not None
    assert ms.end_date is None


def test_monthly_schedule_midnight_start():
    ms = MonthlySchedule(
        day_of_month=1,
        start_time=datetime.time(0, 0),
        duration=Duration.from_string("1h"),
    )
    assert ms.start_time == datetime.time(0, 0)


# ---------------------------------------------------------------------------
# Construction — failure cases
# ---------------------------------------------------------------------------


def test_monthly_schedule_day_0_raises():
    with pytest.raises(ValueError):
        MonthlySchedule(
            day_of_month=0,
            start_time=datetime.time(10),
            duration=Duration.from_string("1h"),
        )


def test_monthly_schedule_day_29_raises():
    with pytest.raises(ValueError):
        MonthlySchedule(
            day_of_month=29,
            start_time=datetime.time(10),
            duration=Duration.from_string("1h"),
        )


def test_monthly_schedule_day_31_raises():
    with pytest.raises(ValueError):
        MonthlySchedule(
            day_of_month=31,
            start_time=datetime.time(10),
            duration=Duration.from_string("1h"),
        )


def test_monthly_schedule_negative_day_raises():
    with pytest.raises(ValueError):
        MonthlySchedule(
            day_of_month=-1,
            start_time=datetime.time(10),
            duration=Duration.from_string("1h"),
        )
