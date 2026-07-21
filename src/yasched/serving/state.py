"""Holds the loaded agenda, reloads it, and applies CRUD mutations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from yasched.backending.Database import Database
from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.loading.DatabaseSerializer import DatabaseSerializer
from yasched.coring.Event import Event
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic

_KINDS = ("topics", "events", "tasks")


class ReadOnlyError(RuntimeError):
    """Raised when a write is attempted on a read-only (multi-file) agenda."""


class UnknownEntityError(KeyError):
    """Raised when an entity id is not found for update/delete."""


class AppState:
    """Loads and caches the :class:`Database` for one agenda file, and writes it back.

    Writes are refused when the agenda uses xyml includes (``__file__`` / ``__ext__``),
    because serializing back would flatten the multi-file structure. Such agendas
    (e.g. the bundled example) are therefore browse-only.
    """

    def __init__(self, agenda_path: Path) -> None:
        self.agenda_path = agenda_path
        self._db: Database | None = None
        self._read_only = False

    @property
    def db(self) -> Database:
        if self._db is None:
            self.reload()
        assert self._db is not None
        return self._db

    @property
    def read_only(self) -> bool:
        # Touch the db so the flag is computed from the on-disk file first.
        _ = self.db
        return self._read_only

    def reload(self) -> Database:
        if not self.agenda_path.exists():
            self._db = Database()
            self._read_only = False
        else:
            text = self.agenda_path.read_text(encoding="utf-8")
            self._read_only = "__file__" in text or "__ext__" in text
            self._db = DatabaseLoader.load(self.agenda_path)
        return self._db

    # -- mutations -----------------------------------------------------

    def _collection(self, kind: str) -> dict[str, Topic | Event | Task]:
        if kind not in _KINDS:
            raise UnknownEntityError(f"Unknown kind: {kind!r}")
        return getattr(self.db, kind)  # type: ignore[no-any-return]

    def upsert(self, kind: str, spec: dict[str, Any]) -> Topic | Event | Task:
        """Create or replace an entity from a raw spec dict; persist to disk."""
        self._guard_writable()
        entity = DatabaseLoader.parse_entity(kind, spec)
        self._collection(kind)[entity.id] = entity
        self.save()
        return entity

    def delete(self, kind: str, entity_id: str) -> None:
        self._guard_writable()
        collection = self._collection(kind)
        if entity_id not in collection:
            raise UnknownEntityError(f"No {kind[:-1]} with id {entity_id!r}")
        del collection[entity_id]
        self.save()

    def save(self) -> None:
        self.agenda_path.parent.mkdir(parents=True, exist_ok=True)
        self.agenda_path.write_text(DatabaseSerializer.to_yaml(self.db), encoding="utf-8")

    def _guard_writable(self) -> None:
        if self.read_only:
            raise ReadOnlyError(
                "This agenda uses file includes and is read-only in the app. "
                "Edit it as YAML, or point yasched at a single-file agenda."
            )
