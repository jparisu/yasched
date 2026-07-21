"""Map resolved entities + occurrences to the JSON shapes the frontend expects.

The frontend has a fixed, narrow schema (single topic per item, low/medium/high
priority, todo/doing/done status, a small style object). This module is the
single place that translates the open v3 model into that schema.
"""

from __future__ import annotations

import datetime
from typing import Any

from yasched.backending.Database import Database
from yasched.backending.resolving.Resolver import Resolved, Resolver
from yasched.backending.scheduling.Occurrences import _times, build_event_occurrences
from yasched.coring.Layout import Layout
from yasched.coring.Schedule import MonthlySchedule, WeeklySchedule, YearlySchedule
from yasched.utilizing.coloring.Color import Color

_DEFAULT_COLOR = Color.from_hex("#94a3b8")

# our shape vocabulary -> frontend CardShape
_SHAPE_MAP = {
    "rectangle": "rectangle",
    "rounded": "rounded",
    "pill": "curvy",
    "trapezoid": "sticky",
    "sticky": "sticky",
    "curvy": "curvy",
    "cloudy": "cloudy",
}


def _primary_color(layout: Layout) -> Color:
    if layout.backgrounds:
        return layout.backgrounds[-1].color  # most-specific (highest) layer
    if layout.pin is not None:
        return layout.pin.color
    if layout.border is not None:
        return layout.border.color
    return _DEFAULT_COLOR


def _rgba(color: Color, alpha: float) -> str:
    return f"rgba({round(color.r * 255)}, {round(color.g * 255)}, {round(color.b * 255)}, {alpha})"


def _style(layout: Layout) -> dict[str, str]:
    color = _primary_color(layout)
    shape = _SHAPE_MAP.get(layout.shape.type, "rounded") if layout.shape else "rounded"
    return {
        "backgroundColor": _rgba(color, 0.15),
        "leftColor": color.to_hex(),
        "shape": shape,
    }


def _num(value: Any) -> float | int | None:
    """Coerce a numeric attribute to int/float; None when absent/non-numeric.

    Legacy string buckets (low/medium/high) map to representative numbers so old
    agendas still sort/bucket sensibly under the new numeric model.
    """
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    s = str(value).strip().lower()
    legacy = {"low": 2, "medium": 5, "high": 8, "easy": 2, "hard": 8}
    if s in legacy:
        return legacy[s]
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "on", "1", "y")
    return False


def _status(value: Any) -> str:
    v = str(value or "todo").lower().replace("_", "-")
    if v in ("done", "completed", "finished"):
        return "done"
    if v in ("doing", "in-progress", "in-process", "wip", "started"):
        return "doing"
    return "todo"


def _first_topic(resolved: Resolved) -> str:
    ids = resolved.topic_ids or (getattr(resolved.source, "topic_ids", []) or [])
    return ids[0] if ids else ""


def _topic_color_maps(
    resolver: Resolver, db: Database
) -> tuple[dict[str, str], dict[str, str]]:
    """Return (topic_id -> hex color, topic_id -> root-ancestor topic_id)."""
    colors = {
        tid: _primary_color(r.layout).to_hex()
        for tid, r in resolver.resolve_all_topics().items()
    }

    def root_of(tid: str, seen: frozenset[str]) -> str:
        topic = db.topics.get(tid)
        if topic is None or not topic.parent_ids or tid in seen:
            return tid
        parent = topic.parent_ids[0]
        if parent not in db.topics:
            return tid
        return root_of(parent, seen | {tid})

    roots = {tid: root_of(tid, frozenset()) for tid in db.topics}
    return colors, roots


def _element_style(
    layout: Layout,
    topic_ids: list[str],
    colors: dict[str, str],
    roots: dict[str, str],
) -> dict[str, Any]:
    """Style for a task/event: the left line shows the MAIN (root) topic, the
    dot shows the specific sub-topic it belongs to."""
    style = _style(layout)
    if topic_ids:
        sub = topic_ids[0]
        dot = colors.get(sub, style["leftColor"])
        main = colors.get(roots.get(sub, sub), dot)
        style["leftColor"] = main
        style["dotColor"] = dot
    else:
        style["dotColor"] = style["leftColor"]
    return style


def topic_view(resolved: Resolved) -> dict[str, Any]:
    color = _primary_color(resolved.layout)
    return {
        "id": resolved.id,
        "name": resolved.name,
        "color": color.to_hex(),
        "parentIds": list(getattr(resolved.source, "parent_ids", []) or []),
        "style": _style(resolved.layout),
        "tags": resolved.tags,
    }


def task_view(
    resolved: Resolved, colors: dict[str, str], roots: dict[str, str]
) -> dict[str, Any]:
    attrs = resolved.attributes
    deadline = attrs.get("deadline")
    # `on-focus` is read from the task's OWN attributes (not inherited) so a
    # sub-task is only surfaced when explicitly focused, matching the UI toggle.
    own_focus = _truthy(getattr(resolved.source, "attributes", {}).get("on-focus"))
    parent_id = getattr(resolved.source, "parent_id", None)
    return {
        "id": resolved.id,
        "title": resolved.name,
        "description": resolved.description,
        "priority": _num(attrs.get("priority")),
        "status": _status(attrs.get("status")),
        "topicId": _first_topic(resolved),
        "deadline": str(deadline) if deadline is not None else None,
        "parentId": parent_id,
        "onFocus": own_focus,
        "difficulty": _num(attrs.get("difficulty")),
        "style": _element_style(resolved.layout, resolved.topic_ids, colors, roots),
        "tags": resolved.tags,
        "createdAt": datetime.date.today().isoformat(),
    }


