"""One-off occurrence spanning multiple consecutive calendar days."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from yasched.coring.Schedule import Schedule


@dataclass(frozen=True)
class MultiDaySchedule(Schedule):
    """All-day range schedule; start_day <= end_day enforced."""

    start_day: datetime.date
    end_day: datetime.date

    def __post_init__(self) -> None:
        if self.start_day > self.end_day:
            raise ValueError(
                f"MultiDaySchedule.start_day ({self.start_day}) must be "
                f"<= end_day ({self.end_day})."
            )
