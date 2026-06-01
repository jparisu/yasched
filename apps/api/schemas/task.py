"""Task read/write schemas."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from apps.api.schemas.common import (
    LayoutSchema,
    ScheduleSchema,
    layout_to_schema,
    schedule_to_schema,
    schema_to_layout,
    schema_to_schedule,
)

if TYPE_CHECKING:
    from yasched.backending.Database import ResolvedTask


class EffortSchema(BaseModel):
    min: str
    max: str


class TaskRelationSchema(BaseModel):
    task_id: str
    type: str
    description: str | None = None


class EventLinkSchema(BaseModel):
    event_id: str
    use_as_deadline: bool = True
    as_context: bool = True


class TaskSchema(BaseModel):
    """Read schema built from ResolvedTask."""

    id: str
    name: str
    description: str | None
    status: str
    priority: int | None
    tags: list[str]
    effective_deadline: datetime.date | None
    topic_ids: list[str]
    parent_id: str | None
    children_ids: list[str]
    schedules: list[ScheduleSchema]
    effort: EffortSchema | None
    effective_layout: LayoutSchema | None
    related_tasks: list[TaskRelationSchema]
    event_links: list[EventLinkSchema]

    @staticmethod
    def from_resolved(task: ResolvedTask) -> TaskSchema:
        effort = None
        if task.effort is not None:
            effort = EffortSchema(min=str(task.effort.min), max=str(task.effort.max))
        return TaskSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            status=task.status.value,
            priority=task.priority,
            tags=task.effective_tags,
            effective_deadline=task.effective_deadline,
            topic_ids=[t.id for t in task.topics],
            parent_id=task.parent.id if task.parent else None,
            children_ids=[c.id for c in task.children],
            schedules=[schedule_to_schema(s) for s in task.schedules],
            effort=effort,
            effective_layout=layout_to_schema(task.effective_layout),
            related_tasks=[
                TaskRelationSchema(
                    task_id=r.task.id,
                    type=r.type.value,
                    description=r.description,
                )
                for r in task.related_tasks
            ],
            event_links=[
                EventLinkSchema(
                    event_id=lnk.event_id,
                    use_as_deadline=lnk.use_as_deadline,
                    as_context=lnk.as_context,
                )
                for lnk in task.event_links
            ],
        )


class TaskWriteSchema(BaseModel):
    """Write schema for POST (create) and PATCH (replace) operations."""

    id: str
    name: str
    description: str | None = None
    status: str = "todo"
    priority: int | None = None
    tags: list[str] = Field(default_factory=list)
    deadline: datetime.date | None = None
    topic_ids: list[str] = Field(default_factory=list)
    parent_id: str | None = None
    schedules: list[ScheduleSchema] = Field(default_factory=list)
    effort: EffortSchema | None = None
    relations: list[TaskRelationSchema] = Field(default_factory=list)
    event_links: list[EventLinkSchema] = Field(default_factory=list)
    layout: LayoutSchema | str | None = None

    def to_task(self) -> object:
        from yasched.coring._shared import (
            EffortRange,
            EventLink,
            RelationType,
            TaskRelation,
            TaskStatus,
        )
        from yasched.coring.Task import Task
        from yasched.utilizing.timing.Duration import Duration

        return Task(
            id=self.id,
            name=self.name,
            description=self.description,
            status=TaskStatus(self.status),
            priority=self.priority,
            tags=self.tags,
            deadline=self.deadline,
            topic_ids=self.topic_ids,
            parent_id=self.parent_id,
            schedules=[schema_to_schedule(s) for s in self.schedules],
            effort=EffortRange(
                min=Duration.from_string(self.effort.min),
                max=Duration.from_string(self.effort.max),
            )
            if self.effort
            else None,
            relations=[
                TaskRelation(
                    task_id=r.task_id,
                    type=RelationType(r.type),
                    description=r.description,
                )
                for r in self.relations
            ],
            event_links=[
                EventLink(
                    event_id=lnk.event_id,
                    use_as_deadline=lnk.use_as_deadline,
                    as_context=lnk.as_context,
                )
                for lnk in self.event_links
            ],
            layout=schema_to_layout(self.layout),
        )
