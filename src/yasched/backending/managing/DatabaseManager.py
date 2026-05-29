"""Validates a Database and resolves cross-entity references."""

from __future__ import annotations

import datetime
from collections import deque

from yasched.backending.Database import (
    Database,
    ResolvedDatabase,
    ResolvedEvent,
    ResolvedTask,
    ResolvedTaskRelation,
    ResolvedTopic,
)
from yasched.backending.managing.ConsistencyError import (
    ConsistencyError,
    CycleError,
    DuplicateIdError,
    LogicError,
    TimeConstraintError,
    UnknownReferenceError,
)
from yasched.coring._shared import EventLink
from yasched.coring.Event import Event
from yasched.coring.Layout import BackgroundStyle, Layout
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.MultiDaySchedule import MultiDaySchedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.WeeklySchedule import WeeklySchedule

_DEFAULT_TOPIC_ID = "__default__"

_EMPTY_LAYOUT = Layout()


def _merge_layouts(low: Layout, high: Layout) -> Layout:
    """Return a new Layout where high-priority fields override low-priority ones.

    For backgrounds, layers are grouped by concrete type: high replaces same type,
    different types coexist so they can be composed visually (e.g. gradient_tr from
    one source alongside gradient_bl from another).
    """
    merged_bgs: dict[type[BackgroundStyle], BackgroundStyle] = {
        type(bg): bg for bg in low.backgrounds
    }
    for bg in high.backgrounds:
        merged_bgs[type(bg)] = bg
    return Layout(
        backgrounds=list(merged_bgs.values()),
        border=high.border if high.border is not None else low.border,
        icon=high.icon if high.icon is not None else low.icon,
        shape=high.shape if high.shape is not None else low.shape,
        pin=high.pin if high.pin is not None else low.pin,
    )


def _is_empty_layout(layout: Layout) -> bool:
    return (
        not layout.backgrounds
        and layout.border is None
        and layout.icon is None
        and layout.shape is None
        and layout.pin is None
    )


def _resolve_own_layout(
    own: Layout | str | None,
    named: dict[str, Layout],
) -> Layout | None:
    if isinstance(own, Layout):
        return own
    if isinstance(own, str):
        return named.get(own)
    return None


def _compute_effective_layout(
    own: Layout | str | None,
    parent_layout: Layout | None,
    topic_layouts: list[Layout | None],
    default_layout: Layout | None,
    named: dict[str, Layout],
) -> Layout | None:
    """Merge layout layers from lowest to highest priority:
    default → topics (in order) → parent → own entity.
    """
    result = _EMPTY_LAYOUT
    if default_layout is not None:
        result = _merge_layouts(result, default_layout)
    for tl in topic_layouts:
        if tl is not None:
            result = _merge_layouts(result, tl)
    if parent_layout is not None:
        result = _merge_layouts(result, parent_layout)
    own_resolved = _resolve_own_layout(own, named)
    if own_resolved is not None:
        result = _merge_layouts(result, own_resolved)
    return None if _is_empty_layout(result) else result


