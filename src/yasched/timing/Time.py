"""
A Pythonic utility for working with date and time (with time-of-day).
Provides construction, string conversion, arithmetic, and rich comparisons.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from yasched.timing.Day import Day


class Time:
    """Represents a specific date and time (with time-of-day component).

    Internally wraps a `datetime.datetime` to maintain both date and time precision.

    The class supports:
      * Clean construction from year/month/day/hour/minute/second
      * Alternate constructors from strings and `datetime.datetime`
      * Easy access to day, hour, minute, second components
      * String conversion with customizable format
      * Adding times (immutably, returns a new `Time`)
      * Comparisons (`==`, `<`, `<=`, `>`, `>=`) based on chronological order

    Memory footprint is minimized via `__slots__`, and instances behave
    immutably in practice (no public setters; methods return new instances).

    Example:
        >>> t = Time(2025, 10, 24, 14, 30, 0)
        >>> str(t)
        '2025-10-24 14:30:00'
        >>> t2 = t + 3600  # Add 3600 seconds (1 hour)
        >>> str(t2)
        '2025-10-24 15:30:00'
    """

    __slots__ = ("_datetime",)

    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> None:
        """Initialize a `Time` from its components.

        Args:
            year: Four-digit year (e.g., 2025).
            month: Month number in [1, 12].
            day: Day-of-month in [1, 31] depending on the month/year.
            hour: Hour in [0, 23]. Defaults to 0.
            minute: Minute in [0, 59]. Defaults to 0.
            second: Second in [0, 59]. Defaults to 0.

        Raises:
            ValueError: If the provided components do not form a valid datetime.

        Example:
            >>> Time(2025, 1, 31, 14, 30, 0)
            Time(2025, 1, 31, 14, 30, 0)
        """
        self._datetime = datetime(year, month, day, hour, minute, second)

    # ---------- Alternate constructors ----------

    @classmethod
    def now(cls) -> Time:
        """Construct a `Time` representing the current local datetime.

        Returns:
            A `Time` for now (according to the system's local datetime).

        Example:
            >>> isinstance(Time.now(), Time)
            True
        """
        dt = datetime.now()
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    @classmethod
    def from_string(cls, time_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Time:
        """Construct a `Time` by parsing a string.

        Args:
            time_str: The string to parse (e.g., "2025-10-24 14:30:00").
            fmt: A `datetime.strptime`-compatible format string.
                 Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            A `Time` corresponding to the parsed datetime.

        Raises:
            ValueError: If parsing fails or produces an invalid datetime.

        Examples:
            >>> Time.from_string("2025-10-24 14:30:00")
            Time(2025, 10, 24, 14, 30, 0)
            >>> Time.from_string("24/10/2025 14:30", fmt="%d/%m/%Y %H:%M")
            Time(2025, 10, 24, 14, 30, 0)
        """
        dt = datetime.strptime(time_str, fmt)
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    @classmethod
    def from_datetime(cls, dt: datetime) -> Time:
        """Construct a `Time` from a `datetime.datetime`.

        Args:
            dt: A `datetime.datetime` instance.

        Returns:
            A `Time` with the same datetime values.

        Example:
            >>> Time.from_datetime(datetime(2025, 10, 24, 14, 30, 0))
            Time(2025, 10, 24, 14, 30, 0)
        """
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    # ---------- Representation ----------

    def __str__(self) -> str:
        """Return the string representation in format YYYY-MM-DD HH:MM:SS.

        Example:
            >>> str(Time(2025, 10, 24, 14, 30, 0))
            '2025-10-24 14:30:00'
        """
        return self._datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self) -> str:
        """Return an unambiguous constructor-style representation.

        Example:
            >>> repr(Time(2025, 10, 24, 14, 30, 0))
            'Time(2025, 10, 24, 14, 30, 0)'
        """
        return f"Time({self.day.year}, {self.day.month}, {self.day.day}, {self.hour}, {self.minute}, {self.second})"

    def to_string(self, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format the time as a string using the specified format.

        Args:
            fmt: A `datetime.strftime`-compatible format string.
                 Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            The formatted string representation of the time.

        Examples:
            >>> Time(2025, 10, 24, 14, 30, 0).to_string()
            '2025-10-24 14:30:00'
            >>> Time(2025, 10, 24, 14, 30, 0).to_string("%d/%m/%Y %H:%M")
            '24/10/2025 14:30'
        """
        return self._datetime.strftime(fmt)

    # ---------- Accessors ----------

    @property
    def day(self) -> Day:
        """The Day component.

        Example:
            >>> Time(2025, 10, 24, 14, 30, 0).day
            Day(2025, 10, 24)
        """
        return Day(self._datetime.year, self._datetime.month, self._datetime.day)

    @property
    def hour(self) -> int:
        """The hour component in [0, 23].

        Example:
            >>> Time(2025, 10, 24, 14, 30, 0).hour
            14
        """
        return self._datetime.hour

    @property
    def minute(self) -> int:
        """The minute component in [0, 59].

        Example:
            >>> Time(2025, 10, 24, 14, 30, 0).minute
            30
        """
        return self._datetime.minute

    @property
    def second(self) -> int:
        """The second component in [0, 59].

        Example:
            >>> Time(2025, 10, 24, 14, 30, 0).second
            0
        """
        return self._datetime.second

    # ---------- Arithmetic ----------

    def __add__(self, other: int | Time) -> Time:
        """Add seconds to this Time, or add two Times.

        Args:
            other: Either an integer (number of seconds) or another Time.
                   If Time, adds the total seconds from both.

        Returns:
            A new Time representing the sum.

        Example:
            >>> Time(2025, 10, 24, 14, 30, 0) + 3600
            Time(2025, 10, 24, 15, 30, 0)
        """
        if isinstance(other, int):
            new_dt = self._datetime + timedelta(seconds=other)
            return Time.from_datetime(new_dt)
        elif isinstance(other, Time):
            # Add the total seconds from both times
            total_seconds = int(self._datetime.timestamp()) + int(other._datetime.timestamp())
            new_dt = datetime.fromtimestamp(total_seconds)
            return Time.from_datetime(new_dt)
        return NotImplemented

    # ---------- Comparison operators ----------

    def __eq__(self, other: object) -> bool:
        """Return `True` if two `Time` instances represent the same datetime.

        Non-`Time` objects compare as `False`.

        Example:
            >>> Time(2025, 10, 24, 14, 30, 0) == Time(2025, 10, 24, 14, 30, 0)
            True
        """
        return isinstance(other, Time) and self._datetime == other._datetime

    def __lt__(self, other: Time) -> bool:
        """Return `True` if `self` occurs before `other` in chronological order.

        Args:
            other: Another `Time` to compare to.

        Returns:
            Whether `self` is earlier than `other`.

        Example:
            >>> Time(2025, 10, 24, 14, 30, 0) < Time(2025, 10, 24, 15, 30, 0)
            True
        """
        if not isinstance(other, Time):
            return NotImplemented
        return self._datetime < other._datetime

    def __le__(self, other: Time) -> bool:
        """Return `True` if `self` is earlier than or equal to `other`."""
        if not isinstance(other, Time):
            return NotImplemented
        return self._datetime <= other._datetime

    def __gt__(self, other: Time) -> bool:
        """Return `True` if `self` occurs after `other`."""
        if not isinstance(other, Time):
            return NotImplemented
        return self._datetime > other._datetime

    def __ge__(self, other: Time) -> bool:
        """Return `True` if `self` is later than or equal to `other`."""
        if not isinstance(other, Time):
            return NotImplemented
        return self._datetime >= other._datetime

    # ---------- Interop ----------

    def to_datetime(self) -> datetime:
        """Return the underlying `datetime.datetime`.

        Useful when interoperating with standard library or third-party code
        that expects a `datetime.datetime`.

        Returns:
            The wrapped `datetime.datetime`.

        Example:
            >>> isinstance(Time(2025, 10, 24, 14, 30, 0).to_datetime(), datetime)
            True
        """
        return self._datetime
