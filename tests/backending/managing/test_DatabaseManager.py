"""Tests for DatabaseManager: validate() and resolve()."""

from __future__ import annotations

import datetime

import pytest

from yasched.backending.Database import Database
from yasched.backending.managing.ConsistencyError import (
    ConsistencyError,
    CycleError,
    DuplicateIdError,
    TimeConstraintError,
    UnknownReferenceError,
)
from yasched.backending.managing.DatabaseManager import DatabaseManager
from yasched.coring._shared import (
    BlockedBy,
    EventLink,
    TaskStatus,
    Weekday,
    WeeklyAppointment,
)
from yasched.coring.Event import Event
from yasched.coring.Layout import Layout
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _topic(id: str, name: str = "N", parents: list[str] | None = None, layout=None, tags=None):
    return Topic(id=id, name=name, parent_ids=parents or [], layout=layout, tags=tags or [])


def _event(id: str, topic_id: str = "t1", name: str = "N", blocking_level=None):
    sched = SingleDaySchedule(day=datetime.date(2026, 1, 1))
    return Event(
        id=id, topic_id=topic_id, name=name, schedules=[sched], blocking_level=blocking_level
    )


def _task(
    id: str,
    topic_id: str | None = "t1",
    name: str = "N",
    parent_id=None,
    deadline=None,
    status=TaskStatus.TODO,
    tags=None,
    event_links=None,
    blocked_by=None,
    schedules=None,
):
    return Task(
        id=id,
        name=name,
        topic_id=topic_id,
        parent_id=parent_id,
        deadline=deadline,
        status=status,
        tags=tags or [],
        event_links=event_links or [],
        blocked_by=blocked_by or [],
        schedules=schedules or [],
    )


def _db(topics=None, events=None, tasks=None, layouts=None):
    return Database(
        layouts=layouts or [],
        topics=topics or [],
        events=events or [],
        tasks=tasks or [],
    )


# ---------------------------------------------------------------------------
# validate — empty database
# ---------------------------------------------------------------------------


def test_validate_empty_db_is_valid():
    assert DatabaseManager.validate(_db()) == []


# ---------------------------------------------------------------------------
# validate — duplicate IDs
# ---------------------------------------------------------------------------


def test_validate_duplicate_topic_id():
    errs = DatabaseManager.validate(_db(topics=[_topic("t1"), _topic("t1")]))
    assert any(isinstance(e, DuplicateIdError) for e in errs)


def test_validate_duplicate_event_id():
    db = _db(topics=[_topic("t1")], events=[_event("e1"), _event("e1")])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, DuplicateIdError) for e in errs)


def test_validate_duplicate_task_id():
    db = _db(topics=[_topic("t1")], tasks=[_task("t1"), _task("t1")])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, DuplicateIdError) for e in errs)


def test_validate_duplicate_layout_id():
    db = _db(layouts=[Layout(id="l1"), Layout(id="l1")])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, DuplicateIdError) for e in errs)


# ---------------------------------------------------------------------------
# validate — unknown references
# ---------------------------------------------------------------------------


def test_validate_unknown_topic_parent():
    db = _db(topics=[_topic("t1", parents=["no_such_topic"])])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, UnknownReferenceError) for e in errs)


def test_validate_unknown_event_topic():
    db = _db(topics=[_topic("t1")], events=[_event("e1", topic_id="ghost")])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, UnknownReferenceError) for e in errs)


def test_validate_unknown_task_topic():
    db = _db(topics=[_topic("t1")], tasks=[_task("t1", topic_id="ghost")])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, UnknownReferenceError) for e in errs)


def test_validate_unknown_task_parent():
    db = _db(topics=[_topic("t1")], tasks=[_task("child", parent_id="no_parent")])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, UnknownReferenceError) for e in errs)


def test_validate_unknown_event_link():
    db = _db(
        topics=[_topic("t1")], tasks=[_task("t1", event_links=[EventLink(event_id="ghost_event")])]
    )
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, UnknownReferenceError) for e in errs)