class DatabaseManager:
    """Validates consistency and resolves cross-entity references."""

    @staticmethod
    def validate(database: Database) -> list[ConsistencyError]:
        errors: list[ConsistencyError] = []
        errors.extend(DatabaseManager._check_unique_ids(database))
        errors.extend(DatabaseManager._check_references(database))
        errors.extend(DatabaseManager._check_time_constraints(database))
        errors.extend(DatabaseManager._check_logic_constraints(database))
        errors.extend(DatabaseManager._check_topic_dag(database))
        errors.extend(DatabaseManager._check_task_tree(database))
        return errors

    @staticmethod
    def resolve(database: Database) -> ResolvedDatabase:
        errors = DatabaseManager.validate(database)
        if errors:
            raise errors[0]
        database = DatabaseManager._inject_default_topic(database)
        layouts = DatabaseManager._resolve_layouts(database)
        topics = DatabaseManager._resolve_topics(database, layouts)
        events = DatabaseManager._resolve_events(database, topics, layouts)
        tasks = DatabaseManager._resolve_tasks(database, topics, events, layouts)
        root_topics = [t for t in topics.values() if not t.parents]
        root_tasks = [t for t in tasks.values() if t.parent is None]
        return ResolvedDatabase(
            layouts=layouts,
            topics=topics,
            events=events,
            tasks=tasks,
            root_topics=root_topics,
            root_tasks=root_tasks,
        )

    # ------------------------------------------------------------------
    # Validation checks
    # ------------------------------------------------------------------

    @staticmethod
    def _check_unique_ids(database: Database) -> list[ConsistencyError]:
        errors: list[ConsistencyError] = []
        for entity_type, entities in (
            ("layout", database.layouts),
            ("topic", database.topics),
            ("event", database.events),
            ("task", database.tasks),
        ):
            seen: set[str] = set()
            for entity in entities:
                eid = entity.id
                if eid is None:
                    continue
                if eid in seen:
                    errors.append(
                        DuplicateIdError(
                            entity=entity_type,
                            entity_id=eid,
                            field="id",
                            message=f"Duplicate {entity_type} id {eid!r}",
                        )
                    )
                else:
                    seen.add(eid)
        return errors

    @staticmethod
    def _check_references(database: Database) -> list[ConsistencyError]:
        errors: list[ConsistencyError] = []
        layout_ids = {lay.id for lay in database.layouts if lay.id is not None}
        topic_ids = {t.id for t in database.topics}
        event_ids = {e.id for e in database.events}
        task_ids = {t.id for t in database.tasks}

        def _check_layout_ref(entity_type: str, entity_id: str, layout: object) -> None:
            if isinstance(layout, str) and layout not in layout_ids:
                errors.append(
                    UnknownReferenceError(
                        entity=entity_type,
                        entity_id=entity_id,
                        field="layout",
                        message=f"Layout {layout!r} not found",
                    )
                )

        for topic in database.topics:
            _check_layout_ref("topic", topic.id, topic.layout)
            for pid in topic.parent_ids:
                if pid not in topic_ids:
                    errors.append(
                        UnknownReferenceError(
                            entity="topic",
                            entity_id=topic.id,
                            field="parent_ids",
                            message=f"Parent topic {pid!r} not found",
                        )
                    )

        for event in database.events:
            _check_layout_ref("event", event.id, event.layout)
            if event.topic_id not in topic_ids:
                errors.append(
                    UnknownReferenceError(
                        entity="event",
                        entity_id=event.id,
                        field="topic_id",
                        message=f"Topic {event.topic_id!r} not found",
                    )
                )

        for task in database.tasks:
            _check_layout_ref("task", task.id, task.layout)
            for tid in task.topic_ids:
                if tid not in topic_ids:
                    errors.append(
                        UnknownReferenceError(
                            entity="task",
                            entity_id=task.id,
                            field="topic_ids",
                            message=f"Topic {tid!r} not found",
                        )
                    )
            if task.parent_id is not None and task.parent_id not in task_ids:
                errors.append(
                    UnknownReferenceError(
                        entity="task",
                        entity_id=task.id,
                        field="parent_id",
                        message=f"Parent task {task.parent_id!r} not found",
                    )
                )
            for link in task.event_links:
                if link.event_id not in event_ids:
                    errors.append(
                        UnknownReferenceError(
                            entity="task",
                            entity_id=task.id,
                            field="event_links",
                            message=f"Event {link.event_id!r} not found",
                        )
                    )
            for rel in task.relations:
                if rel.task_id not in task_ids:
                    errors.append(
                        UnknownReferenceError(
                            entity="task",
                            entity_id=task.id,
                            field="relations",
                            message=f"Related task {rel.task_id!r} not found",
                        )
                    )
        return errors

    @staticmethod
    def _check_time_constraints(database: Database) -> list[ConsistencyError]:
        errors: list[ConsistencyError] = []
        all_entities: list[Event | Task] = [*database.events, *database.tasks]
        for entity in all_entities:
            for sched in entity.schedules:
                if isinstance(sched, WeeklySchedule):
                    if sched.start_date and sched.end_date and sched.start_date > sched.end_date:
                        errors.append(
                            TimeConstraintError(
                                entity=type(entity).__name__.lower(),
                                entity_id=entity.id,
                                field="schedules",
                                message=f"WeeklySchedule start_date {sched.start_date}"
                                f" > end_date {sched.end_date}",
                            )
                        )
                elif isinstance(sched, MonthlySchedule):
                    if sched.start_date and sched.end_date and sched.start_date > sched.end_date:
                        errors.append(
                            TimeConstraintError(
                                entity=type(entity).__name__.lower(),
                                entity_id=entity.id,
                                field="schedules",
                                message=f"MonthlySchedule start_date {sched.start_date}"
                                f" > end_date {sched.end_date}",
                            )
                        )
        return errors

    @staticmethod
    def _check_logic_constraints(database: Database) -> list[ConsistencyError]:
        errors: list[ConsistencyError] = []
        for task in database.tasks:
            if task.priority is not None and task.priority < 1:
                errors.append(
                    LogicError(
                        entity="task",
                        entity_id=task.id,
                        field="priority",
                        message=f"priority must be >= 1, got {task.priority}",
                    )
                )
        return errors

    @staticmethod
    def _check_topic_dag(database: Database) -> list[ConsistencyError]:
        errors: list[ConsistencyError] = []
        topic_ids = {t.id for t in database.topics}
        adj = {t.id: [p for p in t.parent_ids if p in topic_ids] for t in database.topics}
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {t.id: WHITE for t in database.topics}

        def dfs(node: str, path: list[str]) -> None:
            if color[node] == GRAY:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                errors.append(
                    CycleError(
                        entity="topic",
                        entity_id=node,
                        field="parent_ids",
                        message=f"Cycle detected: {' -> '.join(cycle)}",
                    )
                )
                return
            if color[node] == BLACK:
                return
            color[node] = GRAY
            for parent in adj.get(node, []):
                dfs(parent, path + [node])
            color[node] = BLACK

        for t in database.topics:
            if color[t.id] == WHITE:
                dfs(t.id, [])
        return errors

    @staticmethod
    def _check_task_tree(database: Database) -> list[ConsistencyError]:
        errors: list[ConsistencyError] = []
        task_ids = {t.id for t in database.tasks}
        adj = {t.id: t.parent_id for t in database.tasks if t.parent_id in task_ids}
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {t.id: WHITE for t in database.tasks}

        def dfs(node: str, path: list[str]) -> None:
            if color[node] == GRAY:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                errors.append(
                    CycleError(
                        entity="task",
                        entity_id=node,
                        field="parent_id",
                        message=f"Cycle detected: {' -> '.join(cycle)}",
                    )
                )
                return
            if color[node] == BLACK:
                return
            color[node] = GRAY
            parent = adj.get(node)
            if parent:
                dfs(parent, path + [node])
            color[node] = BLACK

        for t in database.tasks:
            if color[t.id] == WHITE:
                dfs(t.id, [])
        return errors

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _inject_default_topic(database: Database) -> Database:
        topic_ids = {t.id for t in database.topics}
        needs_default = any((e.topic_id not in topic_ids) for e in database.events) or any(
            (not t.topic_ids and t.parent_id is None) for t in database.tasks
        )
        if not needs_default:
            return database
        default = Topic(id=_DEFAULT_TOPIC_ID, name="Unassigned")
        return Database(
            layouts=database.layouts,
            topics=[default] + list(database.topics),
            events=database.events,
            tasks=database.tasks,
            default_layout=database.default_layout,
            source_path=database.source_path,
        )

    @staticmethod
    def _resolve_layouts(database: Database) -> dict[str, Layout]:
        return {lay.id: lay for lay in database.layouts if lay.id is not None}

    @staticmethod
    def _resolve_topics(database: Database, layouts: dict[str, Layout]) -> dict[str, ResolvedTopic]:
        topic_map = {t.id: t for t in database.topics}
        resolved: dict[str, ResolvedTopic] = {}
        default_layout = database.default_layout

        # Topological order: parents before children
        parent_to_children: dict[str, list[str]] = {t.id: [] for t in database.topics}
        in_degree: dict[str, int] = {}
        for t in database.topics:
            valid_parents = [p for p in t.parent_ids if p in topic_map]
            in_degree[t.id] = len(valid_parents)
            for pid in valid_parents:
                parent_to_children[pid].append(t.id)

        queue: deque[str] = deque(tid for tid, deg in in_degree.items() if deg == 0)
        while queue:
            tid = queue.popleft()
            raw = topic_map[tid]
            parents = [resolved[pid] for pid in raw.parent_ids if pid in resolved]

            parent_layouts = [p.effective_layout for p in parents]
            effective_layout = _compute_effective_layout(
                own=raw.layout,
                parent_layout=None,
                topic_layouts=parent_layouts,
                default_layout=default_layout,
                named=layouts,
            )

            # effective_tags
            if raw.tags:
                effective_tags = list(raw.tags)
            else:
                seen: set[str] = set()
                effective_tags = []
                for p in parents:
                    for tag in p.effective_tags:
                        if tag not in seen:
                            seen.add(tag)
                            effective_tags.append(tag)

            rt = ResolvedTopic(
                raw=raw,
                parents=parents,
                children=[],
                effective_tags=effective_tags,
                effective_layout=effective_layout,
            )
            resolved[tid] = rt
            for cid in parent_to_children.get(tid, []):
                in_degree[cid] -= 1
                if in_degree[cid] == 0:
                    queue.append(cid)

        # Backlinks: populate children
        for rt in resolved.values():
            for parent in rt.parents:
                if rt not in parent.children:
                    parent.children.append(rt)

        return resolved

    @staticmethod
    def _resolve_events(
        database: Database,
        topics: dict[str, ResolvedTopic],
        layouts: dict[str, Layout],
    ) -> dict[str, ResolvedEvent]:
        resolved: dict[str, ResolvedEvent] = {}
        default_layout = database.default_layout
        for event in database.events:
            topic = topics.get(event.topic_id) or topics[_DEFAULT_TOPIC_ID]
            effective_layout = _compute_effective_layout(
                own=event.layout,
                parent_layout=None,
                topic_layouts=[topic.effective_layout],
                default_layout=default_layout,
                named=layouts,
            )
            resolved[event.id] = ResolvedEvent(
                raw=event, topic=topic, effective_layout=effective_layout
            )
        return resolved

    @staticmethod
    def _resolve_tasks(
        database: Database,
        topics: dict[str, ResolvedTopic],
        events: dict[str, ResolvedEvent],
        layouts: dict[str, Layout],
    ) -> dict[str, ResolvedTask]:
        task_map = {t.id: t for t in database.tasks}
        resolved: dict[str, ResolvedTask] = {}
        default_layout = database.default_layout

        # Topological order: parents before children
        parent_to_children: dict[str, list[str]] = {t.id: [] for t in database.tasks}
        in_degree: dict[str, int] = {}
        for t in database.tasks:
            has_parent = t.parent_id is not None and t.parent_id in task_map
            in_degree[t.id] = 1 if has_parent else 0
            if has_parent:
                parent_to_children[t.parent_id].append(t.id)  # type: ignore[index]

        queue: deque[str] = deque(tid for tid, deg in in_degree.items() if deg == 0)
        while queue:
            tid = queue.popleft()
            raw = task_map[tid]
            parent = resolved.get(raw.parent_id) if raw.parent_id else None

            # topic resolution: own topic_ids, then inherit from parent, then default
            if raw.topic_ids:
                task_topics = [
                    topics.get(tid_) or topics.get(_DEFAULT_TOPIC_ID) or next(iter(topics.values()))
                    for tid_ in raw.topic_ids
                    if tid_ in topics or _DEFAULT_TOPIC_ID in topics
                ]
                # filter out None
                task_topics = [t for t in task_topics if t is not None]
            elif parent is not None:
                task_topics = list(parent.topics)
            else:
                default_topic = topics.get(_DEFAULT_TOPIC_ID) or next(iter(topics.values()))
                task_topics = [default_topic]

            # effective_tags
            if raw.tags:
                effective_tags = list(raw.tags)
            elif parent is not None:
                effective_tags = list(parent.effective_tags)
            else:
                seen_tags: set[str] = set()
                effective_tags = []
                for t in task_topics:
                    for tag in t.effective_tags:
                        if tag not in seen_tags:
                            seen_tags.add(tag)
                            effective_tags.append(tag)

            topic_layouts = [t.effective_layout for t in task_topics]
            effective_layout = _compute_effective_layout(
                own=raw.layout,
                parent_layout=parent.effective_layout if parent is not None else None,
                topic_layouts=topic_layouts,
                default_layout=default_layout,
                named=layouts,
            )

            linked_events = [
                events[lnk.event_id] for lnk in raw.event_links if lnk.event_id in events
            ]
            effective_deadline = DatabaseManager._compute_deadline(
                raw.deadline, raw.event_links, events
            )

            rt = ResolvedTask(
                raw=raw,
                topics=task_topics,
                parent=parent,
                children=[],
                effective_tags=effective_tags,
                effective_layout=effective_layout,
                effective_deadline=effective_deadline,
                linked_events=linked_events,
                related_tasks=[],
            )
            resolved[tid] = rt
            for cid in parent_to_children.get(tid, []):
                in_degree[cid] -= 1
                if in_degree[cid] == 0:
                    queue.append(cid)

        # Second pass: populate children and related_tasks backlinks
        for rt in resolved.values():
            if rt.parent is not None and rt not in rt.parent.children:
                rt.parent.children.append(rt)
            for rel in rt.raw.relations:
                target = resolved.get(rel.task_id)
                if target is not None:
                    rt.related_tasks.append(
                        ResolvedTaskRelation(
                            type=rel.type,
                            task=target,
                            description=rel.description,
                        )
                    )

        return resolved

    @staticmethod
    def _compute_deadline(
        raw_deadline: datetime.date | None,
        event_links: list[EventLink],
        events: dict[str, ResolvedEvent],
    ) -> datetime.date | None:
        if raw_deadline is not None:
            return raw_deadline
        dates: list[datetime.date] = []
        for link in event_links:
            if not link.use_as_deadline:
                continue
            ev = events.get(link.event_id)
            if ev is None:
                continue
            for sched in ev.raw.schedules:
                if isinstance(sched, SingleDaySchedule):
                    dates.append(sched.day)
                elif isinstance(sched, MultiDaySchedule):
                    dates.append(sched.start_day)
        return min(dates) if dates else None
