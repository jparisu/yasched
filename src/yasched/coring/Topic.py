"""Organizational category forming a DAG via parent_ids."""

from __future__ import annotations

from dataclasses import dataclass, field

from yasched.coring.Layout import Layout


@dataclass(frozen=True)
class Topic:
    """Plain data holder for a topic parsed from YAML."""

    id: str
    name: str
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    parent_ids: list[str] = field(default_factory=list)
    layout: Layout | str | None = None
