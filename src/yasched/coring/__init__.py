"""Core domain data holders: entities and value objects.

These are plain, frozen dataclasses parsed from the configuration. They do not
resolve references, apply inheritance, or compute schedules — that is
``backending``'s job. ``coring`` imports ``utilizing`` only.
"""

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

__all__ = [
    "Weekday",
    "RelationType",
    "TaskRelation",
    "EventLink",
    "Background",
    "Border",
    "Icon",
    "Pin",
    "Shape",
    "Layout",
    "Trait",
    "Schedule",
    "WeeklySchedule",
    "MonthlySchedule",
    "YearlySchedule",
    "SingleDaySchedule",
    "MultiDaySchedule",
    "Topic",
    "Event",
    "Task",
]
