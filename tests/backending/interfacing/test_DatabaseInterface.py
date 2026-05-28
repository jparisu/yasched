"""Tests for DatabaseInterface: query API over a ResolvedDatabase."""

from __future__ import annotations

import datetime

import pytest

from yasched.backending.Database import (
    Database,
)
from yasched.backending.interfacing.DatabaseInterface import (
    DailyView,
    DatabaseInterface,
    WeeklyView,
)
from yasched.backending.managing.DatabaseManager import DatabaseManager
from yasched.coring._shared import BlockedBy, EventLink, TaskStatus, Weekday, WeeklyAppointment
from yasched.coring.Event import Event
from yasched.coring.Layout import Layout
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.MultiDaySchedule import MultiDaySchedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring.YearlySchedule import YearlySchedule
from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

TODAY = datetime.date(2026, 5, 28)
ONE_HOUR = Duration.from_string("1h")


def _topic(id: str, name: str = "N", tags=None, parents=None, layout=None):
    return Topic(id=id, name=name, tags=tags or [], parent_ids=parents or [], layout=layout)


def _event(id: str, topic_id: str, sched=None, blocking_level=None, name=None):
    s = sched or SingleDaySchedule(day=datetime.date(2026, 1, 15))
    return Event(
        id=id, topic_id=topic_id, name=name or id, schedules=[s], blocking_level=blocking_level
    )


def _task(
    id: str,
    topic_id: str | None = "t1",
    name=None,
    status=TaskStatus.TODO,
    deadline=None,
    priority=None,
    tags=None,
    parent_id=None,
    event_links=None,
    blocked_by=None,
    schedules=None,
):
    return Task(
        id=id,
        name=name or id,
        topic_id=topic_id,
        status=status,
        deadline=deadline,
        priority=priority,
        tags=tags or [],
        parent_id=parent_id,
        event_links=event_links or [],
        blocked_by=blocked_by or [],
        schedules=schedules or [],
    )


def _build_db(*topics, events=(), tasks=(), layouts=()):
    db = Database(
        layouts=list(layouts),
        topics=list(topics),
        events=list(events),
        tasks=list(tasks),
    )
    return DatabaseManager.resolve(db)


@pytest.fixture
def simple_rdb():
    t1 = _topic("t1", name="Work", tags=["work"])
    t2 = _topic("t2", name="Personal", tags=["personal"])
    e1 = _event("e1", "t1", sched=SingleDaySchedule(day=datetime.date(2026, 6, 1)))
    e2 = _event("e2", "t2", sched=SingleDaySchedule(day=datetime.date(2026, 6, 15)))
    task1 = _task("task1", "t1", deadline=datetime.date(2026, 6, 10), priority=3)
    task2 = _task("task2", "t2", status=TaskStatus.DONE, priority=1)
    task3 = _task("task3", "t1", status=TaskStatus.BLOCKED, priority=5)
    return _build_db(t1, t2, events=[e1, e2], tasks=[task1, task2, task3])


@pytest.fixture
def iface(simple_rdb):
    return DatabaseInterface(simple_rdb)


# ---------------------------------------------------------------------------
# Primitive queries
# ---------------------------------------------------------------------------


def test_get_topic_found(iface):
    t = iface.get_topic("t1")
    assert t.id == "t1"


def test_get_topic_not_found(iface):
    with pytest.raises(KeyError):
        iface.get_topic("ghost")


def test_get_event_found(iface):
    e = iface.get_event("e1")
    assert e.id == "e1"


def test_get_event_not_found(iface):
    with pytest.raises(KeyError):
        iface.get_event("ghost")


def test_get_task_found(iface):
    t = iface.get_task("task1")
    assert t.id == "task1"


def test_get_task_not_found(iface):
    with pytest.raises(KeyError):
        iface.get_task("ghost")


def test_all_topics_returns_all(iface):
    assert len(iface.all_topics()) == 2


def test_all_events_returns_all(iface):
    assert len(iface.all_events()) == 2


def test_all_tasks_returns_all(iface):
    assert len(iface.all_tasks()) == 3


def test_get_layout(simple_rdb):
    layout = Layout(id="my_layout")
    db = Database(
        layouts=[layout],
        topics=[_topic("t1")],
        events=[],
        tasks=[],
    )
    rdb = DatabaseManager.resolve(db)
    iface = DatabaseInterface(rdb)
    assert iface.get_layout("my_layout") is rdb.layouts["my_layout"]


def test_get_layout_not_found(iface):
    with pytest.raises(KeyError):
        iface.get_layout("ghost")


