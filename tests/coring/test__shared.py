"""Tests for coring._shared."""

import datetime

import pytest

from yasched.coring._shared import (
    EffortRange,
    EventLink,
    RelationType,
    TaskRelation,
    TaskStatus,
    Weekday,
    WeeklyAppointment,
)
from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# Weekday — sweet path
# ---------------------------------------------------------------------------


def test_weekday_values_match_strings():
    assert Weekday.MONDAY.value == "monday"
    assert Weekday.SUNDAY.value == "sunday"


def test_weekday_from_string_canonical():
    assert Weekday.from_string("monday") == Weekday.MONDAY
    assert Weekday.from_string("friday") == Weekday.FRIDAY


def test_weekday_from_string_uppercase():
    assert Weekday.from_string("MONDAY") == Weekday.MONDAY


def test_weekday_from_string_mixed_case():
    assert Weekday.from_string("Wednesday") == Weekday.WEDNESDAY


def test_weekday_from_string_all_abbreviations():
    pairs = [
        ("mon", Weekday.MONDAY),
        ("tue", Weekday.TUESDAY),
        ("wed", Weekday.WEDNESDAY),
        ("thu", Weekday.THURSDAY),
        ("fri", Weekday.FRIDAY),
        ("sat", Weekday.SATURDAY),
        ("sun", Weekday.SUNDAY),
    ]
    for abbr, expected in pairs:
        assert Weekday.from_string(abbr) == expected


def test_weekday_from_string_all_full_names():
    for day in Weekday:
        assert Weekday.from_string(day.value) == day


# ---------------------------------------------------------------------------
# Weekday — failure cases
# ---------------------------------------------------------------------------


def test_weekday_from_string_unknown_raises():
    with pytest.raises(ValueError):
        Weekday.from_string("funday")


def test_weekday_from_string_empty_raises():
    with pytest.raises(ValueError):
        Weekday.from_string("")


def test_weekday_from_string_partial_raises():
    with pytest.raises(ValueError):
        Weekday.from_string("mond")


# ---------------------------------------------------------------------------
# WeeklyAppointment — sweet path
# ---------------------------------------------------------------------------


def _time(h: int, m: int = 0) -> datetime.time:
    return datetime.time(h, m)


def test_weekly_appointment_with_end_time():
    wa = WeeklyAppointment(
        week_day=Weekday.MONDAY,
        start_time=_time(9),
        end_time=_time(10),
    )
    assert wa.week_day == Weekday.MONDAY
    assert wa.end_time == _time(10)
    assert wa.duration is None


def test_weekly_appointment_with_duration():
    wa = WeeklyAppointment(
        week_day=Weekday.FRIDAY,
        start_time=_time(14),
        duration=Duration.from_string("45m"),
    )
    assert wa.duration == Duration.from_string("45m")
    assert wa.end_time is None


def test_weekly_appointment_is_frozen():
    wa = WeeklyAppointment(week_day=Weekday.MONDAY, start_time=_time(9), end_time=_time(10))
    with pytest.raises((AttributeError, TypeError)):
        wa.week_day = Weekday.TUESDAY  # type: ignore[misc]


# ---------------------------------------------------------------------------
# WeeklyAppointment — corner cases
# ---------------------------------------------------------------------------


def test_weekly_appointment_midnight_start():
    wa = WeeklyAppointment(
        week_day=Weekday.SATURDAY,
        start_time=_time(0),
        duration=Duration.from_string("30m"),
    )
    assert wa.start_time == datetime.time(0, 0)


def test_weekly_appointment_end_time_before_start_is_allowed():
    # coring stores data as-is; backending validates ordering
    wa = WeeklyAppointment(
        week_day=Weekday.MONDAY,
        start_time=_time(10),
        end_time=_time(9),
    )
    assert wa.end_time == _time(9)


# ---------------------------------------------------------------------------
# WeeklyAppointment — failure cases
# ---------------------------------------------------------------------------


def test_weekly_appointment_both_end_and_duration_raises():
    with pytest.raises(ValueError):
        WeeklyAppointment(
            week_day=Weekday.MONDAY,
            start_time=_time(9),
            end_time=_time(10),
            duration=Duration.from_string("1h"),
        )


def test_weekly_appointment_neither_end_nor_duration_raises():
    with pytest.raises(ValueError):
        WeeklyAppointment(week_day=Weekday.MONDAY, start_time=_time(9))


