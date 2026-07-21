"""Parse an xyml document into a :class:`Database` of ``coring`` objects.

Parsing is lenient: unknown keys are ignored and missing optional keys fall back
to sensible defaults. Structural/consistency validation is a later phase.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from yasched.backending.Database import Database
from yasched.coring._shared import EventLink, RelationType, TaskRelation, Weekday
from yasched.coring.Event import Event
from yasched.coring.Layout import Background, Border, Icon, Layout, Pin, Shape
from yasched.coring.Schedule import (
    MonthlySchedule,
    MultiDaySchedule,
    Schedule,
    SingleDaySchedule,
    WeeklySchedule,
    YearlySchedule,
)
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.Trait import Trait
from yasched.utilizing.coloring.Color import Color
from yasched.utilizing.timing.Date import Date
from yasched.utilizing.timing.Duration import Duration
from yasched.utilizing.timing.Time import Time
from yasched.utilizing.xyml.XymlLoader import XymlLoader


class DatabaseLoadError(ValueError):
    """Raised when a document cannot be parsed into a Database."""


def _as_list(value: Any) -> list[Any]:
    """Accept a single scalar or a list; always return a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _parse_color(value: Any) -> Color:
    """A color is a hex string (``#rrggbb``) or a registered color name."""
    if isinstance(value, Color):
        return value
    s = str(value).strip()
    if s.startswith("#"):
        return Color.from_hex(s)
    return Color.from_name(s)


def _parse_time(value: Any) -> Time | None:
    return None if value is None else Time.from_string(str(value))


def _parse_duration(value: Any) -> Duration | None:
    return None if value is None else Duration.from_string(str(value))


def _parse_date(value: Any) -> Date | None:
    return None if value is None else Date.from_string(str(value))


