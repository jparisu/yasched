"""The universal Element — the single data structure for everything.

``type`` discriminates behavior and which attributes are valid. ``id`` is the
only value that is not an attribute (identity must never be inherited or
merged). ``direct_parents`` is the inheritance relation only. ``layout`` and
``attributes`` are the inheritable bags; ``name``/``description``/dates/status/
``connections``/… all live inside ``attributes``.

Elements are mutable: the app edits them and promotes virtual ones. Value
objects they hold (``Layout``, ``Connection``) stay frozen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.coring.Connection import Connection
from yasched.coring.ElementType import ElementType
from yasched.coring.Layout import Layout


@dataclass
class Element:
    """A topic, event, task, or schedule — the raw, unresolved holder."""

    id: str
    type: ElementType
    direct_parents: list[str] = field(default_factory=list)
    layout: Layout | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    #: True for auto-generated elements not persisted to disk (see generating/).
    virtual: bool = False

    # -- convenience accessors over the attribute bag (own values only) ----

    @property
    def name(self) -> Any:
        return self.attributes.get("name")

    @property
    def description(self) -> Any:
        return self.attributes.get("description")

    def connections(self) -> list[Connection]:
        """The element's own connections (never inherited)."""
        raw = self.attributes.get("connections") or []
        return [Connection.from_raw(c) for c in raw]

    def is_topic(self) -> bool:
        return self.type is ElementType.TOPIC
