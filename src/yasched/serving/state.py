"""Holds the loaded database, reloads it, and applies CRUD mutations.

The agenda is always writable: saving flattens any multi-file xyml source into
the single canonical file at ``agenda_path``.
Promotion of a virtual element is just an upsert with its deterministic id.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from yasched.backending.Database import Database
from yasched.backending.loading.ElementLoader import ElementLoader
from yasched.backending.loading.ElementSerializer import ElementSerializer
from yasched.coring.Element import Element


class UnknownEntityError(KeyError):
    """Raised when an element id is not found for update/delete."""


class AppState:
    """Loads and caches the :class:`Database` for one file, and writes it back."""

    def __init__(self, agenda_path: Path) -> None:
        self.agenda_path = agenda_path
        self._db: Database | None = None

    @property
    def db(self) -> Database:
        if self._db is None:
            self.reload()
        assert self._db is not None
        return self._db

    @property
    def multi_file(self) -> bool:
        """True while the on-disk source still uses xyml includes (pre-flatten)."""
        return self.db.multi_file

    def reload(self) -> Database:
        if not self.agenda_path.exists():
            self._db = Database()
            self._db.all_topic()
        else:
            self._db = ElementLoader.load(self.agenda_path)
        return self._db

    # -- mutations -----------------------------------------------------

    def upsert(self, spec: dict[str, Any]) -> Element:
        """Create or replace an element from a raw spec; persist to disk.

        This is also the promotion path: promoting a virtual element means
        upserting a real element with the same deterministic id.
        """
        element = ElementLoader.parse_element(spec)
        self.db.elements[element.id] = element
        self.save()
        return element

    def delete(self, element_id: str) -> None:
        if element_id not in self.db.elements:
            raise UnknownEntityError(f"No element with id {element_id!r}")
        del self.db.elements[element_id]
        self.save()

    def save(self) -> None:
        # WARNING: this rewrites the file from the model, so YAML comments in the
        # user's agenda do not survive the first save. See the TODO(comments) in
        # ElementSerializer.to_yaml for the options being considered.
        self.agenda_path.parent.mkdir(parents=True, exist_ok=True)
        self.agenda_path.write_text(ElementSerializer.to_yaml(self.db), encoding="utf-8")
        self.db.multi_file = False  # source is now a single flattened file