class DatabaseLoader:
    """Loads and parses a configuration into a :class:`Database`."""

    @staticmethod
    def load(path: str | Path) -> Database:
        """Load *path* (following xyml directives) and parse it."""
        doc = XymlLoader.load(path)
        return DatabaseLoader.from_dict(doc)

    @staticmethod
    def loads(content: str, base_path: str | Path | None = None) -> Database:
        doc = XymlLoader.loads(content, base_path)
        return DatabaseLoader.from_dict(doc)

    @staticmethod
    def from_dict(doc: Any) -> Database:
        if doc is None:
            return Database()
        if not isinstance(doc, dict):
            raise DatabaseLoadError(
                f"Top-level document must be a mapping, got {type(doc).__name__}"
            )

        default = doc.get("default") or {}
        db = Database(
            default_attributes=dict(default.get("attributes") or {}),
            default_layout=DatabaseLoader._parse_layout(default.get("layout")),
        )

        for name, raw in (doc.get("traits") or {}).items():
            db.traits[name] = DatabaseLoader._parse_trait(name, raw)
        for raw in _as_list(doc.get("topics")):
            topic = DatabaseLoader._parse_topic(raw)
            if topic.id in db.topics:
                db.duplicate_ids.append(("topic", topic.id))
            db.topics[topic.id] = topic
        for raw in _as_list(doc.get("events")):
            event = DatabaseLoader._parse_event(raw)
            if event.id in db.events:
                db.duplicate_ids.append(("event", event.id))
            db.events[event.id] = event
        for raw in _as_list(doc.get("tasks")):
            task = DatabaseLoader._parse_task(raw)
            if task.id in db.tasks:
                db.duplicate_ids.append(("task", task.id))
            db.tasks[task.id] = task
        return db

    # ------------------------------------------------------------------
    # Public single-entity parsing (used by write/CRUD paths)
    # ------------------------------------------------------------------

    @staticmethod
    def parse_entity(kind: str, raw: Any) -> Topic | Event | Task:
        """Parse one raw entity dict of the given *kind* (``topics``/``events``/``tasks``)."""
        if kind == "topics":
            return DatabaseLoader._parse_topic(raw)
        if kind == "events":
            return DatabaseLoader._parse_event(raw)
        if kind == "tasks":
            return DatabaseLoader._parse_task(raw)
        raise DatabaseLoadError(f"Unknown entity kind: {kind!r}")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_layout(raw: Any) -> Layout | None:
        if not raw:
            return None
        if not isinstance(raw, dict):
            raise DatabaseLoadError(f"layout must be a mapping, got {type(raw).__name__}")

        backgrounds: list[Background] = []
        bg = raw.get("background")
        for entry in _as_list(bg):
            if entry is None:
                continue
            backgrounds.append(
                Background(
                    type=str(entry.get("type", "solid")), color=_parse_color(entry.get("color"))
                )
            )

        border = None
        if raw.get("border"):
            b = raw["border"]
            border = Border(
                type=str(b.get("type", "solid")),
                width=str(b.get("width", "1px")),
                color=_parse_color(b.get("color")),
            )

        icon = None
        if raw.get("icon"):
            i = raw["icon"]
            icon = Icon(type=str(i.get("type", "emoji")), value=str(i.get("value", "")))

        pin = None
        if raw.get("pin"):
            p = raw["pin"]
            pin = Pin(
                color=_parse_color(p.get("color")), icon=(str(p["icon"]) if p.get("icon") else None)
            )

        shape = None
        if raw.get("shape"):
            s = raw["shape"]
            shape = Shape(
                type=str(s.get("type", "rounded")),
                radius=(str(s["radius"]) if s.get("radius") else None),
            )

        return Layout(backgrounds=backgrounds, border=border, icon=icon, pin=pin, shape=shape)

    # ------------------------------------------------------------------
    # Trait
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_trait(name: str, raw: Any) -> Trait:
        raw = raw or {}
        return Trait(
            name=name,
            attributes=dict(raw.get("attributes") or {}),
            layout=DatabaseLoader._parse_layout(raw.get("layout")),
        )

    # ------------------------------------------------------------------
    # Schedule
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_schedule(raw: Any) -> Schedule:
        if not isinstance(raw, dict):
            raise DatabaseLoadError(f"schedule must be a mapping, got {type(raw).__name__}")
        kind = str(raw.get("type", "")).strip().lower()
        common: dict[str, Any] = {
            "start_time": _parse_time(raw.get("start_time")),
            "end_time": _parse_time(raw.get("end_time")),
            "duration": _parse_duration(raw.get("duration")),
            "start_date": _parse_date(raw.get("start_date")),
            "end_date": _parse_date(raw.get("end_date")),
        }
        if kind == "weekly":
            days = tuple(Weekday.from_string(str(d)) for d in _as_list(raw.get("week_days")))
            return WeeklySchedule(week_days=days, **common)
        if kind == "monthly":
            return MonthlySchedule(day=int(raw.get("day", 1)), **common)
        if kind == "yearly":
            return YearlySchedule(
                month=int(raw.get("month", 1)), day=int(raw.get("day", 1)), **common
            )
        if kind == "single_day":
            return SingleDaySchedule(day=_parse_date(raw.get("day")), **common)
        if kind == "multi_day":
            return MultiDaySchedule(
                start_day=_parse_date(raw.get("start_day")),
                end_day=_parse_date(raw.get("end_day")),
                **common,
            )
        raise DatabaseLoadError(f"Unknown schedule type: {kind!r}")

    # ------------------------------------------------------------------
    # Entities
    # ------------------------------------------------------------------

    @staticmethod
    def _common_ids(raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(raw["id"]),
            "name": str(raw.get("name", raw["id"])),
            "description": (
                str(raw["description"]) if raw.get("description") is not None else None
            ),
            "tags": [str(t) for t in _as_list(raw.get("tags"))],
            "traits": [str(t) for t in _as_list(raw.get("traits"))],
            "attributes": dict(raw.get("attributes") or {}),
            "layout": DatabaseLoader._parse_layout(raw.get("layout")),
        }

    @staticmethod
    def _parse_topic(raw: Any) -> Topic:
        DatabaseLoader._require_mapping_with_id(raw, "topic")
        return Topic(
            parent_ids=[str(p) for p in _as_list(raw.get("parent_ids"))],
            **DatabaseLoader._common_ids(raw),
        )

    @staticmethod
    def _parse_event(raw: Any) -> Event:
        DatabaseLoader._require_mapping_with_id(raw, "event")
        # accept `topics` or `topic_ids`, single string or list
        topics = raw.get("topic_ids", raw.get("topics"))
        return Event(
            topic_ids=[str(t) for t in _as_list(topics)],
            parent_id=(str(raw["parent_id"]) if raw.get("parent_id") else None),
            schedules=[DatabaseLoader._parse_schedule(s) for s in _as_list(raw.get("schedules"))],
            **DatabaseLoader._common_ids(raw),
        )

    @staticmethod
    def _parse_task(raw: Any) -> Task:
        DatabaseLoader._require_mapping_with_id(raw, "task")
        topics = raw.get("topic_ids", raw.get("topics"))
        return Task(
            topic_ids=[str(t) for t in _as_list(topics)],
            parent_id=(str(raw["parent_id"]) if raw.get("parent_id") else None),
            schedules=[DatabaseLoader._parse_schedule(s) for s in _as_list(raw.get("schedules"))],
            relations=[DatabaseLoader._parse_relation(r) for r in _as_list(raw.get("relations"))],
            event_links=[
                DatabaseLoader._parse_event_link(e) for e in _as_list(raw.get("event_links"))
            ],
            **DatabaseLoader._common_ids(raw),
        )

    @staticmethod
    def _parse_relation(raw: Any) -> TaskRelation:
        if isinstance(raw, str):  # shorthand → connected
            return TaskRelation(task_id=raw, type=RelationType.CONNECTED)
        return TaskRelation(
            task_id=str(raw["task"]),
            type=RelationType.from_string(str(raw.get("type", "connected"))),
            description=(str(raw["description"]) if raw.get("description") else None),
        )

    @staticmethod
    def _parse_event_link(raw: Any) -> EventLink:
        if isinstance(raw, str):
            return EventLink(event_id=raw)
        return EventLink(
            event_id=str(raw["event"]),
            use_as_deadline=bool(raw.get("use_as_deadline", False)),
            as_context=bool(raw.get("as_context", False)),
        )

    @staticmethod
    def _require_mapping_with_id(raw: Any, kind: str) -> None:
        if not isinstance(raw, dict):
            raise DatabaseLoadError(f"Each {kind} must be a mapping, got {type(raw).__name__}")
        if "id" not in raw:
            raise DatabaseLoadError(f"Each {kind} requires an 'id'; got keys {sorted(raw)}")