def deadline_view(
    resolved: Resolved, colors: dict[str, str], roots: dict[str, str]
) -> dict[str, Any] | None:
    deadline = resolved.attributes.get("deadline")
    if deadline is None:
        return None
    return {
        "id": f"{resolved.id}::deadline",
        "title": resolved.name,
        "date": str(deadline),
        "priority": _num(resolved.attributes.get("priority")),
        "topicId": _first_topic(resolved),
        "style": _element_style(resolved.layout, resolved.topic_ids, colors, roots),
    }


def _is_recurring(resolved: Resolved) -> bool:
    return any(
        isinstance(s, (WeeklySchedule, MonthlySchedule, YearlySchedule))
        for s in resolved.source.schedules  # type: ignore[union-attr]
    )


def build_payload(
    db: Database,
    window_start: datetime.date | None = None,
    window_end: datetime.date | None = None,
) -> dict[str, Any]:
    """Build the full frontend payload (topics, tasks, events, deadlines)."""
    today = datetime.date.today()
    # A wide default window so a full academic year of recurring events is visible
    # across panels (callers can still pass an explicit window).
    start = window_start or (today - datetime.timedelta(days=60))
    end = window_end or (today + datetime.timedelta(days=400))

    resolver = Resolver(db)
    topics = resolver.resolve_all_topics()
    tasks = resolver.resolve_all_tasks()
    events = resolver.resolve_all_events()
    colors, roots = _topic_color_maps(resolver, db)

    occurrences = build_event_occurrences(events, start, end)
    event_items: list[dict[str, Any]] = []
    for occ in occurrences:
        ev = events[occ.event_id]
        own_focus = _truthy(getattr(ev.source, "attributes", {}).get("on-focus"))
        event_items.append(
            {
                "id": f"{occ.event_id}::{occ.date.to_iso()}",
                "title": ev.name,
                "date": occ.date.to_iso(),
                "startTime": occ.start_time.to_hhmm() if occ.start_time else None,
                "endTime": occ.end_time.to_hhmm() if occ.end_time else None,
                "topicId": _first_topic(ev),
                "description": ev.description,
                "recurring": _is_recurring(ev),
                "onFocus": own_focus,
                "style": _element_style(ev.layout, ev.topic_ids, colors, roots),
            }
        )

    deadlines = [d for t in tasks.values() if (d := deadline_view(t, colors, roots)) is not None]

    return {
        "topics": [topic_view(t) for t in topics.values()],
        "tasks": [task_view(t, colors, roots) for t in tasks.values()],
        "events": event_items,
        "deadlines": deadlines,
        "window": {"start": start.isoformat(), "end": end.isoformat()},
    }


def build_timetable(db: Database) -> list[dict[str, Any]]:
    """Weekly timetable entries: one per (recurring weekly event, weekday)."""
    resolver = Resolver(db)
    entries: list[dict[str, Any]] = []
    for resolved in resolver.resolve_all_events().values():
        for sched in resolved.source.schedules:  # type: ignore[union-attr]
            if not isinstance(sched, WeeklySchedule):
                continue
            start_time, end_time = _times(sched)
            for weekday in sched.week_days:
                entries.append(
                    {
                        "id": f"{resolved.id}::{weekday.value}",
                        "eventId": resolved.id,
                        "title": resolved.name,
                        "weekday": weekday.index(),  # 0=Mon .. 6=Sun
                        "startTime": start_time.to_hhmm() if start_time else None,
                        "endTime": end_time.to_hhmm() if end_time else None,
                        "topicId": _first_topic(resolved),
                        "location": resolved.attributes.get("location"),
                        "style": _style(resolved.layout),
                    }
                )
    return entries


def build_graph(db: Database) -> dict[str, Any]:
    """Nodes (tasks/events) grouped by topic + typed edges, for the graph view."""
    resolver = Resolver(db)
    topics = [
        {
            "id": t.id,
            "name": t.name,
            "color": _primary_color(t.layout).to_hex(),
            "parentIds": list(t.source.parent_ids),  # type: ignore[union-attr]
        }
        for t in resolver.resolve_all_topics().values()
    ]

    resolved_tasks = resolver.resolve_all_tasks()
    resolved_events = resolver.resolve_all_events()

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for task in db.tasks.values():
        resolved = resolved_tasks.get(task.id)
        # Effective topics: a sub-task inherits its parent's topic(s).
        eff_topics = resolved.topic_ids if resolved else list(task.topic_ids)
        nodes.append(
            {
                "id": task.id,
                "kind": "task",
                "label": task.name,
                "topicId": eff_topics[0] if eff_topics else None,
                "topicIds": list(eff_topics),
                "tags": resolved.tags if resolved else list(task.tags),
            }
        )
        if task.parent_id:
            edges.append({"source": task.id, "target": task.parent_id, "type": "subtask"})
        for rel in task.relations:
            edges.append({"source": task.id, "target": rel.task_id, "type": rel.type.value})
        for link in task.event_links:
            edges.append({"source": task.id, "target": link.event_id, "type": "event_link"})

    for event in db.events.values():
        resolved = resolved_events.get(event.id)
        eff_topics = resolved.topic_ids if resolved else list(event.topic_ids)
        nodes.append(
            {
                "id": event.id,
                "kind": "event",
                "label": event.name,
                "topicId": eff_topics[0] if eff_topics else None,
                "topicIds": list(eff_topics),
                "tags": resolved.tags if resolved else list(event.tags),
            }
        )
        if event.parent_id:
            edges.append({"source": event.id, "target": event.parent_id, "type": "suboccurrence"})

    topic_edges = [
        {"source": t.id, "target": parent, "type": "topic_parent"}
        for t in db.topics.values()
        for parent in t.parent_ids
    ]

    return {"topics": topics, "nodes": nodes, "edges": edges, "topicEdges": topic_edges}
