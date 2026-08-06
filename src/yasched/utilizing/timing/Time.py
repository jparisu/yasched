"""Time of day with multi-format parsing."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from yasched.utilizing.timing.Duration import Duration

# 24-hour formats tried first, then 12-hour (uppercased string).
_FORMATS_24H = ["%H:%M:%S", "%H:%M"]
_FORMATS_12H = ["%I:%M:%S %p", "%I:%M %p", "%I %p", "%I:%M:%S%p", "%I:%M%p", "%I%p"]


@dataclass(frozen=True)
class Time:
    """Time of day wrapping datetime.time."""

    value: datetime.time

    @staticmethod
    def from_string(s: str) -> Time:
        s = s.strip()
        for fmt in _FORMATS_24H:
            try:
                return Time(value=datetime.datetime.strptime(s, fmt).time())
            except ValueError:
                continue
        upper = s.upper()
        for fmt in _FORMATS_12H:
            try:
                return Time(value=datetime.datetime.strptime(upper, fmt).time())
            except ValueError:
                continue
        raise ValueError(f"Cannot parse time: {s!r}")

    @staticmethod
    def now() -> Time:
        return Time(value=datetime.datetime.now().time().replace(microsecond=0))

    def to_hhmm(self) -> str:
        return self.value.strftime("%H:%M")

    def to_hhmmss(self) -> str:
        return self.value.strftime("%H:%M:%S")

    def hour(self) -> int:
        return self.value.hour

    def minute(self) -> int:
        return self.value.minute

    def second(self) -> int:
        return self.value.second

    def __str__(self) -> str:
        return self.to_hhmm()

    def __lt__(self, other: Time) -> bool:
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __add__(self, duration: Duration) -> Time:
        dt = datetime.datetime.combine(datetime.date.min, self.value) + duration.value
        return Time(value=dt.time())

    def __sub__(self, other: Time) -> Duration:
        base = datetime.date.min
        delta = abs(
            datetime.datetime.combine(base, self.value)
            - datetime.datetime.combine(base, other.value)
        )
        return Duration(value=delta)
