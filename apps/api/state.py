"""In-memory server state: raw Database + DatabaseInterface."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from yasched.backending.Database import Database
from yasched.backending.interfacing.DatabaseInterface import DatabaseInterface
from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.managing.DatabaseManager import DatabaseManager


@dataclass
class AppState:
    db_path: Path
    raw_db: Database
    interface: DatabaseInterface

    @staticmethod
    def load(db_path: Path) -> AppState:
        raw_db = DatabaseLoader.load(db_path)
        resolved = DatabaseManager.resolve(raw_db)
        return AppState(db_path=db_path, raw_db=raw_db, interface=DatabaseInterface(resolved))

    def commit(self, new_raw_db: Database) -> None:
        """Validate, save to disk, and refresh in-memory state."""
        resolved = DatabaseManager.resolve(new_raw_db)
        DatabaseLoader.save(new_raw_db, self.db_path)
        self.raw_db = new_raw_db
        self.interface = DatabaseInterface(resolved)

    def replace_task(self, task: object) -> Database:
        from yasched.coring.Task import Task as _Task

        assert isinstance(task, _Task)
        new_tasks = [t if t.id != task.id else task for t in self.raw_db.tasks]
        return replace(self.raw_db, tasks=new_tasks)

    def append_task(self, task: object) -> Database:
        from yasched.coring.Task import Task as _Task

        assert isinstance(task, _Task)
        return replace(self.raw_db, tasks=list(self.raw_db.tasks) + [task])

    def remove_task(self, task_id: str) -> Database:
        return replace(self.raw_db, tasks=[t for t in self.raw_db.tasks if t.id != task_id])

    def replace_event(self, event: object) -> Database:
        from yasched.coring.Event import Event as _Event

        assert isinstance(event, _Event)
        new_events = [e if e.id != event.id else event for e in self.raw_db.events]
        return replace(self.raw_db, events=new_events)

    def append_event(self, event: object) -> Database:
        from yasched.coring.Event import Event as _Event

        assert isinstance(event, _Event)
        return replace(self.raw_db, events=list(self.raw_db.events) + [event])

    def remove_event(self, event_id: str) -> Database:
        return replace(self.raw_db, events=[e for e in self.raw_db.events if e.id != event_id])

    def replace_topic(self, topic: object) -> Database:
        from yasched.coring.Topic import Topic as _Topic

        assert isinstance(topic, _Topic)
        new_topics = [t if t.id != topic.id else topic for t in self.raw_db.topics]
        return replace(self.raw_db, topics=new_topics)

    def append_topic(self, topic: object) -> Database:
        from yasched.coring.Topic import Topic as _Topic

        assert isinstance(topic, _Topic)
        return replace(self.raw_db, topics=list(self.raw_db.topics) + [topic])

    def remove_topic(self, topic_id: str) -> Database:
        return replace(self.raw_db, topics=[t for t in self.raw_db.topics if t.id != topic_id])


_state: AppState | None = None


def init_state(db_path: Path) -> AppState:
    global _state
    _state = AppState.load(db_path)
    return _state


def get_state() -> AppState:
    if _state is None:
        raise RuntimeError("Database not loaded")
    return _state
