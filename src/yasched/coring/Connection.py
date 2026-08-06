"""A directed, informational link between two elements.

Connections live inside the built-in ``connections`` attribute (a list of
``Connection``). They are stored once, on the source element, and surfaced on
both endpoints by the UI. They never participate in inheritance and never
change another element's computed state (informational only in v4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Connection:
    """``source --relation--> to``. The relation label is an open string."""

    to: str
    relation: str = "related"

    @staticmethod
    def from_raw(raw: Any) -> Connection:
        """Parse a connection from a mapping or a bare target-id string."""
        if isinstance(raw, str):
            return Connection(to=raw)
        if isinstance(raw, dict):
            return Connection(to=str(raw["to"]), relation=str(raw.get("relation", "related")))
        raise ValueError(f"Cannot parse connection: {raw!r}")

    def to_dict(self) -> dict[str, Any]:
        return {"to": self.to, "relation": self.relation}
