"""
A Pythonic utility for working with date and time (with time-of-day).
Provides construction, string conversion, arithmetic, and rich comparisons.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from yasched.timing.Day import Day
from yasched.timing.DayTime import DayTime


class Moment:
    """Represents a specific date and time (with time-of-day component).

    Internally wraps a `datetime.datetime` to maintain both date and time precision.

    The class supports:
      * Clean construction from year/month/day/hour/minute/second
      * Alternate constructors from strings and `datetime.datetime`
      * Easy access to day, hour, minute, second components
      * String conversion with customizable format
      * Adding times (immutably, returns a new `Moment`)
      * Comparisons (`==`, `<`, `<=`, `>`, `>=`) based on chronological order

    Memory footprint is minimized via `__slots__`, and instances behave
    immutably in practice (no public setters; methods return new instances).

    Example:
        >>> t = Moment(2025, 10, 24, 14, 30, 0)
        >>> str(t)
        '2025-10-24 14:30:00'
        >>> t2 = t + 3600  # Add 3600 seconds (1 hour)
        >>> str(t2)
        '2025-10-24 15:30:00'
    """

    __slots__ = ("_datetime",)

    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> None:
        """Initialize a `Moment` from its components.

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
            >>> Moment(2025, 1, 31, 14, 30, 0)
            Moment(2025, 1, 31, 14, 30, 0)
        """
        self._datetime = datetime(year, month, day, hour, minute, second)

    # ---------- Alternate constructors ----------

    @classmethod
    def now(cls) -> Moment:
        """Construct a `Moment` representing the current local datetime.

        Returns:
            A `Moment` for now (according to the system's local datetime).

        Example:
            >>> isinstance(Moment.now(), Moment)
            True
        """
        dt = datetime.now()
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    @classmethod
    def from_string(cls, time_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Moment:
        """Construct a `Moment` by parsing a string.

        Args:
            time_str: The string to parse (e.g., "2025-10-24 14:30:00").
            fmt: A `datetime.strptime`-compatible format string.
                 Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            A `Moment` corresponding to the parsed datetime.

        Raises:
            ValueError: If parsing fails or produces an invalid datetime.

        Examples:
            >>> Moment.from_string("2025-10-24 14:30:00")
            Moment(2025, 10, 24, 14, 30, 0)
            >>> Moment.from_string("24/10/2025 14:30", fmt="%d/%m/%Y %H:%M")
            Moment(2025, 10, 24, 14, 30, 0)
        """
        dt = datetime.strptime(time_str, fmt)
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    @classmethod
    def from_datetime(cls, dt: datetime) -> Moment:
        """Construct a `Moment` from a `datetime.datetime`.

        Args:
            dt: A `datetime.datetime` instance.

        Returns:
            A `Moment` with the same datetime values.

        Example:
            >>> Moment.from_datetime(datetime(2025, 10, 24, 14, 30, 0))
            Moment(2025, 10, 24, 14, 30, 0)
        """
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    @classmethod
    def from_day_and_daytime(cls, day: Day, daytime: DayTime) -> Moment:
        """Construct a `Moment` from a Day and DayTime.

        Args:
            day: A Day instance.
            daytime: A DayTime instance.

        Returns:
            A `Moment` combining the date from Day and time from DayTime.

        Example:
            >>> from yasched.timing.DayTime import DayTime
            >>> Moment.from_day_and_daytime(Day(2025, 10, 24), DayTime(14, 30, 0))
            Moment(2025, 10, 24, 14, 30, 0)
        """
        return cls(day.year, day.month, day.day, daytime.hour, daytime.minute, daytime.second)

    # ---------- Representation ----------

    def __str__(self) -> str:
        """Return the string representation in format YYYY-MM-DD HH:MM:SS.

        Example:
            >>> str(Moment(2025, 10, 24, 14, 30, 0))
            '2025-10-24 14:30:00'
        """
        return self._datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self) -> str:
        """Return an unambiguous constructor-style representation.

        Example:
            >>> repr(Moment(2025, 10, 24, 14, 30, 0))
            'Moment(2025, 10, 24, 14, 30, 0)'
        """
        return f"Moment({self.day.year}, {self.day.month}, {self.day.day}, {self.hour}, {self.minute}, {self.second})"

    def to_string(self, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format the time as a string using the specified format.

        Args:
            fmt: A `datetime.strftime`-compatible format string.
                 Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            The formatted string representation of the time.

        Examples:
            >>> Moment(2025, 10, 24, 14, 30, 0).to_string()
            '2025-10-24 14:30:00'
            >>> Moment(2025, 10, 24, 14, 30, 0).to_string("%d/%m/%Y %H:%M")
            '24/10/2025 14:30'
        """
        return self._datetime.strftime(fmt)

    # ---------- Accessors ----------

    @property
    def day(self) -> Day:
        """The Day component.

        Example:
            >>> Moment(2025, 10, 24, 14, 30, 0).day
            Day(2025, 10, 24)
        """
        return Day(self._datetime.year, self._datetime.month, self._datetime.day)

    @property
    def daytime(self) -> DayTime:
        """The DayTime component.

        Example:
            >>> from yasched.timing.DayTime import DayTime
            >>> Moment(2025, 10, 24, 14, 30, 0).daytime
            DayTime(14, 30, 0)
        """
        from yasched.timing.DayTime import DayTime

        return DayTime(self._datetime.hour, self._datetime.minute, self._datetime.second)

    @property
    def hour(self) -> int:
        """The hour component in [0, 23].

        Example:
            >>> Moment(2025, 10, 24, 14, 30, 0).hour
            14
        """
        return self._datetime.hour

    @property
    def minute(self) -> int:
        """The minute component in [0, 59].

        Example:
            >>> Moment(2025, 10, 24, 14, 30, 0).minute
            30
        """
        return self._datetime.minute

    @property
    def second(self) -> int:
        """The second component in [0, 59].

        Example:
            >>> Moment(2025, 10, 24, 14, 30, 0).second
            0
        """
        return self._datetime.second

    # ---------- Arithmetic ----------

    def __add__(self, other: int | Moment) -> Moment:
        """Add seconds or another Moment to this Moment.

        Args:
            other: Either an integer (number of seconds) or another Moment.
                   If Moment, treats the other Moment's components as a duration to add
                   (years as days*365, months as days*30, days, hours, minutes, seconds).

        Returns:
            A new Moment representing the sum.

        Examples:
            >>> Moment(2025, 10, 24, 14, 30, 0) + 3600
            Moment(2025, 10, 24, 15, 30, 0)
            >>> Moment(2025, 1, 1, 10, 30, 45) + Moment(1970, 1, 2, 5, 15, 30)
            Moment(2025, 1, 3, 15, 46, 15)
        """
        if isinstance(other, int):
            new_dt = self._datetime + timedelta(seconds=other)
            return Moment.from_datetime(new_dt)
        elif isinstance(other, Moment):
            # Convert the other Moment to a duration in seconds
            # Use the Day components to calculate days to add
            days_to_add = (other.day.year - 1970) * 365 + (other.day.month - 1) * 30 + (other.day.day - 1)
            total_seconds = days_to_add * 86400 + other.hour * 3600 + other.minute * 60 + other.second

            return self + total_seconds
        raise NotImplementedError(f"Cannot add Moment and {type(other).__name__}")

    # ---------- Comparison operators ----------

    def __eq__(self, other: object) -> bool:
        """Return `True` if two `Moment` instances represent the same datetime.

        Non-`Moment` objects compare as `False`.

        Example:
            >>> Moment(2025, 10, 24, 14, 30, 0) == Moment(2025, 10, 24, 14, 30, 0)
            True
        """
        return isinstance(other, Moment) and self._datetime == other._datetime

    def __lt__(self, other: Moment) -> bool:
        """Return `True` if `self` occurs before `other` in chronological order.

        Args:
            other: Another `Moment` to compare to.

        Returns:
            Whether `self` is earlier than `other`.

        Example:
            >>> Moment(2025, 10, 24, 14, 30, 0) < Moment(2025, 10, 24, 15, 30, 0)
            True
        """
        if not isinstance(other, Moment):
            return NotImplemented
        return self._datetime < other._datetime

    def __le__(self, other: Moment) -> bool:
        """Return `True` if `self` is earlier than or equal to `other`."""
        if not isinstance(other, Moment):
            return NotImplemented
        return self._datetime <= other._datetime

    def __gt__(self, other: Moment) -> bool:
        """Return `True` if `self` occurs after `other`."""
        if not isinstance(other, Moment):
            return NotImplemented
        return self._datetime > other._datetime

    def __ge__(self, other: Moment) -> bool:
        """Return `True` if `self` is later than or equal to `other`."""
        if not isinstance(other, Moment):
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
            >>> isinstance(Moment(2025, 10, 24, 14, 30, 0).to_datetime(), datetime)
            True
        """
        return self._datetime
