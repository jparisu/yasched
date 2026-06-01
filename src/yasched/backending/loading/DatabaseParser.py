"""Converts a plain Python dict (from XymlLoader) into a Database of coring objects."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from yasched.backending.Database import Database
from yasched.backending.loading.DatabaseLoader import DatabaseParseError
from yasched.coring._shared import (
    EffortRange,
    EventLink,
    RelationType,
    TaskRelation,
    TaskStatus,
    Weekday,
    WeeklyAppointment,
)
from yasched.coring.Event import Event
from yasched.coring.Layout import (
    BackgroundStyle,
    BorderStyle,
    GradientBottomLeftBackground,
    GradientTopRightBackground,
    IconStyle,
    Layout,
    PinStyle,
    ShapeStyle,
    SolidBackground,
)
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.MultiDaySchedule import MultiDaySchedule
from yasched.coring.Schedule import Schedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring.YearlySchedule import YearlySchedule
from yasched.utilizing.coloring.Color import Color
from yasched.utilizing.timing.Duration import Duration
from yasched.utilizing.timing.Time import Time

_VALID_TOP_KEYS = {"layouts", "topics", "events", "tasks", "default_layout"}

_MONTH_NAMES: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


class DatabaseParser:
    """Stateless parser: raw dict → Database."""

    @staticmethod
    def parse(raw: Any, source_path: Path | None = None) -> Database:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"Top-level YAML must be a mapping, got {type(raw).__name__}")
        unknown = set(raw.keys()) - _VALID_TOP_KEYS
        if unknown:
            raise DatabaseParseError(f"Unknown top-level keys: {sorted(unknown)}")
        try:
            layouts = [DatabaseParser._parse_layout_entry(r) for r in raw.get("layouts") or []]
            topics = [DatabaseParser._parse_topic(r) for r in raw.get("topics") or []]
            events = [DatabaseParser._parse_event(r) for r in raw.get("events") or []]
            tasks = [DatabaseParser._parse_task(r) for r in raw.get("tasks") or []]
            default_layout = (
                DatabaseParser._parse_layout_dict(raw["default_layout"])
                if "default_layout" in raw
                else None
            )
        except DatabaseParseError:
            raise
        except Exception as exc:
            raise DatabaseParseError(str(exc)) from exc
        return Database(
            layouts=layouts,
            topics=topics,
            events=events,
            tasks=tasks,
            default_layout=default_layout,
            source_path=source_path,
        )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_layout_entry(raw: Any) -> Layout:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"Layout entry must be a mapping, got {type(raw).__name__}")
        return DatabaseParser._parse_layout_dict(raw)

    @staticmethod
    def _parse_layout(value: Any) -> Layout | str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return DatabaseParser._parse_layout_dict(value)
        raise DatabaseParseError(f"Cannot parse layout from {value!r}")

    @staticmethod
    def _parse_layout_dict(raw: dict[str, Any]) -> Layout:
        id_ = raw.get("id")
        backgrounds: list[BackgroundStyle] = []
        if "background" in raw:
            backgrounds = DatabaseParser._parse_backgrounds(raw["background"])
        border = None
        if "border" in raw:
            border = DatabaseParser._parse_border_style(raw["border"])
        icon = None
        if "icon" in raw:
            icon = DatabaseParser._parse_icon_style(raw["icon"])
        shape = None
        if "shape" in raw:
            shape = DatabaseParser._parse_shape_style(raw["shape"])
        pin = None
        if "pin" in raw:
            pin = DatabaseParser._parse_pin_style(raw["pin"])
        return Layout(
            id=id_, backgrounds=backgrounds, border=border, icon=icon, shape=shape, pin=pin
        )

    @staticmethod
    def _parse_backgrounds(raw: Any) -> list[BackgroundStyle]:
        """Accept a single background dict or a list of background dicts."""
        if isinstance(raw, dict):
            return [DatabaseParser._parse_background_style(raw)]
        if isinstance(raw, list):
            return [DatabaseParser._parse_background_style(item) for item in raw]
        raise DatabaseParseError(f"background must be a mapping or list, got {type(raw).__name__}")

    @staticmethod
    def _parse_background_style(raw: Any) -> BackgroundStyle:
        if not isinstance(raw, dict):
            raise DatabaseParseError(
                f"background entry must be a mapping, got {type(raw).__name__}"
            )
        type_ = str(raw.get("type", "solid"))
        if type_ == "solid":
            color = DatabaseParser._parse_color(raw["color"]) if "color" in raw else Color(0, 0, 0)
            return SolidBackground(color=color)
        if type_ == "gradient_tr":
            if "color" not in raw:
                raise DatabaseParseError("gradient_tr background requires a 'color' field")
            return GradientTopRightBackground(color=DatabaseParser._parse_color(raw["color"]))
        if type_ == "gradient_bl":
            if "color" not in raw:
                raise DatabaseParseError("gradient_bl background requires a 'color' field")
            return GradientBottomLeftBackground(color=DatabaseParser._parse_color(raw["color"]))
        raise DatabaseParseError(
            f"Unknown background type {type_!r}; expected 'solid', 'gradient_tr', or 'gradient_bl'"
        )

    @staticmethod
    def _parse_border_style(raw: Any) -> BorderStyle:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"border must be a mapping, got {type(raw).__name__}")
        type_ = str(raw.get("type", "solid"))
        width = str(raw.get("width", "1px"))
        color = DatabaseParser._parse_color(raw["color"]) if "color" in raw else Color(0, 0, 0)
        return BorderStyle(type=type_, width=width, color=color)

    @staticmethod
    def _parse_icon_style(raw: Any) -> IconStyle:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"icon must be a mapping, got {type(raw).__name__}")
        type_ = str(raw.get("type", "emoji"))
        value = str(raw.get("value", ""))
        return IconStyle(type=type_, value=value)

    @staticmethod
    def _parse_shape_style(raw: Any) -> ShapeStyle:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"shape must be a mapping, got {type(raw).__name__}")
        type_ = str(raw.get("type", "rectangle"))
        radius = str(raw["radius"]) if "radius" in raw else None
        return ShapeStyle(type=type_, radius=radius)

    @staticmethod
    def _parse_pin_style(raw: Any) -> PinStyle:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"pin must be a mapping, got {type(raw).__name__}")
        if "color" not in raw:
            raise DatabaseParseError("pin requires a 'color' field")
        color = DatabaseParser._parse_color(raw["color"])
        icon = str(raw["icon"]) if "icon" in raw else None
        return PinStyle(color=color, icon=icon)

    @staticmethod
    def _parse_color(value: Any) -> Color:
        if isinstance(value, str):
            return Color.from_hex(value) if value.startswith("#") else Color.from_name(value)
        if isinstance(value, dict):
            return Color.from_rgb(
                value.get("r", 0), value.get("g", 0), value.get("b", 0), value.get("a", 1.0)
            )
        raise DatabaseParseError(f"Cannot parse color from {value!r}")

    # ------------------------------------------------------------------
    # Topic
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_topic(raw: Any) -> Topic:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"Topic entry must be a mapping, got {type(raw).__name__}")
        if "id" not in raw:
            raise DatabaseParseError("Topic entry missing required field 'id'")
        if "name" not in raw:
            raise DatabaseParseError(f"Topic '{raw['id']}' missing required field 'name'")
        return Topic(
            id=str(raw["id"]),
            name=str(raw["name"]),
            description=str(raw["description"]) if "description" in raw else None,
            tags=list(raw.get("tags") or []),
            parent_ids=[str(p) for p in (raw.get("parents") or [])],
            layout=DatabaseParser._parse_layout(raw.get("layout")),
        )

    # ------------------------------------------------------------------
    # Event
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_event(raw: Any) -> Event:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"Event entry must be a mapping, got {type(raw).__name__}")
        if "id" not in raw:
            raise DatabaseParseError("Event entry missing required field 'id'")
        if "topic" not in raw:
            raise DatabaseParseError(f"Event '{raw['id']}' missing required field 'topic'")
        if "name" not in raw:
            raise DatabaseParseError(f"Event '{raw['id']}' missing required field 'name'")
        if "schedule" not in raw:
            raise DatabaseParseError(f"Event '{raw['id']}' missing required field 'schedule'")
        schedules = DatabaseParser._parse_schedules(raw["schedule"])
        return Event(
            id=str(raw["id"]),
            topic_id=str(raw["topic"]),
            name=str(raw["name"]),
            description=str(raw["description"]) if "description" in raw else None,
            location=str(raw["location"]) if "location" in raw else None,
            schedules=schedules,
            layout=DatabaseParser._parse_layout(raw.get("layout")),
            blocking_level=int(raw["blocking_level"]) if "blocking_level" in raw else None,
        )

    # ------------------------------------------------------------------
    # Task
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_task(raw: Any) -> Task:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"Task entry must be a mapping, got {type(raw).__name__}")
        if "id" not in raw:
            raise DatabaseParseError("Task entry missing required field 'id'")
        if "name" not in raw:
            raise DatabaseParseError(f"Task '{raw['id']}' missing required field 'name'")
        status_str = str(raw.get("status", "todo"))
        try:
            status = TaskStatus(status_str)
        except ValueError as err:
            raise DatabaseParseError(f"Task '{raw['id']}': unknown status {status_str!r}") from err
        effort = None
        if "effort" in raw:
            effort_raw = raw["effort"]
            effort = EffortRange(
                min=DatabaseParser._parse_duration(effort_raw["min"]),
                max=DatabaseParser._parse_duration(effort_raw["max"]),
            )
        deadline = None
        if "deadline" in raw:
            deadline = DatabaseParser._parse_date(raw["deadline"])
        schedules = DatabaseParser._parse_schedules(raw["schedule"]) if "schedule" in raw else []
        event_links = [DatabaseParser._parse_event_link(e) for e in (raw.get("events") or [])]
        relations = [DatabaseParser._parse_task_relation(r) for r in (raw.get("relations") or [])]
        topic_ids = DatabaseParser._parse_topic_ids(raw)
        return Task(
            id=str(raw["id"]),
            name=str(raw["name"]),
            topic_ids=topic_ids,
            parent_id=str(raw["parent"]) if "parent" in raw else None,
            description=str(raw["description"]) if "description" in raw else None,
            tags=list(raw.get("tags") or []),
            deadline=deadline,
            priority=int(raw["priority"]) if "priority" in raw else None,
            status=status,
            effort=effort,
            schedules=schedules,
            event_links=event_links,
            relations=relations,
            layout=DatabaseParser._parse_layout(raw.get("layout")),
        )

    @staticmethod
    def _parse_topic_ids(raw: dict[str, Any]) -> list[str]:
        """Accept 'topics' (list or string) key."""
        value = raw.get("topics")
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(t) for t in value]
        raise DatabaseParseError(f"'topics' must be a string or list, got {type(value).__name__}")

    # ------------------------------------------------------------------
    # EventLink / TaskRelation
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_event_link(raw: Any) -> EventLink:
        if isinstance(raw, str):
            return EventLink(event_id=raw)
        if isinstance(raw, dict):
            return EventLink(
                event_id=str(raw["id"]),
                use_as_deadline=bool(raw.get("use_as_deadline", True)),
                as_context=bool(raw.get("as_context", True)),
            )
        raise DatabaseParseError(f"Cannot parse event link from {raw!r}")

    @staticmethod
    def _parse_task_relation(raw: Any) -> TaskRelation:
        if isinstance(raw, str):
            return TaskRelation(task_id=raw, type=RelationType.CONNECTED)
        if isinstance(raw, dict):
            if "task" not in raw:
                raise DatabaseParseError(f"Task relation entry must have a 'task' key, got {raw!r}")
            type_str = str(raw.get("type", "connected"))
            try:
                rel_type = RelationType(type_str)
            except ValueError:
                raise DatabaseParseError(
                    f"Unknown relation type {type_str!r}; "
                    f"expected one of {[t.value for t in RelationType]}"
                ) from None
            return TaskRelation(
                task_id=str(raw["task"]),
                type=rel_type,
                description=str(raw["description"]) if "description" in raw else None,
            )
        raise DatabaseParseError(f"Cannot parse task relation from {raw!r}")

    # ------------------------------------------------------------------
    # Schedules
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_schedules(raw: Any) -> list[Schedule]:
        if isinstance(raw, dict):
            return [DatabaseParser._parse_schedule_entry(raw)]
        if isinstance(raw, list):
            return [DatabaseParser._parse_schedule_entry(item) for item in raw]
        raise DatabaseParseError(f"schedule must be a mapping or list, got {type(raw).__name__}")

    @staticmethod
    def _parse_schedule_entry(raw: Any) -> Schedule:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"Schedule entry must be a mapping, got {type(raw).__name__}")
        type_val = str(raw.get("type", "")).lower()
        if type_val == "weekly" or "week_days" in raw or "appointments" in raw:
            return DatabaseParser._parse_weekly(raw)
        if type_val == "monthly" or "day_of_month" in raw:
            return DatabaseParser._parse_monthly(raw)
        if type_val == "yearly" or ("month" in raw and "day" in raw and "day_of_month" not in raw):
            return DatabaseParser._parse_yearly(raw)
        if "start_day" in raw:
            return DatabaseParser._parse_multi_day(raw)
        if "day" in raw:
            return DatabaseParser._parse_single_day(raw)
        raise DatabaseParseError(f"Cannot determine schedule type from keys: {sorted(raw.keys())}")

    @staticmethod
    def _parse_single_day(raw: dict[str, Any]) -> SingleDaySchedule:
        return SingleDaySchedule(
            day=DatabaseParser._parse_date(raw["day"]),
            start_time=DatabaseParser._parse_time(raw["start_time"])
            if "start_time" in raw
            else None,
            duration=DatabaseParser._parse_duration(raw["duration"]) if "duration" in raw else None,
        )

    @staticmethod
    def _parse_multi_day(raw: dict[str, Any]) -> MultiDaySchedule:
        return MultiDaySchedule(
            start_day=DatabaseParser._parse_date(raw["start_day"]),
            end_day=DatabaseParser._parse_date(raw["end_day"]),
        )

    @staticmethod
    def _parse_weekly(raw: dict[str, Any]) -> WeeklySchedule:
        start_date = DatabaseParser._parse_date(raw["start_date"]) if "start_date" in raw else None
        end_date = DatabaseParser._parse_date(raw["end_date"]) if "end_date" in raw else None
        if "appointments" in raw:
            appointments = [DatabaseParser._parse_appointment(a) for a in raw["appointments"]]
        else:
            week_days = raw.get("week_days") or []
            start_time = DatabaseParser._parse_time(raw["start_time"])
            duration = (
                DatabaseParser._parse_duration(raw["duration"]) if "duration" in raw else None
            )
            end_time = DatabaseParser._parse_time(raw["end_time"]) if "end_time" in raw else None
            appointments = [
                WeeklyAppointment(
                    week_day=Weekday.from_string(str(wd)),
                    start_time=start_time,
                    duration=duration,
                    end_time=end_time,
                )
                for wd in week_days
            ]
        return WeeklySchedule(appointments=appointments, start_date=start_date, end_date=end_date)

    @staticmethod
    def _parse_appointment(raw: Any) -> WeeklyAppointment:
        if not isinstance(raw, dict):
            raise DatabaseParseError(f"Appointment must be a mapping, got {type(raw).__name__}")
        return WeeklyAppointment(
            week_day=Weekday.from_string(str(raw["week_day"])),
            start_time=DatabaseParser._parse_time(raw["start_time"]),
            duration=DatabaseParser._parse_duration(raw["duration"]) if "duration" in raw else None,
            end_time=DatabaseParser._parse_time(raw["end_time"]) if "end_time" in raw else None,
        )

    @staticmethod
    def _parse_monthly(raw: dict[str, Any]) -> MonthlySchedule:
        return MonthlySchedule(
            day_of_month=int(raw["day_of_month"]),
            start_time=DatabaseParser._parse_time(raw["start_time"]),
            duration=DatabaseParser._parse_duration(raw["duration"]),
            start_date=DatabaseParser._parse_date(raw["start_date"])
            if "start_date" in raw
            else None,
            end_date=DatabaseParser._parse_date(raw["end_date"]) if "end_date" in raw else None,
        )

    @staticmethod
    def _parse_yearly(raw: dict[str, Any]) -> YearlySchedule:
        month = raw["month"]
        if isinstance(month, str):
            month = _MONTH_NAMES.get(month.lower())
            if month is None:
                raise DatabaseParseError(f"Unknown month name: {raw['month']!r}")
        return YearlySchedule(month=int(month), day=int(raw["day"]))

    # ------------------------------------------------------------------
    # Primitive value parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_date(value: Any) -> datetime.date:
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, str):
            from yasched.utilizing.timing.Date import Date

            return Date.from_string(value).value
        raise DatabaseParseError(f"Cannot parse date from {value!r} ({type(value).__name__})")

    @staticmethod
    def _parse_time(value: Any) -> datetime.time:
        if isinstance(value, datetime.time):
            return value
        if isinstance(value, int):
            # YAML 1.1 sexagesimal: H:MM → H*60 + MM
            hours, minutes = divmod(value, 60)
            return datetime.time(hours, minutes)
        if isinstance(value, str):
            return Time.from_string(value).value
        raise DatabaseParseError(f"Cannot parse time from {value!r} ({type(value).__name__})")

    @staticmethod
    def _parse_duration(value: Any) -> Duration:
        if isinstance(value, str):
            return Duration.from_string(value)
        if isinstance(value, (int, float)):
            return Duration(value=datetime.timedelta(minutes=int(value)))
        raise DatabaseParseError(f"Cannot parse duration from {value!r}")