def test_all_layouts(simple_rdb):
    layout = Layout(id="l1")
    db = Database(layouts=[layout], topics=[_topic("t1")], events=[], tasks=[])
    rdb = DatabaseManager.resolve(db)
    iface = DatabaseInterface(rdb)
    assert len(iface.all_layouts()) == 1


# ---------------------------------------------------------------------------
# Schedule queries
# ---------------------------------------------------------------------------


def test_get_events_in_range_single_day_hit(iface):
    result = iface.get_events_in_range(datetime.date(2026, 6, 1), datetime.date(2026, 6, 1))
    assert any(e.id == "e1" for e in result)


def test_get_events_in_range_miss(iface):
    result = iface.get_events_in_range(datetime.date(2025, 1, 1), datetime.date(2025, 12, 31))
    assert result == []


def test_get_events_in_range_multi_day_overlap():
    t1 = _topic("t1")
    e = _event(
        "e1",
        "t1",
        sched=MultiDaySchedule(
            start_day=datetime.date(2026, 6, 10), end_day=datetime.date(2026, 6, 20)
        ),
    )
    rdb = _build_db(t1, events=[e])
    iface = DatabaseInterface(rdb)
    result = iface.get_events_in_range(datetime.date(2026, 6, 15), datetime.date(2026, 6, 15))
    assert any(ev.id == "e1" for ev in result)


def test_get_events_in_range_weekly_hit():
    t1 = _topic("t1")
    appt = WeeklyAppointment(
        week_day=Weekday.MONDAY, start_time=datetime.time(9), duration=ONE_HOUR
    )
    e = _event("e1", "t1", sched=WeeklySchedule(appointments=[appt]))
    rdb = _build_db(t1, events=[e])
    iface = DatabaseInterface(rdb)
    # 2026-06-01 is a Monday
    result = iface.get_events_in_range(datetime.date(2026, 6, 1), datetime.date(2026, 6, 1))
    assert any(ev.id == "e1" for ev in result)


def test_get_events_in_range_weekly_miss():
    t1 = _topic("t1")
    appt = WeeklyAppointment(
        week_day=Weekday.MONDAY, start_time=datetime.time(9), duration=ONE_HOUR
    )
    e = _event("e1", "t1", sched=WeeklySchedule(appointments=[appt]))
    rdb = _build_db(t1, events=[e])
    iface = DatabaseInterface(rdb)
    # 2026-06-02 is a Tuesday — no Monday in that single day
    result = iface.get_events_in_range(datetime.date(2026, 6, 2), datetime.date(2026, 6, 2))
    assert not any(ev.id == "e1" for ev in result)


def test_get_events_in_range_monthly_hit():
    t1 = _topic("t1")
    e = _event(
        "e1",
        "t1",
        sched=MonthlySchedule(day_of_month=15, start_time=datetime.time(10), duration=ONE_HOUR),
    )
    rdb = _build_db(t1, events=[e])
    iface = DatabaseInterface(rdb)
    result = iface.get_events_in_range(datetime.date(2026, 6, 15), datetime.date(2026, 6, 15))
    assert any(ev.id == "e1" for ev in result)


def test_get_events_in_range_yearly_hit():
    t1 = _topic("t1")
    e = _event("e1", "t1", sched=YearlySchedule(month=12, day=25))
    rdb = _build_db(t1, events=[e])
    iface = DatabaseInterface(rdb)
    result = iface.get_events_in_range(datetime.date(2026, 12, 25), datetime.date(2026, 12, 25))
    assert any(ev.id == "e1" for ev in result)


def test_get_tasks_in_range_recurring_hit():
    t1 = _topic("t1")
    appt = WeeklyAppointment(
        week_day=Weekday.MONDAY, start_time=datetime.time(9), duration=ONE_HOUR
    )
    task = _task("t1", "t1", schedules=[WeeklySchedule(appointments=[appt])])
    rdb = _build_db(t1, tasks=[task])
    iface = DatabaseInterface(rdb)
    result = iface.get_tasks_in_range(datetime.date(2026, 6, 1), datetime.date(2026, 6, 1))
    assert any(t.id == "t1" for t in result)


def test_get_daily_schedule_returns_daily_view(iface):
    view = iface.get_daily_schedule(datetime.date(2026, 6, 1))
    assert isinstance(view, DailyView)
    assert view.date == datetime.date(2026, 6, 1)
    assert any(e.id == "e1" for e in view.events)


def test_get_weekly_schedule_returns_weekly_view(iface):
    # 2026-06-01 is a Monday
    view = iface.get_weekly_schedule(datetime.date(2026, 6, 1))
    assert isinstance(view, WeeklyView)
    assert len(view.days) == 7
    assert view.days[0].date == datetime.date(2026, 6, 1)
    assert view.days[6].date == datetime.date(2026, 6, 7)


