"""Small support types shared across two or more coring classes."""

from __future__ import annotations

import datetime
import enum
from dataclasses import dataclass

from yasched.utilizing.timing.Duration import Duration


class Weekday(enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @staticmethod
    def from_string(s: str) -> Weekday:
        _ALIASES: dict[str, str] = {
            "mon": "monday",
            "tue": "tuesday",
            "wed": "wednesday",
            "thu": "thursday",
            "fri": "friday",
            "sat": "saturday",
            "sun": "sunday",
        }
        normalised = s.lower()
        canonical = _ALIASES.get(normalised, normalised)
        try:
            return Weekday(canonical)
        except ValueError:
            raise ValueError(f"Unknown weekday: {s!r}") from None


@dataclass(frozen=True)
class WeeklyAppointment:
    """One time slot within a weekly recurring schedule."""

    week_day: Weekday
    start_time: datetime.time
    end_time: datetime.time | None = None
    duration: Duration | None = None

    def __post_init__(self) -> None:
        if self.end_time is not None and self.duration is not None:
            raise ValueError("Exactly one of 'end_time' or 'duration' must be set, not both.")
        if self.end_time is None and self.duration is None:
            raise ValueError("Exactly one of 'end_time' or 'duration' must be set.")


class TaskStatus(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class EffortRange:
    """Estimated effort bounds for a task."""

    min: Duration
    max: Duration

    def __post_init__(self) -> None:
        if self.min.to_minutes() > self.max.to_minutes():
            raise ValueError(f"EffortRange.min ({self.min}) must not exceed max ({self.max}).")


@dataclass(frozen=True)
class EventLink:
    """Reference from a task to a related event."""

    event_id: str
    use_as_deadline: bool = True
    as_context: bool = True


@dataclass(frozen=True)
class BlockedBy:
    """Dependency declaration: another task that must complete first."""

    task_id: str
    description: str | None = None
