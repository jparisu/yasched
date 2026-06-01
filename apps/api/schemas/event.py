"""Event read/write schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from apps.api.schemas.common import (
    LayoutSchema,
    ScheduleSchema,
    layout_to_schema,
    schedule_to_schema,
    schema_to_layout,
    schema_to_schedule,
)

if TYPE_CHECKING:
    from yasched.backending.Database import ResolvedEvent


class EventSchema(BaseModel):
    """Read schema built from ResolvedEvent."""

    id: str
    name: str
    description: str | None
    location: str | None
    topic_id: str
    blocking_level: int | None
    schedules: list[ScheduleSchema]
    effective_layout: LayoutSchema | None

    @staticmethod
    def from_resolved(event: ResolvedEvent) -> EventSchema:
        return EventSchema(
            id=event.id,
            name=event.name,
            description=event.description,
            location=event.location,
            topic_id=event.topic.id,
            blocking_level=event.blocking_level,
            schedules=[schedule_to_schema(s) for s in event.schedules],
            effective_layout=layout_to_schema(event.effective_layout),
        )


class EventWriteSchema(BaseModel):
    """Write schema for POST (create) and PATCH (replace) operations."""

    id: str
    name: str
    topic_id: str
    schedules: list[ScheduleSchema]
    description: str | None = None
    location: str | None = None
    blocking_level: int | None = None
    layout: LayoutSchema | str | None = None

    def to_event(self) -> object:
        from yasched.coring.Event import Event

        return Event(
            id=self.id,
            name=self.name,
            topic_id=self.topic_id,
            schedules=[schema_to_schedule(s) for s in self.schedules],
            description=self.description,
            location=self.location,
            blocking_level=self.blocking_level,
            layout=schema_to_layout(self.layout),
        )
