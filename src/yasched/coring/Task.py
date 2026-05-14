"""Unit of work with optional deadline, recurrence, and subtask hierarchy."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field

from yasched.coring._shared import BlockedBy, EffortRange, EventLink, TaskStatus
from yasched.coring.Layout import Layout
from yasched.coring.Schedule import Schedule


@dataclass(frozen=True)
class Task:
    """Plain data holder for a task parsed from YAML."""

    id: str
    name: str
    topic_id: str | None = None
    parent_id: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    deadline: datetime.date | None = None
    priority: int | None = None
    status: TaskStatus = TaskStatus.TODO
    effort: EffortRange | None = None
    schedules: list[Schedule] = field(default_factory=list)
    event_links: list[EventLink] = field(default_factory=list)
    blocked_by: list[BlockedBy] = field(default_factory=list)
    layout: Layout | str | None = None

    def __post_init__(self) -> None:
        if self.schedules and self.deadline is not None:
            raise ValueError(
                "Task may not have both 'schedules' and 'deadline'; the schedule defines timing."
            )
