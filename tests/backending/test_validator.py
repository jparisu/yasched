"""Tests for the v4 validator."""

from yasched.backending.loading.ElementLoader import ElementLoader
from yasched.backending.validating.Validator import Severity, validate_database


def _codes(doc):
    db = ElementLoader.from_dict(doc)
    return {i.code for i in validate_database(db)}


def test_unknown_parent_and_self_parent():
    codes = _codes(
        {
            "elements": [
                {"id": "AllTopic", "type": "topic"},
                {"id": "a", "type": "task", "directParents": ["ghost"]},
                {"id": "b", "type": "task", "directParents": ["b"]},
            ]
        }
    )
    assert "unknown-parent" in codes
    assert "self-parent" in codes


def test_parent_cycle():
    codes = _codes(
        {
            "elements": [
                {"id": "AllTopic", "type": "topic"},
                {"id": "b", "type": "task", "directParents": ["c"]},
                {"id": "c", "type": "task", "directParents": ["b"]},
            ]
        }
    )
    assert "parent-cycle" in codes


def test_unknown_connection_and_out_of_range():
    codes = _codes(
        {
            "elements": [
                {"id": "AllTopic", "type": "topic"},
                {
                    "id": "t",
                    "type": "task",
                    "attributes": {
                        "priority": 99,
                        "connections": [{"to": "nope", "relation": "x"}],
                    },
                },
            ]
        }
    )
    assert "unknown-connection" in codes
    assert "out-of-range" in codes


def test_detached_occurrence():
    codes = _codes(
        {
            "elements": [
                {"id": "AllTopic", "type": "topic"},
                {"id": "x#deadline", "type": "event"},
            ]
        }
    )
    assert "detached-occurrence" in codes


def test_clean_document_has_no_errors():
    db = ElementLoader.from_dict(
        {
            "elements": [
                {"id": "AllTopic", "type": "topic"},
                {
                    "id": "t",
                    "type": "task",
                    "directParents": ["AllTopic"],
                    "attributes": {"priority": 3},
                },
            ]
        }
    )
    issues = validate_database(db)
    assert not [i for i in issues if i.severity is Severity.ERROR]


def test_topic_defaults_not_flagged_as_wrong_type():
    # A topic holding a task-only attribute (priority) as a default must NOT warn.
    codes = _codes(
        {
            "elements": [
                {"id": "AllTopic", "type": "topic", "attributes": {"priority": 3}},
            ]
        }
    )
    assert "wrong-type-attribute" not in codes
