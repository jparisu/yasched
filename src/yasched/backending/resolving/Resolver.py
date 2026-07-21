"""Resolve inheritance, traits, and merges into effective values.

Precedence, lowest → highest (topics ancestors-first in listed order; traits in
listed order)::

    default  <  topic(s)  <  traits  <  parent  <  own

Merge rules per namespace:

* ``attributes`` — replace by key (higher layer wins per key)
* ``tags``       — union (accumulate, order-preserving, de-duplicated)
* ``layout``     — backgrounds compose by concrete ``type``; other fields higher-wins

Cycles (topic DAG or task/event parent) are guarded by a visited set and skipped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.backending.Database import Database
from yasched.coring.Event import Event
from yasched.coring.Layout import Layout
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic

# A raw layer contributed by a single node: (attributes, tags, layout).
_Layer = tuple[dict[str, Any], list[str], Layout | None]


@dataclass
class Resolved:
    """An entity with its effective (post-inheritance) values."""

    source: Topic | Event | Task
    attributes: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    layout: Layout = field(default_factory=Layout)
    # Effective topics: a subtask/sub-event with no topics of its own inherits
    # them from its parent chain (empty for topics themselves).
    topic_ids: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.source.id

    @property
    def name(self) -> str:
        return self.source.name

    @property
    def description(self) -> str | None:
        return self.source.description


def _union_tags(layers: list[_Layer]) -> list[str]:
    seen: dict[str, None] = {}
    for _attrs, tags, _layout in layers:
        for tag in tags:
            seen.setdefault(tag, None)
    return list(seen)


def _merge_attributes(layers: list[_Layer]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for attrs, _tags, _layout in layers:
        merged.update(attrs)
    return merged


def _merge_layouts(layers: list[_Layer]) -> Layout:
    bg_by_type: dict[str, Any] = {}
    border = icon = pin = shape = None
    for _attrs, _tags, layout in layers:
        if layout is None:
            continue
        for bg in layout.backgrounds:
            bg_by_type[bg.type] = bg  # same type replaces; new type appends (order kept)
        if layout.border is not None:
            border = layout.border
        if layout.icon is not None:
            icon = layout.icon
        if layout.pin is not None:
            pin = layout.pin
        if layout.shape is not None:
            shape = layout.shape
    return Layout(
        backgrounds=list(bg_by_type.values()), border=border, icon=icon, pin=pin, shape=shape
    )


class Resolver:
    """Computes effective values for every entity in a :class:`Database`."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._topic_cache: dict[str, Resolved] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve_topic(self, topic_id: str) -> Resolved | None:
        topic = self._db.topics.get(topic_id)
        if topic is None:
            return None
        return self._fold(topic, self._topic_layers(topic_id, frozenset()))

    def resolve_event(self, event_id: str) -> Resolved | None:
        event = self._db.events.get(event_id)
        if event is None:
            return None
        resolved = self._fold(event, self._event_layers(event, frozenset()))
        resolved.topic_ids = self._effective_event_topics(event, frozenset())
        return resolved

    def resolve_task(self, task_id: str) -> Resolved | None:
        task = self._db.tasks.get(task_id)
        if task is None:
            return None
        resolved = self._fold(task, self._task_layers(task, frozenset()))
        resolved.topic_ids = self._effective_task_topics(task, frozenset())
        return resolved

    def _effective_task_topics(self, task: Task, visited: frozenset[str]) -> list[str]:
        if task.topic_ids:
            return list(task.topic_ids)
        parent_id = task.parent_id
        if parent_id and parent_id in self._db.tasks and parent_id not in visited:
            return self._effective_task_topics(self._db.tasks[parent_id], visited | {task.id})
        return []

    def _effective_event_topics(self, event: Event, visited: frozenset[str]) -> list[str]:
        if event.topic_ids:
            return list(event.topic_ids)
        parent_id = event.parent_id
        if parent_id and parent_id in self._db.events and parent_id not in visited:
            return self._effective_event_topics(self._db.events[parent_id], visited | {event.id})
        return []

    def resolve_all_topics(self) -> dict[str, Resolved]:
        return {tid: r for tid in self._db.topics if (r := self.resolve_topic(tid)) is not None}

    def resolve_all_events(self) -> dict[str, Resolved]:
        return {eid: r for eid in self._db.events if (r := self.resolve_event(eid)) is not None}

    def resolve_all_tasks(self) -> dict[str, Resolved]:
        return {tid: r for tid in self._db.tasks if (r := self.resolve_task(tid)) is not None}

    # ------------------------------------------------------------------
    # Layer builders (all EXCLUDE the default layer; it is added once by _fold)
    # ------------------------------------------------------------------

    def _trait_layers(self, names: list[str]) -> list[_Layer]:
        layers: list[_Layer] = []
        for name in names:
            trait = self._db.traits.get(name)
            if trait is not None:
                layers.append((trait.attributes, [], trait.layout))
        return layers

    def _topic_layers(self, topic_id: str, visited: frozenset[str]) -> list[_Layer]:
        if topic_id in visited:
            return []
        topic = self._db.topics.get(topic_id)
        if topic is None:
            return []
        visited = visited | {topic_id}
        layers: list[_Layer] = []
        for parent_id in topic.parent_ids:  # ancestors first, in listed order
            layers.extend(self._topic_layers(parent_id, visited))
        layers.extend(self._trait_layers(topic.traits))
        layers.append((topic.attributes, topic.tags, topic.layout))
        return layers

    def _topics_layers(self, topic_ids: list[str]) -> list[_Layer]:
        layers: list[_Layer] = []
        for topic_id in topic_ids:  # listed order; later topics win
            layers.extend(self._topic_layers(topic_id, frozenset()))
        return layers

    def _event_layers(self, event: Event, visited: frozenset[str]) -> list[_Layer]:
        if event.id in visited:
            return []
        visited = visited | {event.id}
        layers = self._topics_layers(event.topic_ids)
        layers.extend(self._trait_layers(event.traits))
        if event.parent_id and event.parent_id in self._db.events:
            layers.extend(self._event_layers(self._db.events[event.parent_id], visited))
        layers.append((event.attributes, event.tags, event.layout))
        return layers

    def _task_layers(self, task: Task, visited: frozenset[str]) -> list[_Layer]:
        if task.id in visited:
            return []
        visited = visited | {task.id}
        layers = self._topics_layers(task.topic_ids)
        layers.extend(self._trait_layers(task.traits))
        if task.parent_id and task.parent_id in self._db.tasks:
            parent = self._db.tasks[task.parent_id]
            # A subtask with no topics of its own inherits the parent's topics.
            layers.extend(self._task_layers(parent, visited))
        layers.append((task.attributes, task.tags, task.layout))
        return layers

    # ------------------------------------------------------------------
    # Fold
    # ------------------------------------------------------------------

    def _fold(self, source: Topic | Event | Task, layers: list[_Layer]) -> Resolved:
        default_layer: _Layer = (self._db.default_attributes, [], self._db.default_layout)
        all_layers = [default_layer, *layers]
        return Resolved(
            source=source,
            attributes=_merge_attributes(all_layers),
            tags=_union_tags(all_layers),
            layout=_merge_layouts(all_layers),
        )
