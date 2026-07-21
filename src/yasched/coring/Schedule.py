"""Recurrence / timing value objects.

A ``Schedule`` describes *when* an event or recurring task happens. It carries no
date-expansion logic itself; ``backending.scheduling`` turns a schedule into
concrete dated occurrences.

All schedules optionally carry a time-of-day window via ``start_time`` plus
exactly-or-fewer of ``end_time`` / ``duration`` (all optional → an all-day item).
"""

from __future__ import annotations

from dataclasses import dataclass

from yasched.coring._shared import Weekday
from yasched.utilizing.timing.Date import Date
from yasched.utilizing.timing.Duration import Duration
from yasched.utilizing.timing.Time import Time


@dataclass(frozen=True)
class Schedule:
    """Base type unifying all schedule kinds under one type for ``list[Schedule]``.

    ``start_date`` / ``end_date`` optionally bound a recurring schedule to a date
    range (e.g. a class that only runs during one semester). They are inclusive
    and clamp occurrence expansion; ``None`` means unbounded on that side.
    """

    start_time: Time | None = None
    end_time: Time | None = None
    duration: Duration | None = None
    start_date: Date | None = None
    end_date: Date | None = None


@dataclass(frozen=True)
class WeeklySchedule(Schedule):
    """Repeats on the given days of the week, indefinitely."""

    week_days: tuple[Weekday, ...] = ()


@dataclass(frozen=True)
class MonthlySchedule(Schedule):
    """Repeats on a fixed day-of-month (1-31); months without that day are skipped."""

    day: int = 1


@dataclass(frozen=True)
class YearlySchedule(Schedule):
    """Repeats once per year on a fixed month/day."""

    month: int = 1
    day: int = 1


@dataclass(frozen=True)
class SingleDaySchedule(Schedule):
    """One-off occurrence on a single date."""

    day: Date | None = None


@dataclass(frozen=True)
class MultiDaySchedule(Schedule):
    """One-off occurrence spanning an inclusive date range."""

    start_day: Date | None = None
    end_day: Date | None = None