# ---------------------------------------------------------------------------
# Task queries
# ---------------------------------------------------------------------------


def test_get_tasks_by_status_todo(iface):
    result = iface.get_tasks_by_status(TaskStatus.TODO)
    assert all(t.status == TaskStatus.TODO for t in result)
    assert any(t.id == "task1" for t in result)


def test_get_tasks_by_status_done(iface):
    result = iface.get_tasks_by_status(TaskStatus.DONE)
    assert all(t.status == TaskStatus.DONE for t in result)


def test_get_tasks_by_topic_direct(iface):
    result = iface.get_tasks_by_topic("t1")
    assert all(t.topic.id == "t1" for t in result)


def test_get_tasks_by_topic_include_subtopics():
    t_root = _topic("root", tags=["r"])
    t_child = _topic("child", parents=["root"])
    task_root = _task("t_root", "root")
    task_child = _task("t_child", "child")
    rdb = _build_db(t_root, t_child, tasks=[task_root, task_child])
    iface = DatabaseInterface(rdb)
    result = iface.get_tasks_by_topic("root", include_subtopics=True)
    ids = [t.id for t in result]
    assert "t_root" in ids
    assert "t_child" in ids


def test_get_tasks_with_tag():
    t1 = _topic("t1", tags=["work"])
    task = _task("t1", "t1", tags=["urgent"])
    rdb = _build_db(t1, tasks=[task])
    iface = DatabaseInterface(rdb)
    assert any(t.id == "t1" for t in iface.get_tasks_with_tag("urgent"))
    assert iface.get_tasks_with_tag("nonexistent") == []


def test_get_tasks_by_priority_range(iface):
    result = iface.get_tasks_by_priority(min_priority=3)
    assert all(t.priority is not None and t.priority >= 3 for t in result)


def test_get_upcoming_deadlines(iface):
    result = iface.get_upcoming_deadlines(days_ahead=30, reference_date=datetime.date(2026, 5, 28))
    assert any(t.id == "task1" for t in result)


def test_get_upcoming_deadlines_sorted(iface):
    result = iface.get_upcoming_deadlines(days_ahead=365, reference_date=datetime.date(2026, 1, 1))
    deadlines = [t.effective_deadline for t in result if t.effective_deadline]
    assert deadlines == sorted(deadlines)


def test_get_overdue_tasks():
    t1 = _topic("t1")
    task = _task("past_due", "t1", deadline=datetime.date(2020, 1, 1))
    rdb = _build_db(t1, tasks=[task])
    iface = DatabaseInterface(rdb)
    result = iface.get_overdue_tasks(reference_date=datetime.date(2026, 1, 1))
    assert any(t.id == "past_due" for t in result)


def test_get_overdue_tasks_excludes_done():
    t1 = _topic("t1")
    task = _task("done_task", "t1", deadline=datetime.date(2020, 1, 1), status=TaskStatus.DONE)
    rdb = _build_db(t1, tasks=[task])
    iface = DatabaseInterface(rdb)
    result = iface.get_overdue_tasks(reference_date=datetime.date(2026, 1, 1))
    assert not any(t.id == "done_task" for t in result)


def test_get_blocked_tasks(iface):
    result = iface.get_blocked_tasks()
    assert any(t.id == "task3" for t in result)


def test_get_blocking_tasks():
    t1 = _topic("t1")
    blocker = _task("blocker", "t1")
    blocked = _task("blocked", "t1", blocked_by=[BlockedBy(task_id="blocker")])
    rdb = _build_db(t1, tasks=[blocker, blocked])
    iface = DatabaseInterface(rdb)
    result = iface.get_blocking_tasks("blocked")
    assert any(t.id == "blocker" for t in result)


def test_get_task_children():
    t1 = _topic("t1")
    parent = _task("parent", "t1")
    child1 = _task("child1", parent_id="parent")
    child2 = _task("child2", parent_id="parent")
    rdb = _build_db(t1, tasks=[parent, child1, child2])
    iface = DatabaseInterface(rdb)
    children = iface.get_task_children("parent")
    assert len(children) == 2
    assert {c.id for c in children} == {"child1", "child2"}


def test_get_task_subtree():
    t1 = _topic("t1")
    parent = _task("root", "t1")
    child = _task("child", parent_id="root")
    grandchild = _task("grand", parent_id="child")
    rdb = _build_db(t1, tasks=[parent, child, grandchild])
    iface = DatabaseInterface(rdb)
    subtree = iface.get_task_subtree("root")
    ids = {t.id for t in subtree}
    assert "child" in ids
    assert "grand" in ids
    assert "root" not in ids


