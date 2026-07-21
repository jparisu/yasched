"""Tests for schedule occurrence expansion and sub-event overrides."""

import datetime

from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.resolving.Resolver import Resolver
from yasched.backending.scheduling.Occurrences import build_event_occurrences, expand
from yasched.coring._shared import Weekday
from yasched.coring.Schedule import (
    MonthlySchedule,
    MultiDaySchedule,
    SingleDaySchedule,
    WeeklySchedule,
    YearlySchedule,
)
from yasched.utilizing.timing.Date import Date

SEP_START = datetime.date(2026, 9, 1)
SEP_END = datetime.date(2026, 9, 30)


def test_weekly_expansion():
    sch = WeeklySchedule(week_days=(Weekday.MONDAY,))
    dates = expand(sch, SEP_START, SEP_END)
    assert all(d.weekday() == 0 for d in dates)
    assert datetime.date(2026, 9, 7) in dates


def test_monthly_expansion_clamps_to_month_end():
    sch = MonthlySchedule(day=31)
    # September has 30 days -> the 30th fires
    dates = expand(sch, SEP_START, SEP_END)
    assert dates == [datetime.date(2026, 9, 30)]


def test_yearly_expansion():
    sch = YearlySchedule(month=9, day=15)
    dates = expand(sch, datetime.date(2025, 1, 1), datetime.date(2027, 12, 31))
    assert dates == [
        datetime.date(2025, 9, 15),
        datetime.date(2026, 9, 15),
        datetime.date(2027, 9, 15),
    ]


def test_single_day_in_and_out_of_window():
    sch = SingleDaySchedule(day=Date.from_string("2026-09-16"))
    assert expand(sch, SEP_START, SEP_END) == [datetime.date(2026, 9, 16)]
    assert expand(sch, datetime.date(2026, 10, 1), SEP_END + datetime.timedelta(days=60)) == []


def test_multi_day_expands_each_day():
    sch = MultiDaySchedule(
        start_day=Date.from_string("2026-09-10"), end_day=Date.from_string("2026-09-13")
    )
    dates = expand(sch, SEP_START, SEP_END)
    assert dates == [datetime.date(2026, 9, d) for d in (10, 11, 12, 13)]


def test_subevent_override_replaces_parent_occurrence(teacher_db):
    r = Resolver(teacher_db)
    occ = build_event_occurrences(r.resolve_all_events(), SEP_START, SEP_END)
    on_16 = [o for o in occ if o.date.value == datetime.date(2026, 9, 16)]
    ids = {o.event_id for o in on_16}
    # the moved sub-event replaces the parent lecture on that date
    assert "math101-lecture-move" in ids
    assert "math101-lecture" not in ids


def test_cancelled_subevent_removes_occurrence(teacher_db):
    r = Resolver(teacher_db)
    occ = build_event_occurrences(r.resolve_all_events(), SEP_START, SEP_END)
    on_23 = [o for o in occ if o.date.value == datetime.date(2026, 9, 23)]
    lecture_ids = {o.event_id for o in on_23 if o.event_id.startswith("math101-lecture")}
    assert lecture_ids == set()  # nothing on the cancelled day


def test_end_time_derived_from_duration(teacher_db):
    r = Resolver(teacher_db)
    occ = build_event_occurrences(r.resolve_all_events(), SEP_START, SEP_END)
    lecture = next(o for o in occ if o.event_id == "math101-lecture")
    assert lecture.start_time.to_hhmm() == "10:00"
    assert lecture.end_time.to_hhmm() == "11:00"  # 10:00 + 1h


def test_end_time_explicit():
    db = DatabaseLoader.loads(
        "events:\n"
        "  - id: oh\n    name: OH\n    schedules:\n"
        "      - type: weekly\n        week_days: [friday]\n"
        "        start_time: '15:00'\n        end_time: '17:00'\n"
    )
    r = Resolver(db)
    occ = build_event_occurrences(r.resolve_all_events(), SEP_START, SEP_END)
    assert occ and occ[0].end_time.to_hhmm() == "17:00"
