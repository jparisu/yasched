"""Tests for the ConsistencyError hierarchy."""

import pytest

from yasched.backending.managing.ConsistencyError import (
    ConsistencyError,
    CycleError,
    DuplicateIdError,
    LogicError,
    TimeConstraintError,
    UnknownReferenceError,
)


def test_consistency_error_is_value_error():
    err = ConsistencyError(entity="topic", entity_id="t1", field="id", message="bad")
    assert isinstance(err, ValueError)


def test_consistency_error_str():
    err = ConsistencyError(entity="task", entity_id="t1", field="deadline", message="past due")
    s = str(err)
    assert "task" in s
    assert "t1" in s
    assert "deadline" in s


def test_duplicate_id_error_is_consistency_error():
    err = DuplicateIdError(entity="topic", entity_id="t1", field="id", message="dup")
    assert isinstance(err, ConsistencyError)


def test_unknown_reference_error_is_consistency_error():
    err = UnknownReferenceError(entity="event", entity_id="e1", field="topic_id", message="missing")
    assert isinstance(err, ConsistencyError)


def test_cycle_error_is_consistency_error():
    err = CycleError(entity="topic", entity_id="t1", field="parent_ids", message="cycle")
    assert isinstance(err, ConsistencyError)


def test_time_constraint_error_is_consistency_error():
    err = TimeConstraintError(entity="schedule", entity_id="e1", field="end_date", message="bad")
    assert isinstance(err, ConsistencyError)


def test_logic_error_is_consistency_error():
    err = LogicError(entity="task", entity_id="t1", field="schedules", message="bad combo")
    assert isinstance(err, ConsistencyError)


def test_all_subclasses_can_be_raised_and_caught():
    for cls in (
        DuplicateIdError,
        UnknownReferenceError,
        CycleError,
        TimeConstraintError,
        LogicError,
    ):
        with pytest.raises(ConsistencyError):
            raise cls(entity="x", entity_id="y", field="z", message="m")