def test_get_task_events():
    t1 = _topic("t1")
    e = _event("e1", "t1")
    task = _task("t1", "t1", event_links=[EventLink(event_id="e1")])
    rdb = _build_db(t1, events=[e], tasks=[task])
    iface = DatabaseInterface(rdb)
    result = iface.get_task_events("t1")
    assert any(ev.id == "e1" for ev in result)


def test_search_tasks(iface):
    result = iface.search_tasks("task1")
    assert any(t.id == "task1" for t in result)


def test_search_tasks_no_match(iface):
    result = iface.search_tasks("zzznomatch")
    assert result == []


# ---------------------------------------------------------------------------
# Topic queries
# ---------------------------------------------------------------------------


def test_get_root_topics(iface):
    roots = iface.get_root_topics()
    assert len(roots) == 2  # t1 and t2, both root


def test_get_root_topics_with_hierarchy():
    t_root = _topic("root")
    t_child = _topic("child", parents=["root"])
    rdb = _build_db(t_root, t_child)
    iface = DatabaseInterface(rdb)
    roots = iface.get_root_topics()
    assert len(roots) == 1
    assert roots[0].id == "root"


def test_get_topic_children():
    t_root = _topic("root")
    t_child1 = _topic("child1", parents=["root"])
    t_child2 = _topic("child2", parents=["root"])
    rdb = _build_db(t_root, t_child1, t_child2)
    iface = DatabaseInterface(rdb)
    children = iface.get_topic_children("root")
    assert {c.id for c in children} == {"child1", "child2"}


def test_get_topic_subtree():
    t_root = _topic("root")
    t_child = _topic("child", parents=["root"])
    t_grand = _topic("grand", parents=["child"])
    rdb = _build_db(t_root, t_child, t_grand)
    iface = DatabaseInterface(rdb)
    subtree = iface.get_topic_subtree("root")
    ids = {t.id for t in subtree}
    assert "child" in ids
    assert "grand" in ids
    assert "root" not in ids


def test_get_topic_ancestors():
    t_root = _topic("root")
    t_child = _topic("child", parents=["root"])
    t_grand = _topic("grand", parents=["child"])
    rdb = _build_db(t_root, t_child, t_grand)
    iface = DatabaseInterface(rdb)
    ancestors = iface.get_topic_ancestors("grand")
    ids = [t.id for t in ancestors]
    assert "child" in ids
    assert "root" in ids
    assert ids.index("child") < ids.index("root")  # nearest first


def test_get_topics_with_tag():
    t1 = _topic("t1", tags=["edu"])
    t2 = _topic("t2", tags=["work"])
    rdb = _build_db(t1, t2)
    iface = DatabaseInterface(rdb)
    result = iface.get_topics_with_tag("edu")
    assert any(t.id == "t1" for t in result)
    assert not any(t.id == "t2" for t in result)


def test_search_topics(iface):
    result = iface.search_topics("Work")
    assert any(t.id == "t1" for t in result)


# ---------------------------------------------------------------------------
# Check queries
# ---------------------------------------------------------------------------


def test_task_status_summary(iface):
    summary = iface.task_status_summary()
    assert summary[TaskStatus.TODO] >= 1
    assert summary[TaskStatus.DONE] >= 1
    assert summary[TaskStatus.BLOCKED] >= 1


def test_task_count_by_topic(iface):
    counts = iface.task_count_by_topic()
    assert "t1" in counts
    assert counts["t1"] >= 1


def test_get_stale_blocks():
    t1 = _topic("t1")
    blocker = _task("done_blocker", "t1", status=TaskStatus.DONE)
    blocked = _task(
        "still_blocked",
        "t1",
        status=TaskStatus.BLOCKED,
        blocked_by=[BlockedBy(task_id="done_blocker")],
    )
    rdb = _build_db(t1, tasks=[blocker, blocked])
    iface = DatabaseInterface(rdb)
    stale = iface.get_stale_blocks()
    assert any(t.id == "still_blocked" for t in stale)


def test_get_conflicts_blocking_level():
    t1 = _topic("t1")
    # Two events on the same day, one with blocking_level 2
    e1 = _event(
        "blocker_ev", "t1", sched=SingleDaySchedule(day=datetime.date(2026, 6, 1)), blocking_level=2
    )
    e2 = _event(
        "blocked_ev",
        "t1",
        sched=SingleDaySchedule(day=datetime.date(2026, 6, 1)),
        blocking_level=None,
    )
    rdb = _build_db(t1, events=[e1, e2])
    iface = DatabaseInterface(rdb)
    conflicts = iface.get_conflicts(start=datetime.date(2026, 6, 1), end=datetime.date(2026, 6, 1))
    assert len(conflicts) >= 1
    assert any(c.blocker.id == "blocker_ev" for c in conflicts)