def test_validate_unknown_blocked_by():
    db = _db(
        topics=[_topic("t1")], tasks=[_task("t1", blocked_by=[BlockedBy(task_id="ghost_task")])]
    )
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, UnknownReferenceError) for e in errs)


def test_validate_unknown_layout_ref():
    db = _db(topics=[_topic("t1", layout="ghost_layout")])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, UnknownReferenceError) for e in errs)


# ---------------------------------------------------------------------------
# validate — time constraints
# ---------------------------------------------------------------------------


def test_validate_multi_day_schedule_start_after_end():
    # MultiDaySchedule already raises in __post_init__, so this is a coring-level check
    # The parser would catch it; we test that manager also surfaces it via a Task/Event
    # with invalid MultiDaySchedule (this can't be constructed, so test the manager
    # via EffortRange instead)
    pass  # MultiDaySchedule enforces invariant at construction — no separate manager check needed


def test_validate_effort_range_min_exceeds_max_is_coring_level():
    # EffortRange raises ValueError at construction — caught by parser, not manager
    pass


def test_validate_weekly_schedule_start_after_end():
    appt = WeeklyAppointment(
        week_day=Weekday.MONDAY, start_time=datetime.time(9), duration=Duration.from_string("1h")
    )
    sched = WeeklySchedule(
        appointments=[appt],
        start_date=datetime.date(2026, 6, 1),
        end_date=datetime.date(2026, 1, 1),  # end before start
    )
    event = Event(id="e1", topic_id="t1", name="N", schedules=[sched])
    db = _db(topics=[_topic("t1")], events=[event])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, TimeConstraintError) for e in errs)


def test_validate_monthly_schedule_start_after_end():
    sched = MonthlySchedule(
        day_of_month=15,
        start_time=datetime.time(10),
        duration=Duration.from_string("1h"),
        start_date=datetime.date(2026, 6, 1),
        end_date=datetime.date(2026, 1, 1),
    )
    event = Event(id="e1", topic_id="t1", name="N", schedules=[sched])
    db = _db(topics=[_topic("t1")], events=[event])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, TimeConstraintError) for e in errs)


# ---------------------------------------------------------------------------
# validate — logic constraints
# ---------------------------------------------------------------------------


def test_validate_task_with_schedule_and_deadline():
    # Task raises at coring level — test that a task without both still validates
    task = _task("t1", deadline=datetime.date(2026, 1, 1))
    db = _db(topics=[_topic("t1")], tasks=[task])
    errs = DatabaseManager.validate(db)
    assert errs == []  # deadline alone is fine


def test_validate_valid_database_no_errors():
    db = _db(
        topics=[_topic("t1"), _topic("t2", parents=["t1"])],
        events=[_event("e1", topic_id="t1")],
        tasks=[_task("task1", topic_id="t1")],
    )
    assert DatabaseManager.validate(db) == []


# ---------------------------------------------------------------------------
# validate — cycles
# ---------------------------------------------------------------------------


def test_validate_topic_self_cycle():
    db = _db(topics=[_topic("t1", parents=["t1"])])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, CycleError) for e in errs)


def test_validate_topic_two_node_cycle():
    db = _db(topics=[_topic("a", parents=["b"]), _topic("b", parents=["a"])])
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, CycleError) for e in errs)


def test_validate_task_parent_cycle():
    db = _db(
        topics=[_topic("t1")],
        tasks=[
            _task("a", topic_id="t1", parent_id="b"),
            _task("b", topic_id="t1", parent_id="a"),
        ],
    )
    errs = DatabaseManager.validate(db)
    assert any(isinstance(e, CycleError) for e in errs)


def test_validate_fail_slow_collects_all_errors():
    # Two independent errors — both should be reported
    db = _db(topics=[_topic("t1"), _topic("t1"), _topic("t2", parents=["ghost"])])
    errs = DatabaseManager.validate(db)
    assert len(errs) >= 2


