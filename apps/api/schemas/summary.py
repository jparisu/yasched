"""Summary and health schemas."""

from __future__ import annotations

from pydantic import BaseModel


class StatusSummarySchema(BaseModel):
    todo: int
    in_progress: int
    done: int
    cancelled: int
    blocked: int


class HealthSchema(BaseModel):
    db_loaded: bool
    task_count: int
    event_count: int
    topic_count: int
    status_summary: StatusSummarySchema
    errors: list[str]
