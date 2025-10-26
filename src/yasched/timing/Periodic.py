"""
A Pythonic utility for working with periodic/recurring time slots.
"""

from __future__ import annotations

from yasched.timing.Day import Day
from yasched.timing.Time import Time
from yasched.timing.TimeSlot import TimeSlot


class Periodic:
    """Represents a periodic/recurring time slot.

    A Periodic defines a time slot that repeats at specified intervals from
    a start date to an end date. The repetitions are defined as Time offsets
    that determine when the event recurs.

    Attributes:
        start: The first TimeSlot when this periodic event occurs.
        end: The final TimeSlot after which no more repetitions occur.
        repetitions: List of Time offsets defining when the event repeats.

    Example:
        >>> start_slot = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        >>> end_slot = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
        >>> # Repeat every 2 days
        >>> repetitions = [Time(1970, 1, 3, 0, 0, 0)]  # 2 days from epoch
        >>> periodic = Periodic(start_slot, end_slot, repetitions)
    """

    __slots__ = ("start", "end", "repetitions")

    def __init__(self, start: TimeSlot, end: TimeSlot, repetitions: list[Time]) -> None:
        """Initialize a Periodic from start/end slots and repetition pattern.

        Args:
            start: The initial TimeSlot.
            end: The final TimeSlot (inclusive boundary).
            repetitions: List of Time objects representing repetition intervals.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
            >>> reps = [Time(1970, 1, 3, 0, 0, 0)]  # Every 2 days
            >>> Periodic(start, end, reps)
            Periodic(...)
        """
        self.start = start
        self.end = end
        self.repetitions = repetitions

    # ---------- Alternate constructors ----------

    @classmethod
    def from_daily(cls, start: TimeSlot, end: TimeSlot, interval_days: int = 1) -> Periodic:
        """Create a Periodic that repeats daily at a given interval.

        Args:
            start: The initial TimeSlot.
            end: The final TimeSlot.
            interval_days: Number of days between repetitions (default 1 for daily).

        Returns:
            A Periodic with daily repetitions.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
            >>> periodic = Periodic.from_daily(start, end, interval_days=2)
        """
        repetition = Time(1970, 1, 1 + interval_days, 0, 0, 0)
        return cls(start, end, [repetition])

    @classmethod
    def from_weekly(cls, start: TimeSlot, end: TimeSlot, interval_weeks: int = 1) -> Periodic:
        """Create a Periodic that repeats weekly at a given interval.

        Args:
            start: The initial TimeSlot.
            end: The final TimeSlot.
            interval_weeks: Number of weeks between repetitions (default 1 for weekly).

        Returns:
            A Periodic with weekly repetitions.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 12, 31, 9, 0, 0), Time(2025, 12, 31, 10, 0, 0))
            >>> periodic = Periodic.from_weekly(start, end)
        """
        days = interval_weeks * 7
        repetition = Time(1970, 1, 1 + days, 0, 0, 0)
        return cls(start, end, [repetition])

    @classmethod
    def from_count(cls, start: TimeSlot, repetition_interval: Time, count: int) -> Periodic:
        """Create a Periodic with a specific number of occurrences.

        Args:
            start: The initial TimeSlot.
            repetition_interval: Time offset between repetitions.
            count: Total number of occurrences (including the first one).

        Returns:
            A Periodic with the specified number of occurrences.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> interval = Time(1970, 1, 3, 0, 0, 0)  # Every 2 days
            >>> periodic = Periodic.from_count(start, interval, 10)  # 10 occurrences
        """
        # Calculate the end date based on count
        last_occurrence_start = start.start
        for _ in range(count - 1):
            last_occurrence_start = last_occurrence_start + repetition_interval

        duration_seconds = start.duration()
        last_occurrence_end = last_occurrence_start + duration_seconds

        end = TimeSlot(last_occurrence_start, last_occurrence_end)
        return cls(start, end, [repetition_interval])

    # ---------- Methods ----------

    def get_occurrences(self) -> list[TimeSlot]:
        """Generate all occurrences of this periodic event.

        Returns:
            List of TimeSlot instances for each occurrence.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 1, 5, 9, 0, 0), Time(2025, 1, 5, 10, 0, 0))
            >>> reps = [Time(1970, 1, 2, 0, 0, 0)]  # Daily
            >>> periodic = Periodic(start, end, reps)
            >>> occurrences = periodic.get_occurrences()
            >>> len(occurrences)
            5
        """
        occurrences = []
        current_start = self.start.start
        current_end = self.start.end

        # Add the first occurrence
        occurrences.append(TimeSlot(current_start, current_end))

        # Generate subsequent occurrences
        while True:
            # Apply all repetition offsets
            for rep in self.repetitions:
                current_start = current_start + rep
                current_end = current_end + rep

                # Check if we've exceeded the end boundary
                if current_start > self.end.start:
                    return occurrences

                occurrences.append(TimeSlot(current_start, current_end))

    def count_occurrences(self) -> int:
        """Count the total number of occurrences.

        Returns:
            The number of times this periodic event occurs.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 1, 5, 9, 0, 0), Time(2025, 1, 5, 10, 0, 0))
            >>> reps = [Time(1970, 1, 2, 0, 0, 0)]  # Daily
            >>> periodic = Periodic(start, end, reps)
            >>> periodic.count_occurrences()
            5
        """
        return len(self.get_occurrences())

    # ---------- Representation ----------

    def __str__(self) -> str:
        """Return the string representation of the periodic event.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
            >>> reps = [Time(1970, 1, 2, 0, 0, 0)]
            >>> str(Periodic(start, end, reps))
            'Periodic(start=2025-01-01 09:00:00 - 2025-01-01 10:00:00, end=2025-01-31 09:00:00 - 2025-01-31 10:00:00, repetitions=1)'
        """
        return f"Periodic(start={self.start}, end={self.end}, repetitions={len(self.repetitions)})"

    def __repr__(self) -> str:
        """Return an unambiguous constructor-style representation.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
            >>> reps = [Time(1970, 1, 2, 0, 0, 0)]
            >>> repr(Periodic(start, end, reps))
            'Periodic(...)'
        """
        return f"Periodic(start={repr(self.start)}, end={repr(self.end)}, repetitions={repr(self.repetitions)})"

    # ---------- Comparison operators ----------

    def __eq__(self, other: object) -> bool:
        """Return `True` if two `Periodic` instances are equal.

        Non-`Periodic` objects compare as `False`.

        Example:
            >>> start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
            >>> end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
            >>> reps = [Time(1970, 1, 2, 0, 0, 0)]
            >>> p1 = Periodic(start, end, reps)
            >>> p2 = Periodic(start, end, reps)
            >>> p1 == p2
            True
        """
        return (
            isinstance(other, Periodic)
            and self.start == other.start
            and self.end == other.end
            and len(self.repetitions) == len(other.repetitions)
            and all(r1 == r2 for r1, r2 in zip(self.repetitions, other.repetitions))
        )
