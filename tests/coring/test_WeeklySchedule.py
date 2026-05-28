"""Tests for coring.WeeklySchedule."""

import datetime

import pytest

from yasched.coring._shared import Weekday, WeeklyAppointment
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.utilizing.timing.Duration import Duration


def _appt(day: Weekday, h: int, duration: str = "1h") -> WeeklyAppointment:
    return WeeklyAppointment(
        week_day=day,
        start_time=datetime.time(h),
        duration=Duration.from_string(duration),
    )


# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_weekly_schedule_single_appointment():
    ws = WeeklySchedule(appointments=[_appt(Weekday.MONDAY, 9)])
    assert len(ws.appointments) == 1
    assert ws.appointments[0].week_day == Weekday.MONDAY


def test_weekly_schedule_multiple_appointments():
    appts = [_appt(Weekday.MONDAY, 9), _appt(Weekday.WEDNESDAY, 10), _appt(Weekday.FRIDAY, 14)]
    ws = WeeklySchedule(appointments=appts)
    assert len(ws.appointments) == 3


def test_weekly_schedule_no_date_bounds():
    ws = WeeklySchedule(appointments=[_appt(Weekday.TUESDAY, 8)])
    assert ws.start_date is None
    assert ws.end_date is None


def test_weekly_schedule_with_date_bounds():
    ws = WeeklySchedule(
        appointments=[_appt(Weekday.MONDAY, 9)],
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 12, 31),
    )
    assert ws.start_date == datetime.date(2026, 1, 1)
    assert ws.end_date == datetime.date(2026, 12, 31)


def test_weekly_schedule_is_frozen():
    ws = WeeklySchedule(appointments=[_appt(Weekday.MONDAY, 9)])
    with pytest.raises((AttributeError, TypeError)):
        ws.appointments = []  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_weekly_schedule_same_day_multiple_slots():
    appts = [
        WeeklyAppointment(Weekday.MONDAY, datetime.time(9), end_time=datetime.time(10)),
        WeeklyAppointment(Weekday.MONDAY, datetime.time(14), duration=Duration.from_string("1h")),
    ]
    ws = WeeklySchedule(appointments=appts)
    assert len(ws.appointments) == 2


def test_weekly_schedule_only_start_date():
    ws = WeeklySchedule(
        appointments=[_appt(Weekday.FRIDAY, 16)],
        start_date=datetime.date(2026, 3, 1),
    )
    assert ws.start_date is not None
    assert ws.end_date is None


def test_weekly_schedule_start_date_equals_end_date():
    ws = WeeklySchedule(
        appointments=[_appt(Weekday.MONDAY, 9)],
        start_date=datetime.date(2026, 6, 1),
        end_date=datetime.date(2026, 6, 1),
    )
    assert ws.start_date == ws.end_date


# ---------------------------------------------------------------------------
# Construction — failure cases
# ---------------------------------------------------------------------------


def test_weekly_schedule_empty_appointments_raises():
    with pytest.raises(ValueError):
        WeeklySchedule(appointments=[])
