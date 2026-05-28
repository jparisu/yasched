"""Tests for coring.MultiDaySchedule."""

import datetime

import pytest

from yasched.coring.MultiDaySchedule import MultiDaySchedule

# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_multi_day_normal_range():
    m = MultiDaySchedule(
        start_day=datetime.date(2026, 8, 10),
        end_day=datetime.date(2026, 8, 14),
    )
    assert m.start_day == datetime.date(2026, 8, 10)
    assert m.end_day == datetime.date(2026, 8, 14)


def test_multi_day_single_day_span():
    m = MultiDaySchedule(
        start_day=datetime.date(2026, 6, 1),
        end_day=datetime.date(2026, 6, 1),
    )
    assert m.start_day == m.end_day


def test_multi_day_is_frozen():
    m = MultiDaySchedule(
        start_day=datetime.date(2026, 1, 1),
        end_day=datetime.date(2026, 1, 5),
    )
    with pytest.raises((AttributeError, TypeError)):
        m.start_day = datetime.date(2026, 1, 2)  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_multi_day_cross_month():
    m = MultiDaySchedule(
        start_day=datetime.date(2026, 1, 30),
        end_day=datetime.date(2026, 2, 2),
    )
    assert m.end_day > m.start_day


def test_multi_day_cross_year():
    m = MultiDaySchedule(
        start_day=datetime.date(2025, 12, 29),
        end_day=datetime.date(2026, 1, 3),
    )
    assert m.end_day.year > m.start_day.year


def test_multi_day_adjacent_days():
    m = MultiDaySchedule(
        start_day=datetime.date(2026, 6, 1),
        end_day=datetime.date(2026, 6, 2),
    )
    delta = m.end_day - m.start_day
    assert delta.days == 1


# ---------------------------------------------------------------------------
# Construction — failure cases
# ---------------------------------------------------------------------------


def test_multi_day_end_before_start_raises():
    with pytest.raises(ValueError):
        MultiDaySchedule(
            start_day=datetime.date(2026, 8, 14),
            end_day=datetime.date(2026, 8, 10),
        )


def test_multi_day_end_one_day_before_start_raises():
    with pytest.raises(ValueError):
        MultiDaySchedule(
            start_day=datetime.date(2026, 6, 5),
            end_day=datetime.date(2026, 6, 4),
        )
