"""Task: a unit of work; one-off, recurring, or a subtask."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.coring._shared import EventLink, TaskRelation
from yasched.coring.Layout import Layout
from yasched.coring.Schedule import Schedule


@dataclass(frozen=True)
class Task:
    """A unit of work. Plain data holder.

    - One-off: carry a ``deadline`` attribute.
    - Recurring: carry ``schedules``.
    - Subtask: set ``parent_id`` (decomposition); topic/attributes/layout/tags
      inherit from the parent task during resolution.
    """

    id: str
    name: str
    description: str | None = None
    topic_ids: list[str] = field(default_factory=list)
    parent_id: str | None = None
    tags: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    layout: Layout | None = None
    schedules: list[Schedule] = field(default_factory=list)
    relations: list[TaskRelation] = field(default_factory=list)
    event_links: list[EventLink] = field(default_factory=list)
