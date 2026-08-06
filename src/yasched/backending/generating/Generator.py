"""Generate virtual auto-elements within a date window.

Three generators, all producing ``virtual=True`` elements that pin their
generator as ``MainParent`` (``direct_parents=[generator_id]``) and carry a
deterministic id so a later edit can attach to the right occurrence:

======================  ===========================  ==================
Generator               Produces                     id
======================  ===========================  ==================
schedule                events or tasks              ``{sched}#{date}``
task ``deadline``        one ``deadline`` event       ``{task}#deadline``
``reminders``            one ``reminder`` event each   ``{host}#reminder-{offset}``
======================  ===========================  ==================

Suppression: a virtual element whose id already exists as a real element is
dropped (the real one — typically a promoted edit — wins).

Cascade bound: schedule-generated **tasks** may also spawn their deadline and
reminder events, but ``deadline`` / ``reminder`` events never generate further
(depth ≤ 2: ``schedule → task → {deadline, reminder}``).
"""

from __future__ import annotations

import calendar
import datetime
from typing import Any

from yasched.backending.Database import Database
from yasched.backending.resolving.Resolver import ResolvedElement, Resolver
from yasched.coring.AttributeDefinition import NON_INHERITING
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType
from yasched.utilizing.timing.Duration import Duration

_WEEKDAYS = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "tues": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thurs": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}


def _to_date(value: Any) -> datetime.date | None:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    text = str(value).split("T")[0]
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        return None


def _to_datetime(value: Any) -> datetime.datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    text = str(value)
    try:
        if "T" in text:
            return datetime.datetime.fromisoformat(text)
        return datetime.datetime.combine(datetime.date.fromisoformat(text), datetime.time())
    except ValueError:
        return None


def _weekday(value: Any) -> int | None:
    return _WEEKDAYS.get(str(value).strip().lower())


