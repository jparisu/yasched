"""Time span with human-readable parsing."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

# Units must appear in descending order: w d h m
_PATTERN = re.compile(r"^(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?$")


@dataclass(frozen=True)
class Duration:
    """Time span wrapping datetime.timedelta."""

    value: datetime.timedelta

    @staticmethod
    def from_string(s: str) -> Duration:
        if not s:
            raise ValueError("Duration string must not be empty")
        m = _PATTERN.fullmatch(s)
        if m is None or not any(m.groups()):
            raise ValueError(f"Cannot parse duration: {s!r}")
        weeks = int(m.group(1) or 0)
        days = int(m.group(2) or 0)
        hours = int(m.group(3) or 0)
        minutes = int(m.group(4) or 0)
        return Duration(value=datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes))

    @staticmethod
    def zero() -> Duration:
        return Duration(value=datetime.timedelta())

    def to_minutes(self) -> int:
        return int(self.value.total_seconds()) // 60

    def to_hours(self) -> float:
        return self.value.total_seconds() / 3600

    def to_days(self) -> float:
        return self.value.total_seconds() / 86400

    def __str__(self) -> str:
        total_minutes = int(self.value.total_seconds()) // 60
        weeks, rem = divmod(total_minutes, 7 * 24 * 60)
        days, rem = divmod(rem, 24 * 60)
        hours, minutes = divmod(rem, 60)
        parts = []
        if weeks:
            parts.append(f"{weeks}w")
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        return "".join(parts) or "0m"

    def __add__(self, other: Duration) -> Duration:
        return Duration(value=self.value + other.value)

    def __sub__(self, other: Duration) -> Duration:
        result = self.value - other.value
        if result.total_seconds() < 0:
            raise ValueError("Duration subtraction would produce a negative result")
        return Duration(value=result)

    def __mul__(self, factor: int) -> Duration:
        return Duration(value=self.value * factor)

    def __lt__(self, other: Duration) -> bool:
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)
