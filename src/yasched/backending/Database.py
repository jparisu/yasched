"""Raw and resolved database containers, plus resolved-entity wrappers."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path

from yasched.coring._shared import BlockedBy, EffortRange, EventLink, TaskStatus
from yasched.coring.Event import Event
from yasched.coring.Layout import Layout
from yasched.coring.Schedule import Schedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic


@dataclass
class Database:
    """Raw, unresolved container of parsed coring objects."""

    layouts: list[Layout]
    topics: list[Topic]
    events: list[Event]
    tasks: list[Task]
    source_path: Path | None = None


@dataclass
class ResolvedTopic:
    """Topic with resolved parents, backlinks, and computed effective values."""

    raw: Topic
    parents: list[ResolvedTopic]
    children: list[ResolvedTopic]
    effective_tags: list[str]
    effective_layout: Layout | None

    @property
    def id(self) -> str:
        return self.raw.id

    @property
    def name(self) -> str:
        return self.raw.name

    @property
    def description(self) -> str | None:
        return self.raw.description


@dataclass
class ResolvedEvent:
    """Event with resolved topic and effective layout."""

    raw: Event
    topic: ResolvedTopic
    effective_layout: Layout | None

    @property
    def id(self) -> str:
        return self.raw.id

    @property
    def name(self) -> str:
        return self.raw.name

    @property
    def description(self) -> str | None:
        return self.raw.description

    @property
    def location(self) -> str | None:
        return self.raw.location

    @property
    def schedules(self) -> list[Schedule]:
        return self.raw.schedules

    @property
    def blocking_level(self) -> int | None:
        return self.raw.blocking_level


@dataclass
class ResolvedTask:
    """Task with resolved topic, parent, events, blockers, and inherited fields."""

    raw: Task
    topic: ResolvedTopic
    parent: ResolvedTask | None
    children: list[ResolvedTask]
    effective_tags: list[str]
    effective_layout: Layout | None
    effective_deadline: datetime.date | None
    linked_events: list[ResolvedEvent]
    blocking_tasks: list[ResolvedTask]

    @property
    def id(self) -> str:
        return self.raw.id

    @property
    def name(self) -> str:
        return self.raw.name

    @property
    def description(self) -> str | None:
        return self.raw.description

    @property
    def priority(self) -> int | None:
        return self.raw.priority

    @property
    def status(self) -> TaskStatus:
        return self.raw.status

    @property
    def effort(self) -> EffortRange | None:
        return self.raw.effort

    @property
    def schedules(self) -> list[Schedule]:
        return self.raw.schedules

    @property
    def blocked_by(self) -> list[BlockedBy]:
        return self.raw.blocked_by

    @property
    def event_links(self) -> list[EventLink]:
        return self.raw.event_links


@dataclass
class ResolvedDatabase:
    """Validated, reference-resolved database."""

    layouts: dict[str, Layout]
    topics: dict[str, ResolvedTopic]
    events: dict[str, ResolvedEvent]
    tasks: dict[str, ResolvedTask]
    root_topics: list[ResolvedTopic] = field(default_factory=list)
    root_tasks: list[ResolvedTask] = field(default_factory=list)
