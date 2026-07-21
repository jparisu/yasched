"""Event: a time-bound occurrence, recurring via ``schedules``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.coring.Layout import Layout
from yasched.coring.Schedule import Schedule


@dataclass(frozen=True)
class Event:
    """A time-bound occurrence belonging to one or more topics.

    A sub-event sets ``parent_id`` to a recurring parent event and overrides one
    of its occurrences (typically supplying its own ``single_day`` schedule).
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
