"""
A Pythonic utility for working with time slots (start and end times).
"""

from __future__ import annotations

from yasched.timing.Time import Time


class TimeSlot:
    """Represents a time slot with a start and end time.

    The class supports:
      * Clean construction from start and end times
      * Alternate constructor from start time and duration
      * Duration calculation
      * String conversion with customizable format
      * Comparisons based on start time

    Memory footprint is minimized via `__slots__`.

    Example:
        >>> start = Time(2025, 10, 24, 14, 0, 0)
        >>> end = Time(2025, 10, 24, 16, 0, 0)
        >>> slot = TimeSlot(start, end)
        >>> str(slot)
        '2025-10-24 14:00:00 - 2025-10-24 16:00:00'
    """

    __slots__ = ("start", "end")

    def __init__(self, start: Time, end: Time) -> None:
        """Initialize a `TimeSlot` from start and end times.

        Args:
            start: The start time of the slot.
            end: The end time of the slot.

        Example:
            >>> start = Time(2025, 10, 24, 14, 0, 0)
            >>> end = Time(2025, 10, 24, 16, 0, 0)
            >>> TimeSlot(start, end)
            TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))
        """
        self.start = start
        self.end = end

    # ---------- Alternate constructors ----------

    @classmethod
    def from_duration(cls, start: Time, duration: Time) -> TimeSlot:
        """Construct a `TimeSlot` from a start time and duration as a Time object.

        Args:
            start: The start time of the slot.
            duration: Duration as a Time object.

        Returns:
            A `TimeSlot` with the calculated end time.

        Example:
            >>> start = Time(2025, 10, 24, 14, 0, 0)
            >>> duration = Time(0, 0, 0, 2, 0, 0)  # 2 hours
            >>> slot = TimeSlot.from_duration(start, duration)
            >>> str(slot.end)
            '2025-10-24 16:00:00'
        """
        end = start + duration
        return cls(start, end)

    # ---------- Methods ----------

    def duration(self) -> int:
        """Calculate the duration of the time slot in seconds.

        Returns:
            Duration in seconds.

        Example:
            >>> start = Time(2025, 10, 24, 14, 0, 0)
            >>> end = Time(2025, 10, 24, 16, 0, 0)
            >>> TimeSlot(start, end).duration()
            7200
        """
        delta = self.end.to_datetime() - self.start.to_datetime()
        return int(delta.total_seconds())

    # ---------- Representation ----------

    def __str__(self) -> str:
        """Return the string representation of the time slot.

        Example:
            >>> start = Time(2025, 10, 24, 14, 0, 0)
            >>> end = Time(2025, 10, 24, 16, 0, 0)
            >>> str(TimeSlot(start, end))
            '2025-10-24 14:00:00 - 2025-10-24 16:00:00'
        """
        return f"{self.start} - {self.end}"

    def __repr__(self) -> str:
        """Return an unambiguous constructor-style representation.

        Example:
            >>> start = Time(2025, 10, 24, 14, 0, 0)
            >>> end = Time(2025, 10, 24, 16, 0, 0)
            >>> repr(TimeSlot(start, end))
            'TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))'
        """
        return f"TimeSlot({repr(self.start)}, {repr(self.end)})"

    def to_string(self, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format the time slot as a string using the specified format.

        Args:
            fmt: A `datetime.strftime`-compatible format string.
                 Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            The formatted string representation of the time slot.

        Examples:
            >>> start = Time(2025, 10, 24, 14, 0, 0)
            >>> end = Time(2025, 10, 24, 16, 0, 0)
            >>> TimeSlot(start, end).to_string()
            '2025-10-24 14:00:00 - 2025-10-24 16:00:00'
            >>> TimeSlot(start, end).to_string("%H:%M")
            '14:00 - 16:00'
        """
        return f"{self.start.to_string(fmt)} - {self.end.to_string(fmt)}"

    # ---------- Comparison operators ----------

    def __eq__(self, other: object) -> bool:
        """Return `True` if two `TimeSlot` instances are equal.

        Non-`TimeSlot` objects compare as `False`.

        Example:
            >>> start = Time(2025, 10, 24, 14, 0, 0)
            >>> end = Time(2025, 10, 24, 16, 0, 0)
            >>> TimeSlot(start, end) == TimeSlot(start, end)
            True
        """
        return isinstance(other, TimeSlot) and self.start == other.start and self.end == other.end

    def __lt__(self, other: TimeSlot) -> bool:
        """Return `True` if `self` starts before `other`.

        Args:
            other: Another `TimeSlot` to compare to.

        Returns:
            Whether `self` starts earlier than `other`.

        Raises:
            TypeError: If other is not a TimeSlot.

        Example:
            >>> start1 = Time(2025, 10, 24, 14, 0, 0)
            >>> end1 = Time(2025, 10, 24, 16, 0, 0)
            >>> start2 = Time(2025, 10, 24, 15, 0, 0)
            >>> end2 = Time(2025, 10, 24, 17, 0, 0)
            >>> TimeSlot(start1, end1) < TimeSlot(start2, end2)
            True
        """
        if not isinstance(other, TimeSlot):
            raise TypeError(f"'<' not supported between instances of 'TimeSlot' and '{type(other).__name__}'")
        return self.start < other.start

    def __le__(self, other: TimeSlot) -> bool:
        """Return `True` if `self` starts before or at the same time as `other`.
        
        Raises:
            TypeError: If other is not a TimeSlot.
        """
        if not isinstance(other, TimeSlot):
            raise TypeError(f"'<=' not supported between instances of 'TimeSlot' and '{type(other).__name__}'")
        return self.start <= other.start

    def __gt__(self, other: TimeSlot) -> bool:
        """Return `True` if `self` starts after `other`.
        
        Raises:
            TypeError: If other is not a TimeSlot.
        """
        if not isinstance(other, TimeSlot):
            raise TypeError(f"'>' not supported between instances of 'TimeSlot' and '{type(other).__name__}'")
        return self.start > other.start

    def __ge__(self, other: TimeSlot) -> bool:
        """Return `True` if `self` starts after or at the same time as `other`.
        
        Raises:
            TypeError: If other is not a TimeSlot.
        """
        if not isinstance(other, TimeSlot):
            raise TypeError(f"'>=' not supported between instances of 'TimeSlot' and '{type(other).__name__}'")
        return self.start >= other.start
