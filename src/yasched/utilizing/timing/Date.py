"""Calendar date with multi-format parsing."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from yasched.utilizing.timing.Duration import Duration

_FORMATS = [
    "%Y-%m-%d",  # ISO 8601 — canonical
    "%d/%m/%Y",  # DD/MM/YYYY  (tried before MM/DD for ambiguous inputs)
    "%m/%d/%Y",  # MM/DD/YYYY
    "%B %d, %Y",  # January 15, 2026
    "%b %d %Y",  # Jan 15 2026
]


@dataclass(frozen=True)
class Date:
    """Calendar date wrapping datetime.date."""

    value: datetime.date

    @staticmethod
    def from_string(s: str) -> Date:
        s = s.strip()
        if s.lower() == "today":
            return Date.today()
        if s.lower() == "tomorrow":
            return Date.tomorrow()
        for fmt in _FORMATS:
            try:
                return Date(value=datetime.datetime.strptime(s, fmt).date())
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {s!r}")

    @staticmethod
    def today() -> Date:
        return Date(value=datetime.date.today())

    @staticmethod
    def tomorrow() -> Date:
        return Date(value=datetime.date.today() + datetime.timedelta(days=1))

    def to_iso(self) -> str:
        return self.value.strftime("%Y-%m-%d")

    def to_long(self) -> str:
        return f"{self.value.strftime('%B')} {self.value.day}, {self.value.year}"

    def year(self) -> int:
        return self.value.year

    def month(self) -> int:
        return self.value.month

    def day(self) -> int:
        return self.value.day

    def __str__(self) -> str:
        return self.to_iso()

    def __lt__(self, other: Date) -> bool:
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __add__(self, duration: Duration) -> Date:
        return Date(value=self.value + datetime.timedelta(days=duration.value.days))

    def __sub__(self, other: Date) -> Duration:
        delta = self.value - other.value
        return Duration(value=abs(delta))
