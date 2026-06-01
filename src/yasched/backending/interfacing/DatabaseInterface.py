"""High-level query API over a ResolvedDatabase."""

from __future__ import annotations

import datetime
from collections import deque
from dataclasses import dataclass, field

from yasched.backending.Database import (
    ResolvedDatabase,
    ResolvedEvent,
    ResolvedTask,
    ResolvedTopic,
)
from yasched.coring._shared import TaskStatus, Weekday
from yasched.coring.Layout import Layout
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.MultiDaySchedule import MultiDaySchedule
from yasched.coring.Schedule import Schedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring.YearlySchedule import YearlySchedule

_WEEKDAY_MAP: dict[int, Weekday] = {
    0: Weekday.MONDAY,
    1: Weekday.TUESDAY,
    2: Weekday.WEDNESDAY,
    3: Weekday.THURSDAY,
    4: Weekday.FRIDAY,
    5: Weekday.SATURDAY,
    6: Weekday.SUNDAY,
}

_DONE_STATUSES = {TaskStatus.DONE, TaskStatus.CANCELLED}


@dataclass(frozen=True)
class EventConflict:
    """A pair of events whose schedules overlap and trigger a blocking_level warning."""

    blocker: ResolvedEvent
    blocked: ResolvedEvent
    date: datetime.date


@dataclass(frozen=True)
class DailyView:
    """All scheduled items and conflicts for a single calendar day."""

    date: datetime.date
    events: list[ResolvedEvent] = field(default_factory=list)
    tasks: list[ResolvedTask] = field(default_factory=list)
    conflicts: list[EventConflict] = field(default_factory=list)


@dataclass(frozen=True)
class WeeklyView:
    """Seven DailyViews for a calendar week (Monday–Sunday)."""

    week_start: datetime.date
    days: list[DailyView] = field(default_factory=list)


