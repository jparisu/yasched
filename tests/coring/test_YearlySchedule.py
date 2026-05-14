"""Tests for coring.YearlySchedule."""

import pytest

from yasched.coring.YearlySchedule import YearlySchedule


# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_yearly_schedule_christmas():
    ys = YearlySchedule(month=12, day=25)
    assert ys.month == 12
    assert ys.day == 25


def test_yearly_schedule_new_year():
    ys = YearlySchedule(month=1, day=1)
    assert ys.month == 1
    assert ys.day == 1


def test_yearly_schedule_last_valid_month():
    ys = YearlySchedule(month=12, day=31)
    assert ys.month == 12


def test_yearly_schedule_is_frozen():
    ys = YearlySchedule(month=6, day=15)
    with pytest.raises((AttributeError, TypeError)):
        ys.month = 7  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_yearly_schedule_feb_29_stored_without_calendar_check():
    # coring does not validate day-in-month; backending does
    ys = YearlySchedule(month=2, day=29)
    assert ys.day == 29


def test_yearly_schedule_month_1_day_31():
    ys = YearlySchedule(month=1, day=31)
    assert ys.day == 31


# ---------------------------------------------------------------------------
# Construction — failure cases
# ---------------------------------------------------------------------------


def test_yearly_schedule_month_0_raises():
    with pytest.raises(ValueError):
        YearlySchedule(month=0, day=1)


def test_yearly_schedule_month_13_raises():
    with pytest.raises(ValueError):
        YearlySchedule(month=13, day=1)


def test_yearly_schedule_day_0_raises():
    with pytest.raises(ValueError):
        YearlySchedule(month=6, day=0)


def test_yearly_schedule_day_32_raises():
    with pytest.raises(ValueError):
        YearlySchedule(month=6, day=32)


def test_yearly_schedule_negative_month_raises():
    with pytest.raises(ValueError):
        YearlySchedule(month=-1, day=15)


def test_yearly_schedule_negative_day_raises():
    with pytest.raises(ValueError):
        YearlySchedule(month=6, day=-5)