# ---------------------------------------------------------------------------
# TaskStatus — sweet path
# ---------------------------------------------------------------------------


def test_task_status_all_values():
    assert TaskStatus.TODO.value == "todo"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.DONE.value == "done"
    assert TaskStatus.CANCELLED.value == "cancelled"
    assert TaskStatus.BLOCKED.value == "blocked"


def test_task_status_from_string():
    assert TaskStatus("todo") == TaskStatus.TODO
    assert TaskStatus("blocked") == TaskStatus.BLOCKED


# ---------------------------------------------------------------------------
# TaskStatus — failure cases
# ---------------------------------------------------------------------------


def test_task_status_unknown_raises():
    with pytest.raises(ValueError):
        TaskStatus("pending")


# ---------------------------------------------------------------------------
# EffortRange — sweet path
# ---------------------------------------------------------------------------


def test_effort_range_equal_bounds():
    er = EffortRange(min=Duration.from_string("1h"), max=Duration.from_string("1h"))
    assert er.min == er.max


def test_effort_range_min_less_than_max():
    er = EffortRange(min=Duration.from_string("30m"), max=Duration.from_string("2h"))
    assert er.min < er.max


def test_effort_range_is_frozen():
    er = EffortRange(min=Duration.from_string("1h"), max=Duration.from_string("2h"))
    with pytest.raises((AttributeError, TypeError)):
        er.min = Duration.from_string("30m")  # type: ignore[misc]


# ---------------------------------------------------------------------------
# EffortRange — failure cases
# ---------------------------------------------------------------------------


def test_effort_range_min_greater_than_max_raises():
    with pytest.raises(ValueError):
        EffortRange(min=Duration.from_string("3h"), max=Duration.from_string("1h"))


def test_effort_range_zero_min_nonzero_max():
    er = EffortRange(min=Duration.zero(), max=Duration.from_string("1h"))
    assert er.min.to_minutes() == 0


# ---------------------------------------------------------------------------
# EventLink — sweet path
# ---------------------------------------------------------------------------


def test_event_link_defaults():
    el = EventLink(event_id="math_exam")
    assert el.use_as_deadline is True
    assert el.as_context is True


def test_event_link_explicit_flags():
    el = EventLink(event_id="concert", use_as_deadline=False, as_context=False)
    assert el.use_as_deadline is False
    assert el.as_context is False


def test_event_link_is_frozen():
    el = EventLink(event_id="x")
    with pytest.raises((AttributeError, TypeError)):
        el.event_id = "y"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# EventLink — corner cases
# ---------------------------------------------------------------------------


def test_event_link_use_as_deadline_false_as_context_true():
    el = EventLink(event_id="e1", use_as_deadline=False, as_context=True)
    assert el.use_as_deadline is False
    assert el.as_context is True


def test_event_link_empty_id_allowed():
    # coring does not validate non-emptiness of IDs; backending does
    el = EventLink(event_id="")
    assert el.event_id == ""


# ---------------------------------------------------------------------------
# RelationType — sweet path
# ---------------------------------------------------------------------------


def test_relation_type_values():
    assert RelationType.REQUIRES.value == "requires"
    assert RelationType.NEEDS.value == "needs"
    assert RelationType.CONNECTED.value == "connected"
    assert RelationType.SIMILAR.value == "similar"


def test_relation_type_from_string():
    assert RelationType("requires") == RelationType.REQUIRES
    assert RelationType("similar") == RelationType.SIMILAR


def test_relation_type_unknown_raises():
    with pytest.raises(ValueError):
        RelationType("blocks")


# ---------------------------------------------------------------------------
# TaskRelation — sweet path
# ---------------------------------------------------------------------------


def test_task_relation_no_description():
    rel = TaskRelation(task_id="study_ch2", type=RelationType.REQUIRES)
    assert rel.task_id == "study_ch2"
    assert rel.type == RelationType.REQUIRES
    assert rel.description is None


def test_task_relation_with_description():
    rel = TaskRelation(task_id="study_ch2", type=RelationType.NEEDS, description="Prereq")
    assert rel.description == "Prereq"


def test_task_relation_is_frozen():
    rel = TaskRelation(task_id="x", type=RelationType.CONNECTED)
    with pytest.raises((AttributeError, TypeError)):
        rel.task_id = "y"  # type: ignore[misc]


def test_task_relation_all_types():
    for rt in RelationType:
        rel = TaskRelation(task_id="t", type=rt)
        assert rel.type == rt