class DatabaseInterface:
    """Read-only query API over a ResolvedDatabase."""

    def __init__(self, db: ResolvedDatabase) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Primitive
    # ------------------------------------------------------------------

    def get_layout(self, layout_id: str) -> Layout:
        if layout_id not in self._db.layouts:
            raise KeyError(layout_id)
        return self._db.layouts[layout_id]

    def get_topic(self, topic_id: str) -> ResolvedTopic:
        if topic_id not in self._db.topics:
            raise KeyError(topic_id)
        return self._db.topics[topic_id]

    def get_event(self, event_id: str) -> ResolvedEvent:
        if event_id not in self._db.events:
            raise KeyError(event_id)
        return self._db.events[event_id]

    def get_task(self, task_id: str) -> ResolvedTask:
        if task_id not in self._db.tasks:
            raise KeyError(task_id)
        return self._db.tasks[task_id]

    def all_layouts(self) -> list[Layout]:
        return list(self._db.layouts.values())

    def all_topics(self) -> list[ResolvedTopic]:
        return list(self._db.topics.values())

    def all_events(self) -> list[ResolvedEvent]:
        return list(self._db.events.values())

    def all_tasks(self) -> list[ResolvedTask]:
        return list(self._db.tasks.values())

    # ------------------------------------------------------------------
    # Schedule
    # ------------------------------------------------------------------

    def get_events_in_range(self, start: datetime.date, end: datetime.date) -> list[ResolvedEvent]:
        return [e for e in self._db.events.values() if _any_occurrence(e.raw.schedules, start, end)]

    def get_tasks_in_range(self, start: datetime.date, end: datetime.date) -> list[ResolvedTask]:
        return [
            t
            for t in self._db.tasks.values()
            if t.raw.schedules and _any_occurrence(t.raw.schedules, start, end)
        ]

    def get_daily_schedule(self, date: datetime.date) -> DailyView:
        events = self.get_events_in_range(date, date)
        tasks = self.get_tasks_in_range(date, date)
        conflicts = self.get_conflicts(start=date, end=date)
        return DailyView(date=date, events=events, tasks=tasks, conflicts=conflicts)

    def get_weekly_schedule(self, week_start: datetime.date) -> WeeklyView:
        days = [self.get_daily_schedule(week_start + datetime.timedelta(days=i)) for i in range(7)]
        return WeeklyView(week_start=week_start, days=days)

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    def get_tasks_by_status(self, status: TaskStatus) -> list[ResolvedTask]:
        return [t for t in self._db.tasks.values() if t.status == status]

    def get_tasks_by_topic(
        self, topic_id: str, include_subtopics: bool = False
    ) -> list[ResolvedTask]:
        if include_subtopics:
            sub_ids = {topic_id} | {t.id for t in self.get_topic_subtree(topic_id)}
            return [t for t in self._db.tasks.values() if any(tp.id in sub_ids for tp in t.topics)]
        return [t for t in self._db.tasks.values() if any(tp.id == topic_id for tp in t.topics)]

    def get_tasks_with_tag(self, tag: str) -> list[ResolvedTask]:
        return [t for t in self._db.tasks.values() if tag in t.effective_tags]

    def get_tasks_by_priority(
        self,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> list[ResolvedTask]:
        result = []
        for t in self._db.tasks.values():
            p = t.priority
            if p is None:
                continue
            if min_priority is not None and p < min_priority:
                continue
            if max_priority is not None and p > max_priority:
                continue
            result.append(t)
        return result

    def get_upcoming_deadlines(
        self,
        days_ahead: int,
        include_today: bool = True,
        reference_date: datetime.date | None = None,
    ) -> list[ResolvedTask]:
        today = reference_date or datetime.date.today()
        cutoff = today + datetime.timedelta(days=days_ahead)
        result = []
        for t in self._db.tasks.values():
            d = t.effective_deadline
            if d is None:
                continue
            if t.status in _DONE_STATUSES:
                continue
            if include_today and today <= d <= cutoff:
                result.append(t)
            elif not include_today and today < d <= cutoff:
                result.append(t)
        result.sort(key=lambda t: t.effective_deadline)  # type: ignore[arg-type, return-value]
        return result

    def get_overdue_tasks(self, reference_date: datetime.date | None = None) -> list[ResolvedTask]:
        today = reference_date or datetime.date.today()
        return [
            t
            for t in self._db.tasks.values()
            if t.effective_deadline is not None
            and t.effective_deadline < today
            and t.status not in _DONE_STATUSES
        ]

    def get_blocked_tasks(self) -> list[ResolvedTask]:
        return [t for t in self._db.tasks.values() if t.status == TaskStatus.BLOCKED]

    def get_blocking_tasks(self, task_id: str) -> list[ResolvedTask]:
        task = self.get_task(task_id)
        return list(task.blocking_tasks)

    def get_task_children(self, task_id: str) -> list[ResolvedTask]:
        task = self.get_task(task_id)
        return list(task.children)

    def get_task_subtree(self, task_id: str) -> list[ResolvedTask]:
        root = self.get_task(task_id)
        result: list[ResolvedTask] = []
        queue: deque[ResolvedTask] = deque(root.children)
        while queue:
            node = queue.popleft()
            result.append(node)
            queue.extend(node.children)
        return result

    def get_task_events(self, task_id: str) -> list[ResolvedEvent]:
        task = self.get_task(task_id)
        return list(task.linked_events)

    def search_tasks(self, query: str) -> list[ResolvedTask]:
        q = query.lower()
        return [
            t
            for t in self._db.tasks.values()
            if q in t.name.lower() or (t.description and q in t.description.lower())
        ]

    # ------------------------------------------------------------------
    # Topics
    # ------------------------------------------------------------------

    def get_root_topics(self) -> list[ResolvedTopic]:
        return list(self._db.root_topics)

    def get_topic_children(self, topic_id: str) -> list[ResolvedTopic]:
        topic = self.get_topic(topic_id)
        return list(topic.children)

    def get_topic_subtree(self, topic_id: str) -> list[ResolvedTopic]:
        root = self.get_topic(topic_id)
        result: list[ResolvedTopic] = []
        queue: deque[ResolvedTopic] = deque(root.children)
        while queue:
            node = queue.popleft()
            result.append(node)
            queue.extend(node.children)
        return result

    def get_topic_ancestors(self, topic_id: str) -> list[ResolvedTopic]:
        topic = self.get_topic(topic_id)
        result: list[ResolvedTopic] = []
        visited: set[str] = set()
        queue: deque[ResolvedTopic] = deque(topic.parents)
        while queue:
            node = queue.popleft()
            if node.id in visited:
                continue
            visited.add(node.id)
            result.append(node)
            queue.extend(node.parents)
        return result

    def get_topics_with_tag(self, tag: str) -> list[ResolvedTopic]:
        return [t for t in self._db.topics.values() if tag in t.effective_tags]

    def search_topics(self, query: str) -> list[ResolvedTopic]:
        q = query.lower()
        return [
            t
            for t in self._db.topics.values()
            if q in t.name.lower() or (t.description and q in t.description.lower())
        ]

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------

    def get_conflicts(
        self,
        start: datetime.date | None = None,
        end: datetime.date | None = None,
    ) -> list[EventConflict]:
        if start is None:
            start = datetime.date.today()
        if end is None:
            end = datetime.date.max

        events_in_range = self.get_events_in_range(start, end)
        conflicts: list[EventConflict] = []
        for ev_a in events_in_range:
            if ev_a.blocking_level is None:
                continue
            for ev_b in events_in_range:
                if ev_a is ev_b:
                    continue
                b_level = ev_b.blocking_level if ev_b.blocking_level is not None else 0
                if b_level <= ev_a.blocking_level:
                    # Find the overlap date
                    overlap_dates = _overlap_dates(
                        ev_a.raw.schedules, ev_b.raw.schedules, start, end
                    )
                    for d in overlap_dates:
                        conflicts.append(EventConflict(blocker=ev_a, blocked=ev_b, date=d))
        return conflicts

    def get_stale_event_links(self) -> list[ResolvedTask]:
        today = datetime.date.today()
        stale = []
        for task in self._db.tasks.values():
            for ev in task.linked_events:
                if _all_schedules_ended(ev.raw.schedules, today):
                    stale.append(task)
                    break
        return stale

    def get_stale_blocks(self) -> list[ResolvedTask]:
        return [
            t
            for t in self._db.tasks.values()
            if t.blocking_tasks and all(b.status in _DONE_STATUSES for b in t.blocking_tasks)
        ]

    def task_status_summary(self) -> dict[TaskStatus, int]:
        summary: dict[TaskStatus, int] = {s: 0 for s in TaskStatus}
        for t in self._db.tasks.values():
            summary[t.status] += 1
        return summary

    def task_count_by_topic(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for t in self._db.tasks.values():
            for topic in t.topics:
                counts[topic.id] = counts.get(topic.id, 0) + 1
        return counts


# ------------------------------------------------------------------
# Schedule occurrence helpers
# ------------------------------------------------------------------


def _any_occurrence(schedules: list[Schedule], start: datetime.date, end: datetime.date) -> bool:
    return any(_schedule_in_range(s, start, end) for s in schedules)


def _schedule_in_range(schedule: Schedule, start: datetime.date, end: datetime.date) -> bool:
    if isinstance(schedule, SingleDaySchedule):
        return start <= schedule.day <= end

    if isinstance(schedule, MultiDaySchedule):
        return schedule.start_day <= end and schedule.end_day >= start

    if isinstance(schedule, WeeklySchedule):
        sched_start = schedule.start_date or datetime.date.min
        sched_end = schedule.end_date or datetime.date.max
        overlap_start = max(start, sched_start)
        overlap_end = min(end, sched_end)
        if overlap_start > overlap_end:
            return False
        target_days = {a.week_day for a in schedule.appointments}
        if (overlap_end - overlap_start).days >= 6:
            return True
        current = overlap_start
        while current <= overlap_end:
            if _WEEKDAY_MAP[current.weekday()] in target_days:
                return True
            current += datetime.timedelta(days=1)
        return False

    if isinstance(schedule, MonthlySchedule):
        sched_start = schedule.start_date or datetime.date.min
        sched_end = schedule.end_date or datetime.date.max
        year, month = start.year, start.month
        while True:
            try:
                occurrence = datetime.date(year, month, schedule.day_of_month)
                if occurrence > end:
                    break
                if start <= occurrence <= end and sched_start <= occurrence <= sched_end:
                    return True
            except ValueError:
                pass
            month += 1
            if month > 12:
                month = 1
                year += 1
            if year > end.year + 1:
                break
        return False

    if isinstance(schedule, YearlySchedule):
        for year in range(start.year, end.year + 1):
            try:
                occurrence = datetime.date(year, schedule.month, schedule.day)
                if start <= occurrence <= end:
                    return True
            except ValueError:
                pass
        return False

    return False


def _overlap_dates(
    schedules_a: list[Schedule],
    schedules_b: list[Schedule],
    start: datetime.date,
    end: datetime.date,
) -> list[datetime.date]:
    """Return dates in [start, end] where both A and B have occurrences."""
    result = []
    current = start
    while current <= end:
        if _any_occurrence(schedules_a, current, current) and _any_occurrence(
            schedules_b, current, current
        ):
            result.append(current)
        current += datetime.timedelta(days=1)
    return result


def _all_schedules_ended(schedules: list[Schedule], today: datetime.date) -> bool:
    for sched in schedules:
        if isinstance(sched, WeeklySchedule):
            if sched.end_date is None or sched.end_date >= today:
                return False
        elif isinstance(sched, MonthlySchedule):
            if sched.end_date is None or sched.end_date >= today:
                return False
        elif isinstance(sched, SingleDaySchedule):
            if sched.day >= today:
                return False
        elif isinstance(sched, MultiDaySchedule):
            if sched.end_day >= today:
                return False
        else:
            return False  # YearlySchedule never ends
    return True
