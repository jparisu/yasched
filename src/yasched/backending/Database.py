"""In-memory container for a parsed configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.coring.Event import Event
from yasched.coring.Layout import Layout
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.Trait import Trait


@dataclass
class Database:
    """Holds every parsed entity keyed by id, plus the database-level defaults.

    This is the raw, *unresolved* view: references are still strings and no
    inheritance has been applied. Resolution is done by ``resolving.Resolver``.
    """

    default_attributes: dict[str, Any] = field(default_factory=dict)
    default_layout: Layout | None = None
    traits: dict[str, Trait] = field(default_factory=dict)
    topics: dict[str, Topic] = field(default_factory=dict)
    events: dict[str, Event] = field(default_factory=dict)
    tasks: dict[str, Task] = field(default_factory=dict)
    # Duplicate ids seen while parsing (later definitions win): (kind, id).
    duplicate_ids: list[tuple[str, str]] = field(default_factory=list)

    def topic(self, topic_id: str) -> Topic | None:
        return self.topics.get(topic_id)

    def trait(self, name: str) -> Trait | None:
        return self.traits.get(name)
