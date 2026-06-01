"""Shared schema types: Color, Duration, Layout, Schedule discriminated unions."""

from __future__ import annotations

import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from yasched.coring._shared import Weekday, WeeklyAppointment
from yasched.coring.Layout import (
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
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring.YearlySchedule import YearlySchedule
from yasched.utilizing.coloring.Color import Color
from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# Schedule schemas
# ---------------------------------------------------------------------------


class SingleDayScheduleSchema(BaseModel):
    type: Literal["single_day"] = "single_day"
    day: datetime.date
    start_time: datetime.time | None = None
    duration: str | None = None


class MultiDayScheduleSchema(BaseModel):
    type: Literal["multi_day"] = "multi_day"
    start_day: datetime.date
    end_day: datetime.date


class WeeklyAppointmentSchema(BaseModel):
    week_day: str
    start_time: datetime.time
    end_time: datetime.time | None = None
    duration: str | None = None


class WeeklyScheduleSchema(BaseModel):
    type: Literal["weekly"] = "weekly"
    appointments: list[WeeklyAppointmentSchema]
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None


class MonthlyScheduleSchema(BaseModel):
    type: Literal["monthly"] = "monthly"
    day_of_month: int
    start_time: datetime.time
    duration: str
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None


class YearlyScheduleSchema(BaseModel):
    type: Literal["yearly"] = "yearly"
    month: int
    day: int


ScheduleSchema = Annotated[
    SingleDayScheduleSchema
    | MultiDayScheduleSchema
    | WeeklyScheduleSchema
    | MonthlyScheduleSchema
    | YearlyScheduleSchema,
    Field(discriminator="type"),
]

# ---------------------------------------------------------------------------
# Layout schemas
# ---------------------------------------------------------------------------


class SolidBackgroundSchema(BaseModel):
    type: Literal["solid"] = "solid"
    color: str


class GradientTRBackgroundSchema(BaseModel):
    type: Literal["gradient_tr"] = "gradient_tr"
    color: str


class GradientBLBackgroundSchema(BaseModel):
    type: Literal["gradient_bl"] = "gradient_bl"
    color: str


BackgroundSchema = Annotated[
    SolidBackgroundSchema | GradientTRBackgroundSchema | GradientBLBackgroundSchema,
    Field(discriminator="type"),
]


class BorderStyleSchema(BaseModel):
    type: str
    width: str
    color: str


class IconStyleSchema(BaseModel):
    type: str
    value: str


class ShapeStyleSchema(BaseModel):
    type: str
    radius: str | None = None


class PinStyleSchema(BaseModel):
    color: str
    icon: str | None = None


class LayoutSchema(BaseModel):
    id: str | None = None
    backgrounds: list[BackgroundSchema] = Field(default_factory=list)
    border: BorderStyleSchema | None = None
    icon: IconStyleSchema | None = None
    shape: ShapeStyleSchema | None = None
    pin: PinStyleSchema | None = None


# ---------------------------------------------------------------------------
# Python → Schema converters (read path)
# ---------------------------------------------------------------------------


def color_to_hex(color: Color) -> str:
    return color.to_hex()


def duration_to_str(duration: Duration) -> str:
    return str(duration)


def schedule_to_schema(s: Schedule) -> ScheduleSchema:
    if isinstance(s, SingleDaySchedule):
        return SingleDayScheduleSchema(
            day=s.day,
            start_time=s.start_time,
            duration=str(s.duration) if s.duration else None,
        )
    if isinstance(s, MultiDaySchedule):
        return MultiDayScheduleSchema(start_day=s.start_day, end_day=s.end_day)
    if isinstance(s, WeeklySchedule):
        return WeeklyScheduleSchema(
            appointments=[
                WeeklyAppointmentSchema(
                    week_day=a.week_day.value,
                    start_time=a.start_time,
                    end_time=a.end_time,
                    duration=str(a.duration) if a.duration else None,
                )
                for a in s.appointments
            ],
            start_date=s.start_date,
            end_date=s.end_date,
        )
    if isinstance(s, MonthlySchedule):
        return MonthlyScheduleSchema(
            day_of_month=s.day_of_month,
            start_time=s.start_time,
            duration=str(s.duration),
            start_date=s.start_date,
            end_date=s.end_date,
        )
    if isinstance(s, YearlySchedule):
        return YearlyScheduleSchema(month=s.month, day=s.day)
    raise ValueError(f"Unknown schedule type: {type(s).__name__}")


def layout_to_schema(layout: Layout | None) -> LayoutSchema | None:
    if layout is None:
        return None
    bgs: list[BackgroundSchema] = []
    for bg in layout.backgrounds:
        if isinstance(bg, SolidBackground):
            bgs.append(SolidBackgroundSchema(color=bg.color.to_hex()))
        elif isinstance(bg, GradientTopRightBackground):
            bgs.append(GradientTRBackgroundSchema(color=bg.color.to_hex()))
        elif isinstance(bg, GradientBottomLeftBackground):
            bgs.append(GradientBLBackgroundSchema(color=bg.color.to_hex()))
    return LayoutSchema(
        id=layout.id,
        backgrounds=bgs,
        border=BorderStyleSchema(
            type=layout.border.type,
            width=layout.border.width,
            color=layout.border.color.to_hex(),
        )
        if layout.border
        else None,
        icon=IconStyleSchema(type=layout.icon.type, value=layout.icon.value)
        if layout.icon
        else None,
        shape=ShapeStyleSchema(type=layout.shape.type, radius=layout.shape.radius)
        if layout.shape
        else None,
        pin=PinStyleSchema(color=layout.pin.color.to_hex(), icon=layout.pin.icon)
        if layout.pin
        else None,
    )


# ---------------------------------------------------------------------------
# Schema → Python converters (write path)
# ---------------------------------------------------------------------------


def schema_to_schedule(s: ScheduleSchema) -> Schedule:  # type: ignore[return]
    if isinstance(s, SingleDayScheduleSchema):
        return SingleDaySchedule(
            day=s.day,
            start_time=s.start_time,
            duration=Duration.from_string(s.duration) if s.duration else None,
        )
    if isinstance(s, MultiDayScheduleSchema):
        return MultiDaySchedule(start_day=s.start_day, end_day=s.end_day)
    if isinstance(s, WeeklyScheduleSchema):
        appointments = [
            WeeklyAppointment(
                week_day=Weekday.from_string(a.week_day),
                start_time=a.start_time,
                end_time=a.end_time,
                duration=Duration.from_string(a.duration) if a.duration else None,
            )
            for a in s.appointments
        ]
        return WeeklySchedule(
            appointments=appointments,
            start_date=s.start_date,
            end_date=s.end_date,
        )
    if isinstance(s, MonthlyScheduleSchema):
        return MonthlySchedule(
            day_of_month=s.day_of_month,
            start_time=s.start_time,
            duration=Duration.from_string(s.duration),
            start_date=s.start_date,
            end_date=s.end_date,
        )
    if isinstance(s, YearlyScheduleSchema):
        return YearlySchedule(month=s.month, day=s.day)
    raise ValueError(f"Unknown schedule schema: {type(s).__name__}")


def schema_to_layout(s: LayoutSchema | str | None) -> Layout | str | None:
    if s is None:
        return None
    if isinstance(s, str):
        return s
    bgs = []
    for bg in s.backgrounds:
        if isinstance(bg, SolidBackgroundSchema):
            bgs.append(SolidBackground(color=Color.from_hex(bg.color)))
        elif isinstance(bg, GradientTRBackgroundSchema):
            bgs.append(GradientTopRightBackground(color=Color.from_hex(bg.color)))
        elif isinstance(bg, GradientBLBackgroundSchema):
            bgs.append(GradientBottomLeftBackground(color=Color.from_hex(bg.color)))
    return Layout(
        id=s.id,
        backgrounds=bgs,
        border=BorderStyle(
            type=s.border.type,
            width=s.border.width,
            color=Color.from_hex(s.border.color),
        )
        if s.border
        else None,
        icon=IconStyle(type=s.icon.type, value=s.icon.value) if s.icon else None,
        shape=ShapeStyle(type=s.shape.type, radius=s.shape.radius) if s.shape else None,
        pin=PinStyle(color=Color.from_hex(s.pin.color), icon=s.pin.icon) if s.pin else None,
    )
