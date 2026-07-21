"""Small support types shared across two or more coring classes."""

from __future__ import annotations

import enum
from dataclasses import dataclass

# Common weekday abbreviations → canonical enum value. Kept at module level
# (not inside the Enum) so it is not coerced into an enum member.
_WEEKDAY_ALIASES = {
    "mon": "monday",
    "tue": "tuesday",
    "tues": "tuesday",
    "wed": "wednesday",
    "weds": "wednesday",
    "thu": "thursday",
    "thur": "thursday",
    "thurs": "thursday",
    "fri": "friday",
    "sat": "saturday",
    "sun": "sunday",
}


class Weekday(enum.Enum):
    """Days of the week."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @staticmethod
    def from_string(s: str) -> Weekday:
        """Parse a weekday name case-insensitively, accepting common abbreviations."""
        key = s.strip().lower()
        key = _WEEKDAY_ALIASES.get(key, key)
        return Weekday(key)

    def index(self) -> int:
        """Monday=0 .. Sunday=6, matching ``datetime.date.weekday()``."""
        return _WEEKDAY_ORDER.index(self)


_WEEKDAY_ORDER = [
    Weekday.MONDAY,
    Weekday.TUESDAY,
    Weekday.WEDNESDAY,
    Weekday.THURSDAY,
    Weekday.FRIDAY,
    Weekday.SATURDAY,
    Weekday.SUNDAY,
]


class RelationType(enum.Enum):
    """Semantics of a relation between two tasks."""

    REQUIRES = "requires"  # hard dependency; source is blocked until target done
    NEEDS = "needs"  # soft dependency; informational
    CONNECTED = "connected"  # related work, no ordering
    SIMILAR = "similar"  # same kind of task, no ordering

    @staticmethod
    def from_string(s: str) -> RelationType:
        return RelationType(s.strip().lower())


@dataclass(frozen=True)
class TaskRelation:
    """A directed relation from one task to another."""

    task_id: str
    type: RelationType = RelationType.CONNECTED
    description: str | None = None


@dataclass(frozen=True)
class EventLink:
    """A reference from a task to a related event."""

    event_id: str
    use_as_deadline: bool = False
    as_context: bool = False
