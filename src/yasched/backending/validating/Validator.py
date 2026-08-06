"""Consistency checks over a parsed :class:`Database`.

Reports structured :class:`Issue`s (errors and warnings) without mutating the
database. Errors indicate broken references; warnings indicate likely mistakes
that still load.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any

from yasched.backending.Database import Database
from yasched.coring.Element import Element


class Severity(enum.Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    """One validation finding."""

    severity: Severity
    code: str
    message: str
    entity_kind: str  # element type, or ""
    entity_id: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "entityKind": self.entity_kind,
            "entityId": self.entity_id,
        }


class Validator:
    """Runs all consistency checks over a database."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._issues: list[Issue] = []

    def validate(self) -> list[Issue]:
        self._issues = []
        self._check_duplicates()
        for element in self._db.elements.values():
            self._check_parents(element)
            self._check_connections(element)
            self._check_attributes(element)
            self._check_orphan(element)
        return list(self._issues)

    # -- helpers -------------------------------------------------------

    def _err(self, code: str, message: str, element: Element) -> None:
        self._issues.append(Issue(Severity.ERROR, code, message, element.type.value, element.id))

    def _warn(self, code: str, message: str, element: Element) -> None:
        self._issues.append(Issue(Severity.WARNING, code, message, element.type.value, element.id))

    # -- checks --------------------------------------------------------

    def _check_duplicates(self) -> None:
        for eid in self._db.duplicate_ids:
            element = self._db.elements.get(eid)
            kind = element.type.value if element else ""
            self._issues.append(
                Issue(
                    Severity.WARNING,
                    "duplicate-id",
                    f"duplicate id '{eid}' — a later definition overrode an earlier one",
                    kind,
                    eid,
                )
            )

    def _check_parents(self, element: Element) -> None:
        for parent_id in element.direct_parents:
            if parent_id == element.id:
                self._err("self-parent", "lists itself as a direct parent", element)
            elif parent_id not in self._db.elements:
                self._err(
                    "unknown-parent",
                    f"references unknown direct parent '{parent_id}'",
                    element,
                )
        if self._has_cycle(element.id):
            self._err("parent-cycle", "is part of a direct-parent cycle", element)

    def _has_cycle(self, element_id: str) -> bool:
        seen: set[str] = set()
        stack = list(self._db.elements[element_id].direct_parents)
        while stack:
            current = stack.pop()
            if current == element_id:
                return True
            if current in seen:
                continue
            seen.add(current)
            node = self._db.elements.get(current)
            if node is not None:
                stack.extend(node.direct_parents)
        return False

    def _check_connections(self, element: Element) -> None:
        for connection in element.connections():
            if connection.to not in self._db.elements:
                self._warn(
                    "unknown-connection",
                    f"connection '{connection.relation}' targets unknown element '{connection.to}'",
                    element,
                )

    def _check_attributes(self, element: Element) -> None:
        # Note: we deliberately do NOT flag "attribute does not apply to this
        # type". Topics and schedules legitimately hold attributes meant for the
        # elements that inherit from them (defaults / generation templates); the
        # type-scoping that stops such values from leaking lives in the resolver.
        for name, value in element.attributes.items():
            definition = self._db.attribute_defs.get(name)
            if definition is None:
                continue
            self._check_range(element, name, value, definition.minimum, definition.maximum)
            if (
                definition.enum_values
                and value is not None
                and str(value) not in definition.enum_values
            ):
                self._warn(
                    "bad-enum",
                    f"attribute '{name}' value {value!r} not in {list(definition.enum_values)}",
                    element,
                )

    def _check_range(
        self, element: Element, name: str, value: Any, minimum: float | None, maximum: float | None
    ) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return
        if minimum is not None and value < minimum:
            self._warn("out-of-range", f"attribute '{name}'={value} below min {minimum}", element)
        if maximum is not None and value > maximum:
            self._warn("out-of-range", f"attribute '{name}'={value} above max {maximum}", element)

    def _check_orphan(self, element: Element) -> None:
        """A promoted occurrence (id ``base#...``) whose generator is gone."""
        if "#" not in element.id:
            return
        base = element.id.split("#", 1)[0]
        if base and base not in self._db.elements:
            self._warn(
                "detached-occurrence",
                f"looks like a promoted occurrence of '{base}', which no longer exists",
                element,
            )


def validate_database(db: Database) -> list[Issue]:
    """Convenience: run all checks and return the issues."""
    return Validator(db).validate()
