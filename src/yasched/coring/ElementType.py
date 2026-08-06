"""The four element types of the unified v4 model."""

from __future__ import annotations

from enum import StrEnum


class ElementType(StrEnum):
    """Discriminates behavior and which attributes are valid for an element."""

    TOPIC = "topic"
    EVENT = "event"
    TASK = "task"
    SCHEDULE = "schedule"

    @staticmethod
    def from_string(value: str) -> ElementType:
        s = str(value).strip().lower()
        for member in ElementType:
            if member.value == s:
                return member
        raise ValueError(f"Unknown element type: {value!r}")

    def __str__(self) -> str:
        return self.value
