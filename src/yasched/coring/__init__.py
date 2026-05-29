"""Core domain classes: plain data holders for layouts, topics, events, and tasks."""

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

__all__ = [
    "Weekday",
    "WeeklyAppointment",
    "TaskStatus",
    "EffortRange",
    "EventLink",
    "RelationType",
    "TaskRelation",
    "BackgroundStyle",
    "SolidBackground",
    "GradientTopRightBackground",
    "GradientBottomLeftBackground",
    "BorderStyle",
    "IconStyle",
    "ShapeStyle",
    "PinStyle",
    "Layout",
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