class Generator:
    """Expands schedules/deadlines/reminders into virtual elements."""

    def __init__(self, db: Database, resolver: Resolver | None = None) -> None:
        self._db = db
        self._resolver = resolver or Resolver(db)

    def generate(self, start: datetime.date, end: datetime.date) -> list[Element]:
        """Return every virtual element occurring in ``[start, end]`` (inclusive)."""
        produced: list[Element] = []
        seen: set[str] = set(self._db.elements)  # real ids suppress virtuals

        def emit(element: Element) -> bool:
            if element.id in seen:
                return False
            seen.add(element.id)
            produced.append(element)
            return True

        # Pass 1 — schedule occurrences (events / tasks).
        schedule_children: list[tuple[Element, dict[str, Any]]] = []
        for schedule in self._db.schedules:
            resolved = self._resolver.resolve(schedule)
            for element, effective in self._schedule_occurrences(schedule, resolved, start, end):
                if emit(element):
                    schedule_children.append((element, effective))

        # Pass 2 — deadline + reminder events for every task/event (real + generated).
        bases: list[tuple[Element, dict[str, Any]]] = [
            (e, self._resolver.resolve(e).attributes) for e in (*self._db.tasks, *self._db.events)
        ]
        bases.extend(schedule_children)
        for element, attributes in bases:
            if attributes.get("class") in ("deadline", "reminder"):
                continue  # auto events never cascade further
            for extra in self._deadline_events(element, attributes, start, end):
                emit(extra)
            for extra in self._reminder_events(element, attributes, start, end):
                emit(extra)

        return produced

    # ------------------------------------------------------------------
    # Schedules
    # ------------------------------------------------------------------

    def _schedule_occurrences(
        self,
        schedule: Element,
        resolved: ResolvedElement,
        window_start: datetime.date,
        window_end: datetime.date,
    ) -> list[tuple[Element, dict[str, Any]]]:
        attrs = resolved.attributes
        generates = (
            ElementType.EVENT
            if str(attrs.get("generates", "event")) == "event"
            else ElementType.TASK
        )
        kind = str(attrs.get("kind", "")).strip().lower()

        lo = max(window_start, _to_date(attrs.get("startDate")) or window_start)
        hi = min(window_end, _to_date(attrs.get("endDate")) or window_end)
        time_text = str(attrs["time"]) if attrs.get("time") else None
        duration = attrs.get("duration")

        out: list[tuple[Element, dict[str, Any]]] = []
        for day in self._matching_days(kind, attrs, lo, hi):
            iso = day.isoformat()
            own: dict[str, Any] = {}
            if generates is ElementType.EVENT:
                own["start"] = f"{iso}T{time_text}" if time_text else iso
                if duration:
                    own["duration"] = str(duration)
                own["class"] = "normal"
            else:
                own["deadline"] = iso
            element = Element(
                id=f"{schedule.id}#{iso}",
                type=generates,
                direct_parents=[schedule.id],
                attributes=own,
                virtual=True,
            )
            out.append((element, self._effective(element, resolved)))
        return out

    def _matching_days(
        self, kind: str, attrs: dict[str, Any], lo: datetime.date, hi: datetime.date
    ) -> list[datetime.date]:
        if hi < lo:
            return []
        week_days = {d for v in attrs.get("weekDays") or [] if (d := _weekday(v)) is not None}
        month_days = {int(v) for v in attrs.get("monthDays") or []}
        yearly = {(int(y["month"]), int(y["day"])) for y in attrs.get("yearlyDays") or []}

        days: list[datetime.date] = []
        current = lo
        one_day = datetime.timedelta(days=1)
        while current <= hi:
            if self._day_matches(kind, current, week_days, month_days, yearly):
                days.append(current)
            current += one_day
        return days

    @staticmethod
    def _day_matches(
        kind: str,
        day: datetime.date,
        week_days: set[int],
        month_days: set[int],
        yearly: set[tuple[int, int]],
    ) -> bool:
        if kind == "daily":
            return True
        if kind == "weekly":
            return day.weekday() in week_days
        if kind == "monthly":
            last = calendar.monthrange(day.year, day.month)[1]
            if day.day in month_days:
                return True
            return day.day == last and any(md > last for md in month_days)  # clamp to month end
        if kind == "yearly":
            return (day.month, day.day) in yearly
        return False

    # ------------------------------------------------------------------
    # Deadlines & reminders
    # ------------------------------------------------------------------

    def _deadline_events(
        self, element: Element, attrs: dict[str, Any], start: datetime.date, end: datetime.date
    ) -> list[Element]:
        if element.type is not ElementType.TASK:
            return []
        day = _to_date(attrs.get("deadline"))
        if day is None or not (start <= day <= end):
            return []
        return [
            Element(
                id=f"{element.id}#deadline",
                type=ElementType.EVENT,
                direct_parents=[element.id],
                attributes={"class": "deadline", "start": day.isoformat()},
                virtual=True,
            )
        ]

    def _reminder_events(
        self, element: Element, attrs: dict[str, Any], start: datetime.date, end: datetime.date
    ) -> list[Element]:
        reminders = attrs.get("reminders") or []
        if not reminders:
            return []
        base = (
            _to_datetime(attrs.get("start"))
            if element.type is ElementType.EVENT
            else _to_datetime(attrs.get("deadline"))
        )
        if base is None:
            return []

        out: list[Element] = []
        for offset in reminders:
            delta = _parse_offset(str(offset))
            if delta is None:
                continue
            moment = base - delta
            if not (start <= moment.date() <= end):
                continue
            out.append(
                Element(
                    id=f"{element.id}#reminder-{offset}",
                    type=ElementType.EVENT,
                    direct_parents=[element.id],
                    attributes={"class": "reminder", "start": moment.isoformat(timespec="minutes")},
                    virtual=True,
                )
            )
        return out

    # ------------------------------------------------------------------
    # Effective attributes of a virtual element (own over generator, scoped)
    # ------------------------------------------------------------------

    def _effective(self, element: Element, generator: ResolvedElement) -> dict[str, Any]:
        attrs = dict(element.attributes)
        for key, value in generator.attributes.items():
            if key in attrs or key in NON_INHERITING:
                continue
            definition = self._db.attribute_defs.get(key)
            if definition is not None and (
                not definition.inherits or not definition.applies_to_type(element.type)
            ):
                continue
            attrs[key] = value
        return attrs


def _parse_offset(text: str) -> datetime.timedelta | None:
    """Reminder offset: how long *before* the base moment (leading '-' optional)."""
    cleaned = text.strip().lstrip("-").strip()
    try:
        return Duration.from_string(cleaned).value
    except ValueError:
        return None
