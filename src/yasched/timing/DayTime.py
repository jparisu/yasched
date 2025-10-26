"""
A Pythonic utility for working with time-of-day (hours, minutes, seconds).
Represents a time within a single day without date components.
"""

from __future__ import annotations

from datetime import time


class DayTime:
    """Represents a time within a single day (hours, minutes, seconds).

    This class represents only the time-of-day component, without any date.
    It's useful for representing times like "14:30:00" without a specific date.

    The class supports:
      * Clean construction from hour/minute/second
      * Alternate constructors from strings and `datetime.time`
      * Easy access to hour, minute, second components
      * String conversion with customizable format
      * Comparisons (`==`, `<`, `<=`, `>`, `>=`) based on time order

    Memory footprint is minimized via `__slots__`, and instances behave
    immutably in practice (no public setters; methods return new instances).

    Example:
        >>> dt = DayTime(14, 30, 0)
        >>> str(dt)
        '14:30:00'
        >>> dt < DayTime(15, 0, 0)
        True
    """

    __slots__ = ("_time",)

    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0) -> None:
        """Initialize a `DayTime` from its components.

        Args:
            hour: Hour in [0, 23]. Defaults to 0.
            minute: Minute in [0, 59]. Defaults to 0.
            second: Second in [0, 59]. Defaults to 0.

        Raises:
            ValueError: If the provided components do not form a valid time.

        Example:
            >>> DayTime(14, 30, 0)
            DayTime(14, 30, 0)
        """
        self._time = time(hour, minute, second)

    # ---------- Alternate constructors ----------

    @classmethod
    def from_string(cls, time_str: str, fmt: str = "%H:%M:%S") -> DayTime:
        """Construct a `DayTime` by parsing a string.

        Args:
            time_str: The string to parse (e.g., "14:30:00").
            fmt: A `datetime.strptime`-compatible format string.
                 Defaults to "%H:%M:%S".

        Returns:
            A `DayTime` corresponding to the parsed time.

        Raises:
            ValueError: If parsing fails or produces an invalid time.

        Examples:
            >>> DayTime.from_string("14:30:00")
            DayTime(14, 30, 0)
            >>> DayTime.from_string("2:30 PM", fmt="%I:%M %p")
            DayTime(14, 30, 0)
        """
        from datetime import datetime

        dt = datetime.strptime(time_str, fmt)
        return cls(dt.hour, dt.minute, dt.second)

    @classmethod
    def from_time(cls, t: time) -> DayTime:
        """Construct a `DayTime` from a `datetime.time`.

        Args:
            t: A `datetime.time` instance.

        Returns:
            A `DayTime` with the same time values.

        Example:
            >>> from datetime import time
            >>> DayTime.from_time(time(14, 30, 0))
            DayTime(14, 30, 0)
        """
        return cls(t.hour, t.minute, t.second)

    # ---------- Representation ----------

    def __str__(self) -> str:
        """Return the string representation in format HH:MM:SS.

        Example:
            >>> str(DayTime(14, 30, 0))
            '14:30:00'
        """
        return self._time.isoformat()

    def __repr__(self) -> str:
        """Return an unambiguous constructor-style representation.

        Example:
            >>> repr(DayTime(14, 30, 0))
            'DayTime(14, 30, 0)'
        """
        return f"DayTime({self.hour}, {self.minute}, {self.second})"

    def to_string(self, fmt: str = "%H:%M:%S") -> str:
        """Format the time as a string using the specified format.

        Args:
            fmt: A `datetime.strftime`-compatible format string.
                 Defaults to "%H:%M:%S".

        Returns:
            The formatted string representation of the time.

        Examples:
            >>> DayTime(14, 30, 0).to_string()
            '14:30:00'
            >>> DayTime(14, 30, 0).to_string("%I:%M %p")
            '02:30 PM'
        """
        return self._time.strftime(fmt)

    # ---------- Accessors ----------

    @property
    def hour(self) -> int:
        """The hour component in [0, 23].

        Example:
            >>> DayTime(14, 30, 0).hour
            14
        """
        return self._time.hour

    @property
    def minute(self) -> int:
        """The minute component in [0, 59].

        Example:
            >>> DayTime(14, 30, 0).minute
            30
        """
        return self._time.minute

    @property
    def second(self) -> int:
        """The second component in [0, 59].

        Example:
            >>> DayTime(14, 30, 0).second
            0
        """
        return self._time.second

    # ---------- Comparison operators ----------

    def __eq__(self, other: object) -> bool:
        """Return `True` if two `DayTime` instances represent the same time.

        Non-`DayTime` objects compare as `False`.

        Example:
            >>> DayTime(14, 30, 0) == DayTime(14, 30, 0)
            True
        """
        return isinstance(other, DayTime) and self._time == other._time

    def __lt__(self, other: DayTime) -> bool:
        """Return `True` if `self` occurs before `other`.

        Args:
            other: Another `DayTime` to compare to.

        Returns:
            Whether `self` is earlier than `other`.

        Raises:
            TypeError: If other is not a DayTime.

        Example:
            >>> DayTime(14, 30, 0) < DayTime(15, 0, 0)
            True
        """
        if not isinstance(other, DayTime):
            raise TypeError(f"'<' not supported between instances of 'DayTime' and '{type(other).__name__}'")
        return self._time < other._time

    def __le__(self, other: DayTime) -> bool:
        """Return `True` if `self` is earlier than or equal to `other`.

        Raises:
            TypeError: If other is not a DayTime.
        """
        if not isinstance(other, DayTime):
            raise TypeError(f"'<=' not supported between instances of 'DayTime' and '{type(other).__name__}'")
        return self._time <= other._time

    def __gt__(self, other: DayTime) -> bool:
        """Return `True` if `self` occurs after `other`.

        Raises:
            TypeError: If other is not a DayTime.
        """
        if not isinstance(other, DayTime):
            raise TypeError(f"'>' not supported between instances of 'DayTime' and '{type(other).__name__}'")
        return self._time > other._time

    def __ge__(self, other: DayTime) -> bool:
        """Return `True` if `self` is later than or equal to `other`.

        Raises:
            TypeError: If other is not a DayTime.
        """
        if not isinstance(other, DayTime):
            raise TypeError(f"'>=' not supported between instances of 'DayTime' and '{type(other).__name__}'")
        return self._time >= other._time

    # ---------- Interop ----------

    def to_time(self) -> time:
        """Return the underlying `datetime.time`.

        Useful when interoperating with standard library or third-party code
        that expects a `datetime.time`.

        Returns:
            The wrapped `datetime.time`.

        Example:
            >>> isinstance(DayTime(14, 30, 0).to_time(), time)
            True
        """
        return self._time

    def to_seconds(self) -> int:
        """Convert the time to total seconds since midnight.

        Returns:
            Total seconds as an integer.

        Example:
            >>> DayTime(1, 0, 0).to_seconds()
            3600
            >>> DayTime(0, 1, 30).to_seconds()
            90
        """
        return self.hour * 3600 + self.minute * 60 + self.second
