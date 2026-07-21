"""Tests for the consistency Validator."""

from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.validating.Validator import Severity, validate_database


def _codes(text: str) -> set[str]:
    db = DatabaseLoader.loads(text)
    return {i.code for i in validate_database(db)}


def test_teacher_example_is_clean(teacher_db):
    issues = validate_database(teacher_db)
    errors = [i for i in issues if i.severity is Severity.ERROR]
    assert errors == [], f"unexpected errors: {[i.message for i in errors]}"


def test_unknown_topic_reference():
    assert "unknown-topic" in _codes("tasks:\n  - id: t\n    topic_ids: [ghost]\n")


def test_unknown_trait_reference():
    assert "unknown-trait" in _codes("tasks:\n  - id: t\n    traits: [ghost]\n")


def test_unknown_parent():
    assert "unknown-parent" in _codes("tasks:\n  - id: t\n    parent_id: ghost\n")


def test_unknown_relation_and_event_link():
    codes = _codes(
        "tasks:\n"
        "  - id: t\n"
        "    relations: [{task: ghost, type: requires}]\n"
        "    event_links: [{event: ghost}]\n"
    )
    assert "unknown-relation" in codes
    assert "unknown-event-link" in codes


def test_self_parent():
    assert "self-parent" in _codes("topics:\n  - id: a\n    parent_ids: [a]\n")


def test_topic_cycle():
    codes = _codes("topics:\n  - id: a\n    parent_ids: [b]\n  - id: b\n    parent_ids: [a]\n")
    assert "topic-cycle" in codes


def test_task_cycle():
    codes = _codes("tasks:\n  - id: a\n    parent_id: b\n  - id: b\n    parent_id: a\n")
    assert "task-cycle" in codes


def test_bad_weekly_schedule():
    codes = _codes("events:\n  - id: e\n    schedules: [{type: weekly, week_days: []}]\n")
    assert "bad-schedule" in codes


def test_bad_multi_day_order():
    codes = _codes(
        "events:\n"
        "  - id: e\n"
        "    schedules: [{type: multi_day, start_day: '2026-05-10', end_day: '2026-05-01'}]\n"
    )
    assert "bad-schedule" in codes


def test_duplicate_id_warning():
    db = DatabaseLoader.loads("topics:\n  - id: a\n  - id: a\n")
    issues = validate_database(db)
    dup = [i for i in issues if i.code == "duplicate-id"]
    assert dup and dup[0].severity is Severity.WARNING


def test_redundant_time_warning():
    db = DatabaseLoader.loads(
        "events:\n"
        "  - id: e\n"
        "    schedules:\n"
        "      - {type: weekly, week_days: [monday], start_time: '10:00',"
        " end_time: '11:00', duration: 30m}\n"
    )
    issues = validate_database(db)
    assert any(i.code == "schedule-redundant-time" for i in issues)
