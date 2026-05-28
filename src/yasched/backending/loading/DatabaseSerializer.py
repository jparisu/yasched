"""Converts a Database of coring objects back to a serializable dict."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

import yaml

from yasched.backending.Database import Database
from yasched.coring._shared import BlockedBy, EventLink, WeeklyAppointment
from yasched.coring.Event import Event
from yasched.coring.Layout import BackgroundStyle, BorderStyle, IconStyle, Layout
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.MultiDaySchedule import MultiDaySchedule
from yasched.coring.Schedule import Schedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring.YearlySchedule import YearlySchedule

_T = TypeVar("_T")


class DatabaseSerializer:
    """Stateless serializer: Database → dict → YAML string."""

    @staticmethod
    def serialize(database: Database) -> dict[str, Any]:
        result: dict[str, Any] = {
            "layouts": [
                DatabaseSerializer._serialize_layout_entry(lay) for lay in database.layouts
            ],
            "topics": [DatabaseSerializer._serialize_topic(t) for t in database.topics],
            "events": [DatabaseSerializer._serialize_event(e) for e in database.events],
            "tasks": [DatabaseSerializer._serialize_task(t) for t in database.tasks],
        }
        return result

    @staticmethod
    def to_yaml(database: Database) -> str:
        return yaml.dump(
            DatabaseSerializer.serialize(database),
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_layout_entry(layout: Layout) -> dict[str, Any]:
        return DatabaseSerializer._layout_to_dict(layout)

    @staticmethod
    def _serialize_layout(layout: Layout | str | None) -> Any:
        if layout is None:
            return None
        if isinstance(layout, str):
            return layout
        return DatabaseSerializer._layout_to_dict(layout)

    @staticmethod
    def _layout_to_dict(layout: Layout) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if layout.id is not None:
            d["id"] = layout.id
        if layout.background is not None:
            d["background"] = DatabaseSerializer._serialize_background(layout.background)
        if layout.border is not None:
            d["border"] = DatabaseSerializer._serialize_border(layout.border)
        if layout.icon is not None:
            d["icon"] = DatabaseSerializer._serialize_icon(layout.icon)
        return d

    @staticmethod
    def _serialize_background(bg: BackgroundStyle) -> dict[str, Any]:
        d: dict[str, Any] = {"type": bg.type}
        if bg.color is not None:
            d["color"] = bg.color.to_hex()
        if bg.colors is not None:
            d["colors"] = [c.to_hex() for c in bg.colors]
        return d

    @staticmethod
    def _serialize_border(border: BorderStyle) -> dict[str, Any]:
        return {"type": border.type, "width": border.width, "color": border.color.to_hex()}

    @staticmethod
    def _serialize_icon(icon: IconStyle) -> dict[str, Any]:
        return {"type": icon.type, "value": icon.value}

    # ------------------------------------------------------------------
    # Topic
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_topic(topic: Topic) -> dict[str, Any]:
        d: dict[str, Any] = {"id": topic.id, "name": topic.name}
        if topic.description is not None:
            d["description"] = topic.description
        if topic.tags:
            d["tags"] = list(topic.tags)
        if topic.parent_ids:
            d["parents"] = list(topic.parent_ids)
        layout = DatabaseSerializer._serialize_layout(topic.layout)
        if layout is not None:
            d["layout"] = layout
        return d

    # ------------------------------------------------------------------
    # Event
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_event(event: Event) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": event.id,
            "topic": event.topic_id,
            "name": event.name,
        }
        if event.description is not None:
            d["description"] = event.description
        if event.location is not None:
            d["location"] = event.location
        schedules = [DatabaseSerializer._serialize_schedule(s) for s in event.schedules]
        d["schedule"] = schedules[0] if len(schedules) == 1 else schedules
        layout = DatabaseSerializer._serialize_layout(event.layout)
        if layout is not None:
            d["layout"] = layout
        if event.blocking_level is not None:
            d["blocking_level"] = event.blocking_level
        return d

    # ------------------------------------------------------------------
    # Task
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_task(task: Task) -> dict[str, Any]:
        d: dict[str, Any] = {"id": task.id, "name": task.name}
        if task.topic_id is not None:
            d["topic"] = task.topic_id
        if task.parent_id is not None:
            d["parent"] = task.parent_id
        if task.description is not None:
            d["description"] = task.description
        if task.tags:
            d["tags"] = list(task.tags)
        if task.deadline is not None:
            d["deadline"] = task.deadline.isoformat()
        if task.priority is not None:
            d["priority"] = task.priority
        d["status"] = task.status.value
        if task.effort is not None:
            d["effort"] = {"min": str(task.effort.min), "max": str(task.effort.max)}
        if task.schedules:
            schedules = [DatabaseSerializer._serialize_schedule(s) for s in task.schedules]
            d["schedule"] = schedules[0] if len(schedules) == 1 else schedules
        if task.event_links:
            d["events"] = [
                DatabaseSerializer._serialize_event_link(link) for link in task.event_links
            ]
        if task.blocked_by:
            d["blocked"] = [DatabaseSerializer._serialize_blocked_by(b) for b in task.blocked_by]
        layout = DatabaseSerializer._serialize_layout(task.layout)
        if layout is not None:
            d["layout"] = layout
        return d

    # ------------------------------------------------------------------
    # Schedule
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_schedule(schedule: Schedule) -> dict[str, Any]:
        if isinstance(schedule, SingleDaySchedule):
            d: dict[str, Any] = {"day": schedule.day.isoformat()}
            if schedule.start_time is not None:
                d["start_time"] = schedule.start_time.strftime("%H:%M")
            if schedule.duration is not None:
                d["duration"] = str(schedule.duration)
            return d
        if isinstance(schedule, MultiDaySchedule):
            return {
                "start_day": schedule.start_day.isoformat(),
                "end_day": schedule.end_day.isoformat(),
            }
        if isinstance(schedule, WeeklySchedule):
            d = {"type": "weekly"}
            appts = schedule.appointments
            if appts and _all_same(appts, lambda a: (a.start_time, a.duration, a.end_time)):
                d["week_days"] = [a.week_day.value for a in appts]
                d["start_time"] = appts[0].start_time.strftime("%H:%M")
                if appts[0].duration is not None:
                    d["duration"] = str(appts[0].duration)
                if appts[0].end_time is not None:
                    d["end_time"] = appts[0].end_time.strftime("%H:%M")
            else:
                d["appointments"] = [DatabaseSerializer._serialize_appointment(a) for a in appts]
            if schedule.start_date is not None:
                d["start_date"] = schedule.start_date.isoformat()
            if schedule.end_date is not None:
                d["end_date"] = schedule.end_date.isoformat()
            return d
        if isinstance(schedule, MonthlySchedule):
            d = {
                "type": "monthly",
                "day_of_month": schedule.day_of_month,
                "start_time": schedule.start_time.strftime("%H:%M"),
                "duration": str(schedule.duration),
            }
            if schedule.start_date is not None:
                d["start_date"] = schedule.start_date.isoformat()
            if schedule.end_date is not None:
                d["end_date"] = schedule.end_date.isoformat()
            return d
        if isinstance(schedule, YearlySchedule):
            return {"type": "yearly", "month": schedule.month, "day": schedule.day}
        raise ValueError(f"Unknown schedule type: {type(schedule).__name__}")

    @staticmethod
    def _serialize_appointment(appt: WeeklyAppointment) -> dict[str, Any]:
        d: dict[str, Any] = {
            "week_day": appt.week_day.value,
            "start_time": appt.start_time.strftime("%H:%M"),
        }
        if appt.duration is not None:
            d["duration"] = str(appt.duration)
        if appt.end_time is not None:
            d["end_time"] = appt.end_time.strftime("%H:%M")
        return d

    @staticmethod
    def _serialize_event_link(link: EventLink) -> Any:
        if link.use_as_deadline and link.as_context:
            return link.event_id
        d: dict[str, Any] = {"id": link.event_id}
        if not link.use_as_deadline:
            d["use_as_deadline"] = False
        if not link.as_context:
            d["as_context"] = False
        return d

    @staticmethod
    def _serialize_blocked_by(b: BlockedBy) -> dict[str, Any]:
        d: dict[str, Any] = {"by": b.task_id}
        if b.description is not None:
            d["description"] = b.description
        return d


def _all_same(items: list[_T], key: Callable[[_T], Any]) -> bool:
    if not items:
        return True
    first = key(items[0])
    return all(key(i) == first for i in items[1:])
