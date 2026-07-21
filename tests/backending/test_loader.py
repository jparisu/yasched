"""Tests for DatabaseLoader parsing (including xyml includes)."""

import pytest

from yasched.backending.loading.DatabaseLoader import DatabaseLoader, DatabaseLoadError
from yasched.coring._shared import RelationType
from yasched.coring.Schedule import (
    MonthlySchedule,
    MultiDaySchedule,
    SingleDaySchedule,
    WeeklySchedule,
    YearlySchedule,
)


def test_loads_teacher_example(teacher_db):
    assert len(teacher_db.topics) == 7
    assert len(teacher_db.events) == 10
    assert len(teacher_db.tasks) == 10
    assert len(teacher_db.traits) == 7


def test_default_layer_parsed(teacher_db):
    assert teacher_db.default_attributes["priority"] == 1
    assert teacher_db.default_layout is not None
    assert teacher_db.default_layout.shape.type == "rounded"


def test_trait_shapes(teacher_db):
    assert teacher_db.traits["easy"].attributes == {"difficulty": "easy"}
    assert teacher_db.traits["easy"].layout is None  # attributes-only
    assert teacher_db.traits["exam-style"].attributes == {}  # layout-only
    assert teacher_db.traits["exam-style"].layout is not None
    assert teacher_db.traits["hard"].layout is not None  # both


def test_all_schedule_types_present(teacher_db):
    kinds = {type(s) for e in teacher_db.events.values() for s in e.schedules}
    assert WeeklySchedule in kinds
    assert MonthlySchedule in kinds
    assert YearlySchedule in kinds
    assert SingleDaySchedule in kinds
    assert MultiDaySchedule in kinds


def test_weekly_schedule_parsed(teacher_db):
    lecture = teacher_db.events["math101-lecture"]
    sched = lecture.schedules[0]
    assert isinstance(sched, WeeklySchedule)
    assert len(sched.week_days) == 2
    assert sched.start_time.to_hhmm() == "10:00"
    assert sched.duration.to_minutes() == 60


def test_ext_directive_merged_subevent(teacher_db):
    cancel = teacher_db.events["math101-lecture-cancel"]
    assert cancel.parent_id == "math101-lecture"
    assert cancel.attributes["status"] == "cancelled"  # from template
    assert "cancelled" in cancel.tags  # from template
    assert cancel.layout.icon.value == "❌"  # from template


def test_relation_types_and_shorthand(teacher_db):
    grade = teacher_db.tasks["grade-midterm"]
    by_target = {r.task_id: r.type for r in grade.relations}
    assert by_target["make-slides"] is RelationType.NEEDS
    assert by_target["prepare-exercises"] is RelationType.REQUIRES

    renew = teacher_db.tasks["renew-contract"]
    assert renew.relations[0].task_id == "submit-grades"
    assert renew.relations[0].type is RelationType.CONNECTED  # shorthand default


def test_event_links_parsed(teacher_db):
    grade = teacher_db.tasks["grade-midterm"]
    link = grade.event_links[0]
    assert link.event_id == "midterm-exam"
    assert link.use_as_deadline is True
    assert link.as_context is True


def test_multi_topic_task(teacher_db):
    assert teacher_db.tasks["submit-grades"].topic_ids == ["math-101", "admin"]


def test_single_topic_string_coerced_to_list():
    db = DatabaseLoader.loads(
        "tasks:\n  - id: t\n    name: T\n    topic_ids: solo\n",
    )
    assert db.tasks["t"].topic_ids == ["solo"]


def test_missing_id_raises():
    with pytest.raises(DatabaseLoadError):
        DatabaseLoader.loads("tasks:\n  - name: no id\n")


def test_unknown_schedule_type_raises():
    with pytest.raises(DatabaseLoadError):
        DatabaseLoader.loads(
            "events:\n  - id: e\n    name: E\n    schedules:\n      - type: fortnightly\n"
        )


def test_empty_document_is_empty_database():
    db = DatabaseLoader.loads("")
    assert not db.topics and not db.events and not db.tasks
