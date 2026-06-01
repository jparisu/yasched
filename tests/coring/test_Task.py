"""Tests for coring.Task."""

import datetime

import pytest

from yasched.coring._shared import (
    EffortRange,
    EventLink,
    RelationType,
    TaskRelation,
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
    assert t.topic_ids == []
    assert t.parent_id is None
    assert t.description is None
    assert t.tags == []
    assert t.deadline is None
    assert t.priority is None
    assert t.status == TaskStatus.TODO
    assert t.effort is None
    assert t.schedules == []
    assert t.event_links == []
    assert t.relations == []
    assert t.layout is None


def test_task_full_one_off():
    effort = EffortRange(Duration.from_string("1h"), Duration.from_string("3h"))
    event_link = EventLink(event_id="math_exam")
    relation = TaskRelation(
        task_id="study_ch2", type=RelationType.REQUIRES, description="Must finish first"
    )
    t = Task(
        id="study_ch3",
        topic_ids=["math"],
        name="Study chapter 3",
        description="Read and solve exercises",
        tags=["priority"],
        deadline=datetime.date(2026, 6, 10),
        priority=3,
        status=TaskStatus.IN_PROGRESS,
        effort=effort,
        event_links=[event_link],
        relations=[relation],
        layout=Layout(),
    )
    assert t.topic_ids == ["math"]
    assert t.deadline == datetime.date(2026, 6, 10)
    assert t.priority == 3
    assert t.status == TaskStatus.IN_PROGRESS
    assert len(t.event_links) == 1
    assert len(t.relations) == 1
    assert t.relations[0].type == RelationType.REQUIRES


def test_task_recurring_no_deadline():
    t = Task(id="review", name="Weekly review", schedules=[_schedule()])
    assert len(t.schedules) == 1
    assert t.deadline is None


def test_task_subtask_with_parent_id():
    t = Task(id="sub1", name="Subtask", parent_id="parent_task")
    assert t.parent_id == "parent_task"
    assert t.topic_ids == []  # inherited by backending


def test_task_is_frozen():
    t = Task(id="t", name="N")
    with pytest.raises((AttributeError, TypeError)):
        t.id = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Multiple topics
# ---------------------------------------------------------------------------


def test_task_single_topic():
    t = Task(id="t", name="N", topic_ids=["work"])
    assert t.topic_ids == ["work"]


def test_task_multiple_topics():
    t = Task(id="t", name="N", topic_ids=["work", "personal"])
    assert t.topic_ids == ["work", "personal"]


def test_task_no_topics():
    t = Task(id="t", name="N", topic_ids=[])
    assert t.topic_ids == []


# ---------------------------------------------------------------------------
# Task relations
# ---------------------------------------------------------------------------


def test_task_relation_requires():
    rel = TaskRelation(task_id="other", type=RelationType.REQUIRES)
    t = Task(id="t", name="N", relations=[rel])
    assert len(t.relations) == 1
    assert t.relations[0].type == RelationType.REQUIRES


def test_task_relation_all_types():
    for rel_type in RelationType:
        rel = TaskRelation(task_id="x", type=rel_type)
        assert rel.type == rel_type


def test_task_multiple_relations():
    rels = [
        TaskRelation(task_id="a", type=RelationType.REQUIRES),
        TaskRelation(task_id="b", type=RelationType.NEEDS),
        TaskRelation(task_id="c", type=RelationType.CONNECTED),
        TaskRelation(task_id="d", type=RelationType.SIMILAR),
    ]
    t = Task(id="t", name="N", relations=rels)
    assert len(t.relations) == 4


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_task_default_status_is_todo():
    t = Task(id="t", name="N")
    assert t.status == TaskStatus.TODO


def test_task_status_done():
    t = Task(id="t", name="N", status=TaskStatus.DONE)
    assert t.status == TaskStatus.DONE


def test_task_status_blocked_without_relations():
    # status can be BLOCKED independently of relations
    t = Task(id="t", name="N", status=TaskStatus.BLOCKED)
    assert t.status == TaskStatus.BLOCKED
    assert t.relations == []


def test_task_requires_relation_without_blocked_status():
    # REQUIRES relation does not automatically set status=BLOCKED
    rel = TaskRelation(task_id="other", type=RelationType.REQUIRES)
    t = Task(id="t", name="N", relations=[rel])
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
