"""Integration tests: load basic_example → resolve → query."""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from yasched.backending.interfacing.DatabaseInterface import DatabaseInterface
from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.managing.DatabaseManager import DatabaseManager
from yasched.coring._shared import TaskStatus

BASIC_EXAMPLE = (
    Path(__file__).parent.parent.parent / "resources" / "basic_example" / "basic_example_main.yaml"
)


@pytest.fixture(scope="module")
def rdb():
    if not BASIC_EXAMPLE.exists():
        pytest.skip("basic_example not found")
    db = DatabaseLoader.load(BASIC_EXAMPLE)
    return DatabaseManager.resolve(db)


@pytest.fixture(scope="module")
def iface(rdb):
    return DatabaseInterface(rdb)


# ---------------------------------------------------------------------------
# Database is valid and loadable
# ---------------------------------------------------------------------------


def test_basic_example_loads_without_errors(rdb):
    assert len(rdb.topics) > 0
    assert len(rdb.events) > 0
    assert len(rdb.tasks) > 0


def test_basic_example_topic_ids(rdb):
    ids = set(rdb.topics.keys())
    assert "uni" in ids
    assert "exams" in ids
    assert "classes" in ids
    assert "my" in ids


def test_basic_example_event_ids(rdb):
    ids = set(rdb.events.keys())
    assert "math_exam" in ids
    assert "math_classes" in ids


def test_basic_example_task_ids(rdb):
    ids = set(rdb.tasks.keys())
    assert "math_study" in ids
    assert "xmas" in ids


# ---------------------------------------------------------------------------
# Topic resolution
# ---------------------------------------------------------------------------


def test_exams_topic_has_parent_uni(rdb):
    exams = rdb.topics["exams"]
    assert any(p.id == "uni" for p in exams.parents)


def test_exams_inherits_tags_from_uni(rdb):
    uni = rdb.topics["uni"]
    exams = rdb.topics["exams"]
    for tag in uni.effective_tags:
        assert tag in exams.effective_tags


def test_uni_is_root_topic(rdb):
    assert any(t.id == "uni" for t in rdb.root_topics)


# ---------------------------------------------------------------------------
# Event resolution
# ---------------------------------------------------------------------------


def test_math_exam_topic_resolved(rdb):
    exam = rdb.events["math_exam"]
    assert exam.topic.id == "exams"


def test_math_classes_weekly_schedule(rdb):
    from yasched.coring.WeeklySchedule import WeeklySchedule

    classes = rdb.events["math_classes"]
    assert any(isinstance(s, WeeklySchedule) for s in classes.schedules)


# ---------------------------------------------------------------------------
# Task resolution
# ---------------------------------------------------------------------------


def test_math_study_linked_to_math_exam(rdb):
    task = rdb.tasks["math_study"]
    assert any(e.id == "math_exam" for e in task.linked_events)


def test_math_study_effective_deadline_from_event(rdb):
    task = rdb.tasks["math_study"]
    assert task.effective_deadline == datetime.date(2026, 1, 15)


def test_xmas_gifts_has_blocking_task(rdb):
    gifts = rdb.tasks["xmas_gifts"]
    assert any(t.id == "xmas_gifts_list" for t in gifts.blocking_tasks)


def test_xmas_gifts_list_is_subtask_of_xmas(rdb):
    gifts_list = rdb.tasks["xmas_gifts_list"]
    assert gifts_list.parent is not None
    assert gifts_list.parent.id == "xmas"


# ---------------------------------------------------------------------------
# Interface queries on real data
# ---------------------------------------------------------------------------


def test_query_tasks_by_status_done(iface):
    done = iface.get_tasks_by_status(TaskStatus.DONE)
    assert any(t.id == "xmas_gifts_list" for t in done)


def test_query_math_exam_on_date(iface):
    events = iface.get_events_in_range(datetime.date(2026, 1, 15), datetime.date(2026, 1, 15))
    assert any(e.id == "math_exam" for e in events)


def test_query_daily_schedule_exam_day(iface):
    view = iface.get_daily_schedule(datetime.date(2026, 1, 15))
    assert any(e.id == "math_exam" for e in view.events)


def test_query_weekly_schedule_returns_7_days(iface):
    # 2026-01-12 is a Monday
    view = iface.get_weekly_schedule(datetime.date(2026, 1, 12))
    assert len(view.days) == 7


def test_query_upcoming_deadlines_includes_math_study(iface):
    result = iface.get_upcoming_deadlines(days_ahead=365, reference_date=datetime.date(2026, 1, 1))
    ids = [t.id for t in result]
    assert "math_study" in ids


def test_query_exams_topic_tasks(iface):
    tasks = iface.get_tasks_by_topic("exams")
    assert any(t.id == "math_study" for t in tasks)


def test_query_root_topics(iface):
    roots = iface.get_root_topics()
    root_ids = {t.id for t in roots}
    assert "uni" in root_ids
    assert "my" in root_ids


def test_query_topic_subtree_uni(iface):
    subtree = iface.get_topic_subtree("uni")
    ids = {t.id for t in subtree}
    assert "exams" in ids
    assert "classes" in ids


def test_query_status_summary(iface):
    summary = iface.task_status_summary()
    total = sum(summary.values())
    assert total == len(iface.all_tasks())


def test_query_stale_blocks(iface):
    stale = iface.get_stale_blocks()
    # xmas_gifts_list is done, so xmas_gifts' block on it is stale
    assert any(t.id == "xmas_gifts" for t in stale)
