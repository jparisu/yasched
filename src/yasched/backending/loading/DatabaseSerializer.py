"""Serialize a :class:`Database` back to the canonical agenda YAML.

This is the inverse of :class:`DatabaseLoader`. It writes a single flat document
(xyml includes and comments are not reconstructed), which is what the CRUD/write
path produces for a UI-managed personal agenda.
"""

from __future__ import annotations

from typing import Any

import yaml

from yasched.backending.Database import Database
from yasched.coring._shared import EventLink, TaskRelation
from yasched.coring.Event import Event
from yasched.coring.Layout import Layout
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


def _prune(d: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose values are None or empty (list/dict/str)."""
    out: dict[str, Any] = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, (list, dict, str)) and len(v) == 0:
            continue
        out[k] = v
    return out


def _layout_to_dict(layout: Layout | None) -> dict[str, Any] | None:
    if layout is None or layout.is_empty():
        return None
    out: dict[str, Any] = {}
    if layout.backgrounds:
        bgs = [{"type": b.type, "color": b.color.to_hex()} for b in layout.backgrounds]
        out["background"] = bgs[0] if len(bgs) == 1 else bgs
    if layout.border is not None:
        out["border"] = {
            "type": layout.border.type,
            "width": layout.border.width,
            "color": layout.border.color.to_hex(),
        }
    if layout.icon is not None:
        out["icon"] = {"type": layout.icon.type, "value": layout.icon.value}
    if layout.pin is not None:
        out["pin"] = _prune({"color": layout.pin.color.to_hex(), "icon": layout.pin.icon})
    if layout.shape is not None:
        out["shape"] = _prune({"type": layout.shape.type, "radius": layout.shape.radius})
    return out


def _schedule_to_dict(sch: Schedule) -> dict[str, Any]:
    times: dict[str, Any] = {}
    if sch.start_time is not None:
        times["start_time"] = sch.start_time.to_hhmm()
    if sch.end_time is not None:
        times["end_time"] = sch.end_time.to_hhmm()
    if sch.duration is not None:
        times["duration"] = str(sch.duration)
    # Optional recurrence bounds (inclusive), for schedules that repeat.
    if sch.start_date is not None:
        times["start_date"] = sch.start_date.to_iso()
    if sch.end_date is not None:
        times["end_date"] = sch.end_date.to_iso()

    if isinstance(sch, WeeklySchedule):
        return {"type": "weekly", "week_days": [d.value for d in sch.week_days], **times}
    if isinstance(sch, MonthlySchedule):
        return {"type": "monthly", "day": sch.day, **times}
    if isinstance(sch, YearlySchedule):
        return {"type": "yearly", "month": sch.month, "day": sch.day, **times}
    if isinstance(sch, SingleDaySchedule):
        return _prune({"type": "single_day", "day": sch.day.to_iso() if sch.day else None, **times})
    if isinstance(sch, MultiDaySchedule):
        return _prune(
            {
                "type": "multi_day",
                "start_day": sch.start_day.to_iso() if sch.start_day else None,
                "end_day": sch.end_day.to_iso() if sch.end_day else None,
                **times,
            }
        )
    return {}


def _relation_to_dict(rel: TaskRelation) -> dict[str, Any]:
    return _prune({"task": rel.task_id, "type": rel.type.value, "description": rel.description})


def _event_link_to_dict(link: EventLink) -> dict[str, Any]:
    out: dict[str, Any] = {"event": link.event_id}
    if link.use_as_deadline:
        out["use_as_deadline"] = True
    if link.as_context:
        out["as_context"] = True
    return out


def _common(entity: Topic | Event | Task) -> dict[str, Any]:
    return {
        "id": entity.id,
        "name": entity.name,
        "description": entity.description,
        "tags": list(entity.tags),
        "traits": list(entity.traits),
        "attributes": dict(entity.attributes),
        "layout": _layout_to_dict(entity.layout),
    }


def topic_to_dict(topic: Topic) -> dict[str, Any]:
    return _prune({**_common(topic), "parent_ids": list(topic.parent_ids)})


def event_to_dict(event: Event) -> dict[str, Any]:
    return _prune(
        {
            **_common(event),
            "topic_ids": list(event.topic_ids),
            "parent_id": event.parent_id,
            "schedules": [_schedule_to_dict(s) for s in event.schedules],
        }
    )


def task_to_dict(task: Task) -> dict[str, Any]:
    return _prune(
        {
            **_common(task),
            "topic_ids": list(task.topic_ids),
            "parent_id": task.parent_id,
            "schedules": [_schedule_to_dict(s) for s in task.schedules],
            "relations": [_relation_to_dict(r) for r in task.relations],
            "event_links": [_event_link_to_dict(e) for e in task.event_links],
        }
    )


def _trait_to_dict(trait: Trait) -> dict[str, Any]:
    return _prune({"attributes": dict(trait.attributes), "layout": _layout_to_dict(trait.layout)})


class DatabaseSerializer:
    """Serialize a Database to the canonical agenda dict / YAML text."""

    @staticmethod
    def entity_to_dict(entity: Topic | Event | Task) -> dict[str, Any]:
        """Serialize one entity to its raw spec dict (own values only)."""
        if isinstance(entity, Topic):
            return topic_to_dict(entity)
        if isinstance(entity, Event):
            return event_to_dict(entity)
        if isinstance(entity, Task):
            return task_to_dict(entity)
        raise TypeError(f"Not a serializable entity: {type(entity).__name__}")

    @staticmethod
    def to_dict(db: Database) -> dict[str, Any]:
        default = _prune(
            {
                "attributes": dict(db.default_attributes),
                "layout": _layout_to_dict(db.default_layout),
            }
        )
        doc: dict[str, Any] = {}
        if default:
            doc["default"] = default
        if db.traits:
            doc["traits"] = {name: _trait_to_dict(t) for name, t in db.traits.items()}
        if db.topics:
            doc["topics"] = [topic_to_dict(t) for t in db.topics.values()]
        if db.events:
            doc["events"] = [event_to_dict(e) for e in db.events.values()]
        if db.tasks:
            doc["tasks"] = [task_to_dict(t) for t in db.tasks.values()]
        return doc

    @staticmethod
    def to_yaml(db: Database) -> str:
        header = "# Managed by yasched. Edited through the app UI.\n"
        body = yaml.safe_dump(
            DatabaseSerializer.to_dict(db),
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
        return header + body
