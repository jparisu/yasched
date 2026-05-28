"""Tests for coring.Task."""

import datetime

import pytest

from yasched.coring._shared import (
    BlockedBy,
    EffortRange,
    EventLink,
    TaskStatus,
)
from yasched.coring.Layout import Layout
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.utilizing.timing.Duration import Duration


def _schedule() -> SingleDaySchedule:
    return SingleDaySchedule(day=datetime.date(2026, 6, 15))


# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_task_minimal():
    t = Task(id="t1", name="Study chapter 3")
    assert t.id == "t1"
    assert t.name == "Study chapter 3"
    assert t.topic_id is None
    assert t.parent_id is None
    assert t.description is None
    assert t.tags == []
    assert t.deadline is None
    assert t.priority is None
    assert t.status == TaskStatus.TODO
    assert t.effort is None
    assert t.schedules == []
    assert t.event_links == []
    assert t.blocked_by == []
    assert t.layout is None


def test_task_full_one_off():
    effort = EffortRange(Duration.from_string("1h"), Duration.from_string("3h"))
    event_link = EventLink(event_id="math_exam")
    blocked = BlockedBy(task_id="study_ch2", description="Must finish first")
    t = Task(
        id="study_ch3",
        topic_id="math",
        name="Study chapter 3",
        description="Read and solve exercises",
        tags=["priority"],
        deadline=datetime.date(2026, 6, 10),
        priority=3,
        status=TaskStatus.IN_PROGRESS,
        effort=effort,
        event_links=[event_link],
        blocked_by=[blocked],
        layout=Layout(),
    )
    assert t.topic_id == "math"
    assert t.deadline == datetime.date(2026, 6, 10)
    assert t.priority == 3
    assert t.status == TaskStatus.IN_PROGRESS
    assert len(t.event_links) == 1
    assert len(t.blocked_by) == 1


def test_task_recurring_no_deadline():
    t = Task(id="review", name="Weekly review", schedules=[_schedule()])
    assert len(t.schedules) == 1
    assert t.deadline is None


def test_task_subtask_with_parent_id():
    t = Task(id="sub1", name="Subtask", parent_id="parent_task")
    assert t.parent_id == "parent_task"
    assert t.topic_id is None  # inherited by backending


def test_task_is_frozen():
    t = Task(id="t", name="N")
    with pytest.raises((AttributeError, TypeError)):
        t.id = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_task_default_status_is_todo():
    t = Task(id="t", name="N")
    assert t.status == TaskStatus.TODO


def test_task_status_done():
    t = Task(id="t", name="N", status=TaskStatus.DONE)
    assert t.status == TaskStatus.DONE


def test_task_status_blocked_without_blocked_by():
    # status can be BLOCKED independently of blocked_by entries
    t = Task(id="t", name="N", status=TaskStatus.BLOCKED)
    assert t.status == TaskStatus.BLOCKED
    assert t.blocked_by == []


def test_task_blocked_by_without_blocked_status():
    # blocked_by does not automatically set status=BLOCKED
    bb = BlockedBy(task_id="other")
    t = Task(id="t", name="N", blocked_by=[bb])
    assert t.status == TaskStatus.TODO


def test_task_multiple_event_links():
    links = [EventLink(event_id=f"e{i}") for i in range(3)]
    t = Task(id="t", name="N", event_links=links)
    assert len(t.event_links) == 3


def test_task_priority_1_lowest():
    t = Task(id="t", name="N", priority=1)
    assert t.priority == 1


def test_task_very_high_priority():
    t = Task(id="t", name="N", priority=100)
    assert t.priority == 100


def test_task_layout_as_string_reference():
    t = Task(id="t", name="N", layout="theme_x")
    assert t.layout == "theme_x"


def test_task_empty_tags_lists_are_independent():
    t1 = Task(id="a", name="A")
    t2 = Task(id="b", name="B")
    assert t1.tags is not t2.tags
    assert t1.schedules is not t2.schedules


# ---------------------------------------------------------------------------
# Construction — failure cases
# ---------------------------------------------------------------------------


def test_task_schedules_and_deadline_raises():
    with pytest.raises(ValueError):
        Task(
            id="t",
            name="N",
            schedules=[_schedule()],
            deadline=datetime.date(2026, 6, 30),
        )


def test_task_schedules_and_deadline_raises_regardless_of_order():
    with pytest.raises(ValueError):
        Task(
            id="t",
            name="N",
            deadline=datetime.date(2026, 6, 30),
            schedules=[_schedule()],
        )