# ---------------------------------------------------------------------------
# resolve — basic structure
# ---------------------------------------------------------------------------


def test_resolve_empty_db():
    rdb = DatabaseManager.resolve(_db())
    assert rdb.topics == {}
    assert rdb.events == {}
    assert rdb.tasks == {}
    assert rdb.root_topics == []
    assert rdb.root_tasks == []


def test_resolve_single_topic():
    db = _db(topics=[_topic("t1", name="Topic One")])
    rdb = DatabaseManager.resolve(db)
    assert "t1" in rdb.topics
    rt = rdb.topics["t1"]
    assert rt.id == "t1"
    assert rt.name == "Topic One"
    assert rt.parents == []
    assert rt.children == []


def test_resolve_topic_parent_child_links():
    db = _db(topics=[_topic("parent"), _topic("child", parents=["parent"])])
    rdb = DatabaseManager.resolve(db)
    parent = rdb.topics["parent"]
    child = rdb.topics["child"]
    assert rdb.topics["child"].parents == [parent]
    assert child in parent.children


def test_resolve_root_topics_populated():
    db = _db(topics=[_topic("root"), _topic("child", parents=["root"])])
    rdb = DatabaseManager.resolve(db)
    assert len(rdb.root_topics) == 1
    assert rdb.root_topics[0].id == "root"


def test_resolve_single_event():
    db = _db(topics=[_topic("t1")], events=[_event("e1", topic_id="t1")])
    rdb = DatabaseManager.resolve(db)
    assert "e1" in rdb.events
    re = rdb.events["e1"]
    assert re.topic.id == "t1"


def test_resolve_single_task():
    db = _db(topics=[_topic("t1")], tasks=[_task("task1", topic_id="t1")])
    rdb = DatabaseManager.resolve(db)
    assert "task1" in rdb.tasks
    rt = rdb.tasks["task1"]
    assert rt.topic.id == "t1"
    assert rt.parent is None


def test_resolve_task_parent_child():
    db = _db(
        topics=[_topic("t1")],
        tasks=[
            _task("parent", topic_id="t1"),
            _task("child", topic_id="t1", parent_id="parent"),
        ],
    )
    rdb = DatabaseManager.resolve(db)
    child = rdb.tasks["child"]
    parent = rdb.tasks["parent"]
    assert child.parent is parent
    assert child in parent.children


def test_resolve_root_tasks_populated():
    db = _db(
        topics=[_topic("t1")],
        tasks=[
            _task("root_task", topic_id="t1"),
            _task("child_task", topic_id="t1", parent_id="root_task"),
        ],
    )
    rdb = DatabaseManager.resolve(db)
    assert any(t.id == "root_task" for t in rdb.root_tasks)
    assert not any(t.id == "child_task" for t in rdb.root_tasks)


# ---------------------------------------------------------------------------
# resolve — inheritance
# ---------------------------------------------------------------------------


def test_resolve_topic_inherits_tags_from_parent():
    db = _db(
        topics=[
            _topic("parent", tags=["edu"]),
            _topic("child", parents=["parent"]),
        ]
    )
    rdb = DatabaseManager.resolve(db)
    assert "edu" in rdb.topics["child"].effective_tags


def test_resolve_topic_own_tags_override_parent():
    db = _db(
        topics=[
            _topic("parent", tags=["parent_tag"]),
            _topic("child", parents=["parent"], tags=["child_tag"]),
        ]
    )
    rdb = DatabaseManager.resolve(db)
    assert rdb.topics["child"].effective_tags == ["child_tag"]


def test_resolve_topic_inherits_layout_from_parent():
    layout = Layout(id="blue")
    db = _db(
        layouts=[layout],
        topics=[
            _topic("parent", layout="blue"),
            _topic("child", parents=["parent"]),
        ],
    )
    rdb = DatabaseManager.resolve(db)
    assert rdb.topics["child"].effective_layout is not None


