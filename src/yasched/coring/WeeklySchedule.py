"""Schedule that repeats on specified days of the week."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from yasched.coring._shared import WeeklyAppointment
from yasched.coring.Schedule import Schedule


@dataclass(frozen=True)
class WeeklySchedule(Schedule):
    """Repeating schedule defined by per-day appointments."""

    appointments: list[WeeklyAppointment]
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None

    def __post_init__(self) -> None:
        if not self.appointments:
            raise ValueError("WeeklySchedule.appointments must not be empty.")
