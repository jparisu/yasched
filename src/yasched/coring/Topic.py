"""Topic: an organizational category forming a DAG via ``parent_ids``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.coring.Layout import Layout


@dataclass(frozen=True)
class Topic:
    """A category grouping events and tasks. Plain data holder.

    ``attributes`` and ``layout`` are the two open bags; ``tags`` is a
    first-class list unioned down the inheritance chain. References
    (``parent_ids``, ``traits``) stay as raw strings; resolution is done by
    ``backending``.
    """

    id: str
    name: str
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    parent_ids: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    layout: Layout | None = None
