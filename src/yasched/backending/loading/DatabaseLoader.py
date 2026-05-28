"""Public I/O entry point: load a Database from disk and save it back."""

from __future__ import annotations

from pathlib import Path

from yasched.backending.Database import Database
from yasched.utilizing.xyml.XymlLoader import XymlLoader


class DatabaseParseError(ValueError):
    """Raised when the YAML structure cannot be mapped to coring objects."""


class DatabaseLoader:
    """Stateless utility for Database I/O."""

    @staticmethod
    def load(path: str | Path) -> Database:
        from yasched.backending.loading.DatabaseParser import DatabaseParser

        resolved = Path(path).resolve()
        raw = XymlLoader.load(resolved)
        return DatabaseParser.parse(raw, source_path=resolved)

    @staticmethod
    def save(database: Database, path: str | Path) -> None:
        from yasched.backending.loading.DatabaseSerializer import DatabaseSerializer

        content = DatabaseSerializer.to_yaml(database)
        Path(path).write_text(content, encoding="utf-8")
