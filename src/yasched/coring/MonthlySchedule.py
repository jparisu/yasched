"""Schedule that repeats on a fixed day of the month."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from yasched.coring.Schedule import Schedule
from yasched.utilizing.timing.Duration import Duration


@dataclass(frozen=True)
class MonthlySchedule(Schedule):
    """Repeating schedule on a fixed calendar day each month (1–28)."""

    day_of_month: int
    start_time: datetime.time
    duration: Duration
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None

    def __post_init__(self) -> None:
        if not (1 <= self.day_of_month <= 28):
            raise ValueError(
                f"MonthlySchedule.day_of_month must be 1–28, got {self.day_of_month!r}."
            )
