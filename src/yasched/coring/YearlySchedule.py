"""Schedule that repeats once per year on a fixed month and day."""

from __future__ import annotations

from dataclasses import dataclass

from yasched.coring.Schedule import Schedule


@dataclass(frozen=True)
class YearlySchedule(Schedule):
    """Annual schedule on a fixed month/day."""

    month: int
    day: int

    def __post_init__(self) -> None:
        if not (1 <= self.month <= 12):
            raise ValueError(f"YearlySchedule.month must be 1–12, got {self.month!r}.")
        if not (1 <= self.day <= 31):
            raise ValueError(f"YearlySchedule.day must be 1–31, got {self.day!r}.")
