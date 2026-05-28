"""Error hierarchy for database consistency and integrity violations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConsistencyError(ValueError):
    """Base class for all consistency and integrity errors."""

    entity: str
    entity_id: str
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.entity}:{self.entity_id}] {self.field}: {self.message}"


@dataclass
class DuplicateIdError(ConsistencyError):
    """The same id appears more than once in a collection."""


@dataclass
class UnknownReferenceError(ConsistencyError):
    """A string reference points to a non-existent id."""


@dataclass
class CycleError(ConsistencyError):
    """A graph contains a directed cycle (topics DAG, task parent chain)."""


@dataclass
class TimeConstraintError(ConsistencyError):
    """A temporal invariant is violated (e.g. start_day > end_day)."""


@dataclass
class LogicError(ConsistencyError):
    """A structural invariant is violated (e.g. schedule + deadline on same task)."""
