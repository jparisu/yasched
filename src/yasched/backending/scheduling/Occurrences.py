"""Expand ``Schedule``s into concrete dated occurrences within a window.

Sub-event overrides: an event with a ``parent_id`` overrides its parent's
occurrence on each date the sub-event lands on. If the sub-event's effective
``status`` is ``"cancelled"`` it removes that date entirely (and contributes
nothing itself).
"""

from __future__ import annotations

import calendar
import datetime
from collections.abc import Iterator
from dataclasses import dataclass

from yasched.backending.resolving.Resolver import Resolved
from yasched.coring.Schedule import (
    MonthlySchedule,
    MultiDaySchedule,
    Schedule,
    SingleDaySchedule,
    WeeklySchedule,
    YearlySchedule,
)
from yasched.utilizing.timing.Date import Date
from yasched.utilizing.timing.Time import Time


@dataclass(frozen=True)
class Occurrence:
    """A single concrete instance of an event on a given date."""

    event_id: str
    date: Date
    start_time: Time | None = None
    end_time: Time | None = None
    is_override: bool = False


def _times(sch: Schedule) -> tuple[Time | None, Time | None]:
    start = sch.start_time
    end = sch.end_time
    if end is None and start is not None and sch.duration is not None:
        end = start + sch.duration
    return start, end


def _daterange(start: datetime.date, end: datetime.date) -> Iterator[datetime.date]:
    day = start
    while day <= end:
        yield day
        day += datetime.timedelta(days=1)


def expand(sch: Schedule, start: datetime.date, end: datetime.date) -> list[datetime.date]:
    """Return every date in ``[start, end]`` on which *sch* fires.

    A schedule's optional ``start_date`` / ``end_date`` bounds (inclusive) further
    clamp the window, so a recurring schedule only fires within its own range.
    """
    if sch.start_date is not None:
        start = max(start, sch.start_date.value)
    if sch.end_date is not None:
        end = min(end, sch.end_date.value)
    if start > end:
        return []

    if isinstance(sch, WeeklySchedule):
        wanted = {d.index() for d in sch.week_days}
        return [d for d in _daterange(start, end) if d.weekday() in wanted]

    if isinstance(sch, MonthlySchedule):
        out: list[datetime.date] = []
        for d in _daterange(start, end):
            last = calendar.monthrange(d.year, d.month)[1]
            if d.day == min(sch.day, last):
                out.append(d)
        return out

    if isinstance(sch, YearlySchedule):
        out = []
        for year in range(start.year, end.year + 1):
            last = calendar.monthrange(year, sch.month)[1]
            try:
                d = datetime.date(year, sch.month, min(sch.day, last))
            except ValueError:
                continue
            if start <= d <= end:
                out.append(d)
        return out

    if isinstance(sch, SingleDaySchedule):
        if sch.day is not None and start <= sch.day.value <= end:
            return [sch.day.value]
        return []

    if isinstance(sch, MultiDaySchedule):
        if sch.start_day is None or sch.end_day is None:
            return []
        lo = max(sch.start_day.value, start)
        hi = min(sch.end_day.value, end)
        return list(_daterange(lo, hi)) if lo <= hi else []

    return []


def _event_dates(
    resolved: Resolved, start: datetime.date, end: datetime.date
) -> list[datetime.date]:
    dates: set[datetime.date] = set()
    for sch in resolved.source.schedules:  # type: ignore[union-attr]
        dates.update(expand(sch, start, end))
    return sorted(dates)


def _occurrences_for(
    resolved: Resolved, start: datetime.date, end: datetime.date, is_override: bool
) -> list[Occurrence]:
    out: list[Occurrence] = []
    for sch in resolved.source.schedules:  # type: ignore[union-attr]
        st, et = _times(sch)
        for d in expand(sch, start, end):
            out.append(
                Occurrence(
                    event_id=resolved.id,
                    date=Date(value=d),
                    start_time=st,
                    end_time=et,
                    is_override=is_override,
                )
            )
    return out


def build_event_occurrences(
    resolved_events: dict[str, Resolved],
    start: datetime.date,
    end: datetime.date,
) -> list[Occurrence]:
    """Occurrences for every event, applying sub-event overrides/cancellations."""
    parents = {eid: r for eid, r in resolved_events.items() if r.source.parent_id is None}  # type: ignore[union-attr]
    children = {eid: r for eid, r in resolved_events.items() if r.source.parent_id is not None}  # type: ignore[union-attr]

    # Dates each parent has overridden, and the surviving child occurrences.
    overridden: dict[str, set[datetime.date]] = {}
    child_occurrences: list[Occurrence] = []
    for child in children.values():
        parent_id = child.source.parent_id  # type: ignore[union-attr]
        if parent_id is None:  # already filtered, but narrows the type for mypy
            continue
        dates = _event_dates(child, start, end)
        overridden.setdefault(parent_id, set()).update(dates)
        if str(child.attributes.get("status", "")).lower() != "cancelled":
            child_occurrences.extend(_occurrences_for(child, start, end, is_override=True))

    occurrences: list[Occurrence] = []
    for parent_id, parent in parents.items():
        skip = overridden.get(parent_id, set())
        for occ in _occurrences_for(parent, start, end, is_override=False):
            if occ.date.value not in skip:
                occurrences.append(occ)
    occurrences.extend(child_occurrences)

    occurrences.sort(
        key=lambda o: (o.date.value, o.start_time.value if o.start_time else datetime.time.min)
    )
    return occurrences
