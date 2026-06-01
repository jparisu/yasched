"""Schedule view schemas: DailyView, WeeklyView, EventConflict."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from apps.api.schemas.event import EventSchema
from apps.api.schemas.task import TaskSchema

if TYPE_CHECKING:
    from yasched.backending.interfacing.DatabaseInterface import (
        DailyView,
        EventConflict,
        WeeklyView,
    )


class EventConflictSchema(BaseModel):
    blocker_id: str
    blocked_id: str
    date: datetime.date

    @staticmethod
    def from_conflict(c: EventConflict) -> EventConflictSchema:
        return EventConflictSchema(blocker_id=c.blocker.id, blocked_id=c.blocked.id, date=c.date)


class DailyViewSchema(BaseModel):
    date: datetime.date
    events: list[EventSchema]
    tasks: list[TaskSchema]
    conflicts: list[EventConflictSchema]

    @staticmethod
    def from_view(view: DailyView) -> DailyViewSchema:
        return DailyViewSchema(
            date=view.date,
            events=[EventSchema.from_resolved(e) for e in view.events],
            tasks=[TaskSchema.from_resolved(t) for t in view.tasks],
            conflicts=[EventConflictSchema.from_conflict(c) for c in view.conflicts],
        )


class WeeklyViewSchema(BaseModel):
    week_start: datetime.date
    days: list[DailyViewSchema]

    @staticmethod
    def from_view(view: WeeklyView) -> WeeklyViewSchema:
        return WeeklyViewSchema(
            week_start=view.week_start,
            days=[DailyViewSchema.from_view(d) for d in view.days],
        )