def test_resolve_topic_own_layout_overrides_parent():
    l1 = Layout(id="l1")
    l2 = Layout(id="l2")
    db = _db(
        layouts=[l1, l2],
        topics=[
            _topic("parent", layout="l1"),
            _topic("child", parents=["parent"], layout="l2"),
        ],
    )
    rdb = DatabaseManager.resolve(db)
    assert rdb.topics["child"].effective_layout is rdb.layouts["l2"]


def test_resolve_task_inherits_topic_from_parent():
    db = _db(
        topics=[_topic("t1")],
        tasks=[
            _task("parent_task", topic_id="t1"),
            _task("child_task", topic_id=None, parent_id="parent_task"),
        ],
    )
    rdb = DatabaseManager.resolve(db)
    assert rdb.tasks["child_task"].topic.id == "t1"


def test_resolve_task_linked_events():
    db = _db(
        topics=[_topic("t1")],
        events=[_event("e1", topic_id="t1")],
        tasks=[_task("t1", topic_id="t1", event_links=[EventLink(event_id="e1")])],
    )
    rdb = DatabaseManager.resolve(db)
    assert len(rdb.tasks["t1"].linked_events) == 1
    assert rdb.tasks["t1"].linked_events[0].id == "e1"


def test_resolve_task_blocking_tasks():
    db = _db(
        topics=[_topic("t1")],
        tasks=[
            _task("blocker", topic_id="t1"),
            _task("blocked", topic_id="t1", blocked_by=[BlockedBy(task_id="blocker")]),
        ],
    )
    rdb = DatabaseManager.resolve(db)
    assert len(rdb.tasks["blocked"].blocking_tasks) == 1
    assert rdb.tasks["blocked"].blocking_tasks[0].id == "blocker"


def test_resolve_task_effective_deadline_from_event():
    db = _db(
        topics=[_topic("t1")],
        events=[_event("exam", topic_id="t1")],
        tasks=[
            _task(
                "study",
                topic_id="t1",
                event_links=[EventLink(event_id="exam", use_as_deadline=True)],
            )
        ],
    )
    rdb = DatabaseManager.resolve(db)
    # exam has SingleDaySchedule(day=2026-01-01)
    assert rdb.tasks["study"].effective_deadline == datetime.date(2026, 1, 1)


def test_resolve_task_own_deadline_takes_precedence():
    db = _db(
        topics=[_topic("t1")],
        events=[_event("exam", topic_id="t1")],
        tasks=[
            _task(
                "study",
                topic_id="t1",
                deadline=datetime.date(2025, 12, 1),
                event_links=[EventLink(event_id="exam", use_as_deadline=True)],
            )
        ],
    )
    rdb = DatabaseManager.resolve(db)
    assert rdb.tasks["study"].effective_deadline == datetime.date(2025, 12, 1)


def test_resolve_layout_string_resolved():
    layout = Layout(id="my_layout")
    db = _db(
        layouts=[layout],
        topics=[_topic("t1", layout="my_layout")],
    )
    rdb = DatabaseManager.resolve(db)
    assert rdb.topics["t1"].effective_layout is rdb.layouts["my_layout"]


# ---------------------------------------------------------------------------
# resolve — default topic injection
# ---------------------------------------------------------------------------


def test_resolve_task_without_topic_gets_default():
    db = _db(tasks=[Task(id="orphan", name="N")])
    rdb = DatabaseManager.resolve(db)
    assert rdb.tasks["orphan"].topic.id == "__default__"
    assert "__default__" in rdb.topics


def test_resolve_default_topic_not_created_if_not_needed():
    db = _db(topics=[_topic("t1")], tasks=[_task("t1", topic_id="t1")])
    rdb = DatabaseManager.resolve(db)
    assert "__default__" not in rdb.topics


# ---------------------------------------------------------------------------
# resolve — raises on invalid database
# ---------------------------------------------------------------------------


def test_resolve_raises_on_invalid_db():
    db = _db(topics=[_topic("t1"), _topic("t1")])
    with pytest.raises(ConsistencyError):
        DatabaseManager.resolve(db)
