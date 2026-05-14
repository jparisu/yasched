"""One-off occurrence on a specific calendar date."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from yasched.coring.Schedule import Schedule
from yasched.utilizing.timing.Duration import Duration


@dataclass(frozen=True)
class SingleDaySchedule(Schedule):
    """One-off event on a single date; optionally timed and/or bounded."""

    day: datetime.date
    start_time: datetime.time | None = None
    duration: Duration | None = None
