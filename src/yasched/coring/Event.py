"""Time-bound occurrence belonging to a topic."""

from __future__ import annotations

from dataclasses import dataclass

from yasched.coring.Layout import Layout
from yasched.coring.Schedule import Schedule


@dataclass(frozen=True)
class Event:
    """Plain data holder for an event parsed from YAML."""

    id: str
    topic_id: str
    name: str
    schedules: list[Schedule]
    description: str | None = None
    location: str | None = None
    layout: Layout | str | None = None
    blocking_level: int | None = None

    def __post_init__(self) -> None:
        if not self.schedules:
            raise ValueError("Event.schedules must not be empty.")
