"""Map a resolved :class:`Database` to the JSON shapes the frontend consumes.

Pure functions (no FastAPI import) so the view logic is unit-testable on its
own. Everything the frontend needs is a resolved element plus its generated
(virtual) occurrences within a date window.
"""

from __future__ import annotations

import datetime
from dataclasses import replace
from typing import Any

from yasched.backending.Database import Database
from yasched.backending.generating.Generator import Generator
from yasched.backending.resolving.Resolver import ResolvedElement, Resolver
from yasched.coring.AttributeDefinition import AttributeDefinition
from yasched.coring.ElementType import ElementType
from yasched.utilizing.timing.Duration import Duration


def _combined_database(db: Database, virtuals: list[Any]) -> Database:
    """A shallow database whose element pool also contains the virtual elements."""
    pool = dict(db.elements)
    for virtual in virtuals:
        pool[virtual.id] = virtual
    return replace(db, elements=pool)


def _incoming_map(db: Database) -> dict[str, list[dict[str, str]]]:
    """Reverse connection index: target id -> [{from, relation}]."""
    incoming: dict[str, list[dict[str, str]]] = {}
    for element in db.elements.values():
        for connection in element.connections():
            incoming.setdefault(connection.to, []).append(
                {"from": element.id, "relation": connection.relation}
            )
    return incoming


def element_dto(
    resolved: ResolvedElement, incoming: dict[str, list[dict[str, str]]]
) -> dict[str, Any]:
    return {
        "id": resolved.id,
        "type": resolved.type.value,
        "virtual": resolved.virtual,
        "attributes": {k: v for k, v in resolved.attributes.items() if k != "connections"},
        "layout": resolved.layout.to_dict(),
        "parents": resolved.parents,
        "mainParent": resolved.main_parent,
        "topic": resolved.topic,
        "connections": [c.to_dict() for c in resolved.connections()],
        "incoming": incoming.get(resolved.id, []),
    }


def definition_dto(definition: AttributeDefinition) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": definition.name,
        "valueType": definition.value_type.value,
        "appliesTo": [t.value for t in definition.applies_to],
        "builtin": definition.builtin,
        "inherits": definition.inherits,
    }
    if definition.enum_values:
        out["enumValues"] = list(definition.enum_values)
    if definition.minimum is not None:
        out["min"] = definition.minimum
    if definition.maximum is not None:
        out["max"] = definition.maximum
    if definition.layout is not None and not definition.layout.is_empty():
        out["layout"] = definition.layout.to_dict()
    return out


def build_payload(
    db: Database,
    start: datetime.date | None = None,
    end: datetime.date | None = None,
) -> dict[str, Any]:
    """Resolved real + virtual elements within ``[start, end]``, plus definitions."""
    today = datetime.date.today()
    start = start or (today - datetime.timedelta(days=31))
    end = end or (today + datetime.timedelta(days=365))

    virtuals = Generator(db, Resolver(db)).generate(start, end)
    pool = _combined_database(db, virtuals)
    resolver = Resolver(pool)
    incoming = _incoming_map(pool)

    elements = [element_dto(resolver.resolve(e), incoming) for e in pool.elements.values()]
    return {
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "definitions": [definition_dto(d) for d in db.attribute_defs.values()],
        "elements": elements,
    }


# ---------------------------------------------------------------------------
# Effort — time used per topic, over a chosen period
# ---------------------------------------------------------------------------


def _to_date(value: Any) -> datetime.date | None:
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(str(value).split("T")[0])
    except ValueError:
        return None


def _duration_minutes(value: Any) -> int:
    if not value:
        return 0
    try:
        return Duration.from_string(str(value)).to_minutes()
    except ValueError:
        return 0


def _element_date(resolved: ResolvedElement) -> datetime.date | None:
    """The date that places an element in a period: event ``start``, task ``deadline``."""
    if resolved.type is ElementType.EVENT:
        return _to_date(resolved.attributes.get("start"))
    if resolved.type is ElementType.TASK:
        return _to_date(resolved.attributes.get("deadline"))
    return None


def _element_minutes(resolved: ResolvedElement) -> int:
    """Time used on an element: ``timeSpent`` (events fall back to ``duration``)."""
    if resolved.type is ElementType.EVENT:
        return _duration_minutes(
            resolved.attributes.get("timeSpent") or resolved.attributes.get("duration")
        )
    if resolved.type is ElementType.TASK:
        return _duration_minutes(resolved.attributes.get("timeSpent"))
    return 0


def _min_data_date(db: Database) -> datetime.date | None:
    """Earliest anchor date across the real elements (the natural 'beginning')."""
    dates = [
        d
        for element in db.elements.values()
        for key in ("start", "deadline", "startDate")
        if (d := _to_date(element.attributes.get(key))) is not None
    ]
    return min(dates) if dates else None


def build_effort(
    db: Database,
    start: datetime.date | None = None,
    end: datetime.date | None = None,
) -> dict[str, Any]:
    """Per-topic time used within ``[start, end]`` (own + rolled up the topic tree).

    An element counts when its anchor date (event ``start`` / task ``deadline``)
    falls in the period. ``start`` defaults to the earliest data date ('the
    beginning'); ``end`` defaults to today.
    """
    end = end or datetime.date.today()
    start = start if start is not None else (_min_data_date(db) or end)
    if start > end:
        start = end

    virtuals = Generator(db, Resolver(db)).generate(start, end)
    pool = _combined_database(db, virtuals)
    resolver = Resolver(pool)

    topic_ids = [t.id for t in pool.by_type(ElementType.TOPIC)]
    own = {tid: [0, 0] for tid in topic_ids}  # [event_minutes, task_minutes]
    for element in pool.elements.values():
        if element.type not in (ElementType.EVENT, ElementType.TASK):
            continue
        resolved = resolver.resolve(element)
        if resolved.attributes.get("cancelled"):
            continue
        day = _element_date(resolved)
        if day is None or not (start <= day <= end):
            continue
        topic = resolved.topic
        if topic not in own:
            continue
        minutes = _element_minutes(resolved)
        if minutes <= 0:
            continue
        own[topic][0 if element.type is ElementType.EVENT else 1] += minutes

    children: dict[str | None, list[str]] = {}
    for tid in topic_ids:
        children.setdefault(resolver.main_parent(tid), []).append(tid)

    memo: dict[str, tuple[int, int]] = {}

    def rolled(tid: str, seen: frozenset[str]) -> tuple[int, int]:
        if tid in memo:
            return memo[tid]
        events, tasks = own.get(tid, [0, 0])
        for child in children.get(tid, []):
            if child in seen:
                continue
            cev, ctk = rolled(child, seen | {tid})
            events += cev
            tasks += ctk
        memo[tid] = (events, tasks)
        return memo[tid]

    topics_out: dict[str, dict[str, int]] = {}
    for tid in topic_ids:
        rolled_events, rolled_tasks = rolled(tid, frozenset())
        topics_out[tid] = {
            "ownEvents": own[tid][0],
            "ownTasks": own[tid][1],
            "rolledEvents": rolled_events,
            "rolledTasks": rolled_tasks,
        }

    return {"window": {"start": start.isoformat(), "end": end.isoformat()}, "topics": topics_out}
