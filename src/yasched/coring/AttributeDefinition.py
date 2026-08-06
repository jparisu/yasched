"""Attribute definitions — the user-extensible schema for element attributes.

An attribute value lives in an element's ``attributes`` bag; an attribute
*definition* declares that value's type, which element types may carry it, its
constraints, whether it inherits, and an optional static layout applied when the
attribute is present (conditional layout logic is deferred).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from yasched.coring.ElementType import ElementType
from yasched.coring.Layout import Layout


class ValueType(StrEnum):
    """The value type an attribute holds."""

    STRING = "string"
    NUMBER = "number"
    INT = "int"
    BOOL = "bool"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    DURATION = "duration"
    ENUM = "enum"
    COLOR = "color"
    ID_REF = "id_ref"
    LIST = "list"

    @staticmethod
    def from_string(value: str) -> ValueType:
        s = str(value).strip().lower()
        for member in ValueType:
            if member.value == s:
                return member
        raise ValueError(f"Unknown value type: {value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AttributeDefinition:
    """Schema for one attribute name.

    ``applies_to`` empty means *all* element types. ``inherits`` False keeps the
    attribute strictly per-element (e.g. ``connections``). ``layout`` is applied
    (unconditionally, this version) whenever the attribute is present.
    """

    name: str
    value_type: ValueType = ValueType.STRING
    applies_to: tuple[ElementType, ...] = ()
    enum_values: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None
    layout: Layout | None = None
    inherits: bool = True
    builtin: bool = False

    def applies_to_type(self, element_type: ElementType) -> bool:
        return not self.applies_to or element_type in self.applies_to


# ---------------------------------------------------------------------------
# Built-in definitions (always present; cannot be deleted by the user)
# ---------------------------------------------------------------------------

_ALL: tuple[ElementType, ...] = ()
_EVENT = (ElementType.EVENT,)
_TASK = (ElementType.TASK,)
_SCHEDULE = (ElementType.SCHEDULE,)


def builtin_definitions() -> dict[str, AttributeDefinition]:
    """The built-in attribute definitions, keyed by name."""
    defs = [
        # Common to every element type.
        AttributeDefinition("name", ValueType.STRING, _ALL, builtin=True),
        AttributeDefinition("description", ValueType.STRING, _ALL, builtin=True),
        # focus is explicit per element — it must NOT inherit down the parent chain.
        AttributeDefinition("focus", ValueType.BOOL, _ALL, inherits=False, builtin=True),
        # semi-focus: on the radar (backlog / future) but not formally focused.
        AttributeDefinition("semiFocus", ValueType.BOOL, _ALL, inherits=False, builtin=True),
        AttributeDefinition("cancelled", ValueType.BOOL, _ALL, builtin=True),
        AttributeDefinition("connections", ValueType.LIST, _ALL, inherits=False, builtin=True),
        # Event.
        AttributeDefinition("start", ValueType.DATETIME, _EVENT, builtin=True),
        AttributeDefinition("end", ValueType.DATETIME, _EVENT, builtin=True),
        AttributeDefinition("duration", ValueType.DURATION, (*_EVENT, *_SCHEDULE), builtin=True),
        AttributeDefinition("location", ValueType.STRING, (*_EVENT, *_TASK), builtin=True),
        AttributeDefinition("reminders", ValueType.LIST, (*_EVENT, *_TASK), builtin=True),
        # Time actually used on this element (for the Effort panels). Per-element,
        # so it must NOT inherit (else childless subtasks would inflate a topic's
        # total). Events fall back to their `duration` when this is unset.
        AttributeDefinition(
            "timeSpent", ValueType.DURATION, (*_EVENT, *_TASK), inherits=False, builtin=True
        ),
        AttributeDefinition(
            "class",
            ValueType.ENUM,
            _EVENT,
            enum_values=("normal", "reminder", "deadline"),
            builtin=True,
        ),
        # Task.
        AttributeDefinition(
            "status",
            ValueType.ENUM,
            _TASK,
            enum_values=("not-started", "in-progress", "completed", "paused"),
            builtin=True,
        ),
        AttributeDefinition("priority", ValueType.INT, _TASK, minimum=0, maximum=10, builtin=True),
        AttributeDefinition(
            "difficulty", ValueType.NUMBER, _TASK, minimum=0, maximum=10, builtin=True
        ),
        AttributeDefinition("deadline", ValueType.DATE, _TASK, builtin=True),
        AttributeDefinition("marked", ValueType.BOOL, _TASK, builtin=True),
        # Schedule.
        AttributeDefinition(
            "generates",
            ValueType.ENUM,
            _SCHEDULE,
            enum_values=("event", "task"),
            builtin=True,
        ),
        AttributeDefinition(
            "kind",
            ValueType.ENUM,
            _SCHEDULE,
            enum_values=("daily", "weekly", "monthly", "yearly"),
            builtin=True,
        ),
        AttributeDefinition("startDate", ValueType.DATE, _SCHEDULE, builtin=True),
        AttributeDefinition("endDate", ValueType.DATE, _SCHEDULE, builtin=True),
        AttributeDefinition("weekDays", ValueType.LIST, _SCHEDULE, builtin=True),
        AttributeDefinition("monthDays", ValueType.LIST, _SCHEDULE, builtin=True),
        AttributeDefinition("yearlyDays", ValueType.LIST, _SCHEDULE, builtin=True),
        AttributeDefinition("time", ValueType.TIME, _SCHEDULE, builtin=True),
    ]
    return {d.name: d for d in defs}


#: Attribute names that never inherit from parents, regardless of definition.
NON_INHERITING = frozenset(name for name, d in builtin_definitions().items() if not d.inherits)
