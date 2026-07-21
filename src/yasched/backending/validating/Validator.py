"""Consistency checks over a parsed :class:`Database`.

Reports structured :class:`Issue`s (errors and warnings) without mutating the
database. Errors indicate broken references or impossible schedules; warnings
indicate likely mistakes that still load.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from yasched.backending.Database import Database
from yasched.coring.Schedule import (
    MonthlySchedule,
    MultiDaySchedule,
    SingleDaySchedule,
    WeeklySchedule,
    YearlySchedule,
)
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic


class Severity(enum.Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    """One validation finding."""

    severity: Severity
    code: str
    message: str
    entity_kind: str  # "topic" | "event" | "task" | "trait" | ""
    entity_id: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "entityKind": self.entity_kind,
            "entityId": self.entity_id,
        }


class Validator:
    """Runs all consistency checks over a database."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._issues: list[Issue] = []

    def validate(self) -> list[Issue]:
        self._issues = []
        self._check_duplicates()
        self._check_topics()
        self._check_events()
        self._check_tasks()
        return list(self._issues)

    # -- helpers -------------------------------------------------------

    def _err(self, code: str, msg: str, kind: str, eid: str) -> None:
        self._issues.append(Issue(Severity.ERROR, code, msg, kind, eid))

    def _warn(self, code: str, msg: str, kind: str, eid: str) -> None:
        self._issues.append(Issue(Severity.WARNING, code, msg, kind, eid))

    def _check_traits(self, kind: str, eid: str, traits: list[str]) -> None:
        for name in traits:
            if name not in self._db.traits:
                self._err("unknown-trait", f"references unknown trait '{name}'", kind, eid)

    def _check_topic_refs(self, kind: str, eid: str, topic_ids: list[str]) -> None:
        for tid in topic_ids:
            if tid not in self._db.topics:
                self._err("unknown-topic", f"references unknown topic '{tid}'", kind, eid)

    # -- duplicates ----------------------------------------------------

    def _check_duplicates(self) -> None:
        for kind, eid in self._db.duplicate_ids:
            self._warn(
                "duplicate-id",
                f"duplicate {kind} id '{eid}' — a later definition overrode an earlier one",
                kind,
                eid,
            )

    # -- topics --------------------------------------------------------

    def _check_topics(self) -> None:
        for topic in self._db.topics.values():
            self._check_traits("topic", topic.id, topic.traits)
            for parent in topic.parent_ids:
                if parent == topic.id:
                    self._err("self-parent", "is its own parent", "topic", topic.id)
                elif parent not in self._db.topics:
                    self._err(
                        "unknown-parent",
                        f"references unknown parent topic '{parent}'",
                        "topic",
                        topic.id,
                    )
            if self._has_cycle(topic):
                self._err("topic-cycle", "is part of a parent cycle", "topic", topic.id)

    def _has_cycle(self, topic: Topic) -> bool:
        seen: set[str] = set()
        stack = [topic.id]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            node = self._db.topics.get(current)
            if node is None:
                continue
            for parent in node.parent_ids:
                if parent == topic.id:
                    return True
                stack.append(parent)
        return False

    # -- events --------------------------------------------------------

    def _check_events(self) -> None:
        for event in self._db.events.values():
            self._check_traits("event", event.id, event.traits)
            self._check_topic_refs("event", event.id, event.topic_ids)
            if event.parent_id is not None:
                if event.parent_id == event.id:
                    self._err("self-parent", "is its own parent", "event", event.id)
                elif event.parent_id not in self._db.events:
                    self._err(
                        "unknown-parent",
                        f"sub-event references unknown parent event '{event.parent_id}'",
                        "event",
                        event.id,
                    )
            if not event.schedules and event.parent_id is None:
                self._warn(
                    "no-schedule", "has no schedules and will never occur", "event", event.id
                )
            for sch in event.schedules:
                self._check_schedule("event", event.id, sch)

    # -- tasks ---------------------------------------------------------

    def _check_tasks(self) -> None:
        for task in self._db.tasks.values():
            self._check_traits("task", task.id, task.traits)
            self._check_topic_refs("task", task.id, task.topic_ids)
            if task.parent_id is not None:
                if task.parent_id == task.id:
                    self._err("self-parent", "is its own parent", "task", task.id)
                elif task.parent_id not in self._db.tasks:
                    self._err(
                        "unknown-parent",
                        f"subtask references unknown parent task '{task.parent_id}'",
                        "task",
                        task.id,
                    )
            if self._task_parent_cycle(task):
                self._err("task-cycle", "is part of a parent cycle", "task", task.id)
            for rel in task.relations:
                if rel.task_id not in self._db.tasks:
                    self._err(
                        "unknown-relation",
                        f"relation targets unknown task '{rel.task_id}'",
                        "task",
                        task.id,
                    )
            for link in task.event_links:
                if link.event_id not in self._db.events:
                    self._err(
                        "unknown-event-link",
                        f"event_link targets unknown event '{link.event_id}'",
                        "task",
                        task.id,
                    )
            for sch in task.schedules:
                self._check_schedule("task", task.id, sch)

    def _task_parent_cycle(self, task: Task) -> bool:
        seen: set[str] = set()
        current: str | None = task.parent_id
        while current is not None:
            if current == task.id:
                return True
            if current in seen:
                return False
            seen.add(current)
            node = self._db.tasks.get(current)
            current = node.parent_id if node else None
        return False

    # -- schedules -----------------------------------------------------

    def _check_schedule(self, kind: str, eid: str, sch: object) -> None:
        if isinstance(sch, WeeklySchedule):
            if not sch.week_days:
                self._err("bad-schedule", "weekly schedule has no week_days", kind, eid)
        elif isinstance(sch, MonthlySchedule):
            if not 1 <= sch.day <= 31:
                self._err("bad-schedule", f"monthly day {sch.day} out of range 1-31", kind, eid)
        elif isinstance(sch, YearlySchedule):
            if not 1 <= sch.month <= 12:
                self._err("bad-schedule", f"yearly month {sch.month} out of range 1-12", kind, eid)
            if not 1 <= sch.day <= 31:
                self._err("bad-schedule", f"yearly day {sch.day} out of range 1-31", kind, eid)
        elif isinstance(sch, SingleDaySchedule):
            if sch.day is None:
                self._err("bad-schedule", "single_day schedule has no day", kind, eid)
        elif isinstance(sch, MultiDaySchedule):
            if sch.start_day is None or sch.end_day is None:
                self._err("bad-schedule", "multi_day schedule missing start/end day", kind, eid)
            elif sch.end_day < sch.start_day:
                self._err("bad-schedule", "multi_day end_day is before start_day", kind, eid)
        if (
            getattr(sch, "end_time", None) is not None
            and getattr(sch, "duration", None) is not None
        ):
            self._warn(
                "schedule-redundant-time",
                "schedule sets both end_time and duration (duration is ignored)",
                kind,
                eid,
            )


def validate_database(db: Database) -> list[Issue]:
    """Convenience: run all checks and return the issues."""
    return Validator(db).validate()
