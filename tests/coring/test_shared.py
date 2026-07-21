"""Tests for coring._shared support types."""

import pytest

from yasched.coring._shared import EventLink, RelationType, TaskRelation, Weekday


@pytest.mark.parametrize(
    "text,expected",
    [
        ("monday", Weekday.MONDAY),
        ("Monday", Weekday.MONDAY),
        ("MON", Weekday.MONDAY),
        ("tues", Weekday.TUESDAY),
        ("  fri  ", Weekday.FRIDAY),
        ("sun", Weekday.SUNDAY),
    ],
)
def test_weekday_from_string(text, expected):
    assert Weekday.from_string(text) is expected


def test_weekday_index_matches_datetime():
    assert Weekday.MONDAY.index() == 0
    assert Weekday.SUNDAY.index() == 6


def test_weekday_invalid_raises():
    with pytest.raises(ValueError):
        Weekday.from_string("noneday")


def test_relation_type_from_string():
    assert RelationType.from_string("requires") is RelationType.REQUIRES
    assert RelationType.from_string("SIMILAR") is RelationType.SIMILAR


def test_task_relation_defaults():
    rel = TaskRelation(task_id="a")
    assert rel.type is RelationType.CONNECTED
    assert rel.description is None


def test_event_link_defaults():
    link = EventLink(event_id="e")
    assert link.use_as_deadline is False
    assert link.as_context is False
