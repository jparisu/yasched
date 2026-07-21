"""A named, reusable bundle of attributes and/or layout."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.coring.Layout import Layout


@dataclass(frozen=True)
class Trait:
    """A reusable bundle attached to entities via their ``traits`` list.

    A trait with only a ``layout`` is equivalent to a v2 "named layout".
    """

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    layout: Layout | None = None
