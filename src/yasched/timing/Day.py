"""
A small, Pythonic utility for working with calendar days (no time-of-day).
Provides simple construction, string conversion, arithmetic (add days),
and rich comparisons, while staying lightweight and easy to use.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta


class Day:
    """Represents a specific calendar day (no time component).

    Internally wraps a `datetime.date` to keep the concept strictly at
    day-level precision (no hours/minutes/seconds, no timezone).

    The class supports:
      * Clean construction from year/month/day
      * Alternate constructors from strings and `datetime.date`
      * Easy access to `year`, `month`, `day`
      * String conversion as ISO date (YYYY-MM-DD)
      * Adding days (immutably, returns a new `Day`)
      * Comparisons (`==`, `<`, `<=`, `>`, `>=`) based on calendar order

    Memory footprint is minimized via `__slots__`, and instances behave
    immutably in practice (no public setters; methods return new instances).

    Example:
        >>> d = Day(2025, 10, 24)
        >>> str(d)
        '2025-10-24'
        >>> d2 = d.add_days(7)
        >>> d2
        Day(2025, 10, 31)
        >>> d < d2
        True
    """

    __slots__ = ("_date",)

    def __init__(self, year: int, month: int, day: int) -> None:
        """Initialize a `Day` from its components.

        Args:
            year: Four-digit year (e.g., 2025).
            month: Month number in [1, 12].
            day: Day-of-month in [1, 31] depending on the month/year.

        Raises:
            ValueError: If the provided components do not form a valid date.

        Example:
            >>> Day(2025, 1, 31)
            Day(2025, 1, 31)
        """
        self._date = date(year, month, day)

    # ---------- Alternate constructors ----------

    @classmethod
    def today(cls) -> Day:
        """Construct a `Day` representing the current local calendar date.

        Returns:
            A `Day` for today (according to the system’s local date).

        Example:
            >>> isinstance(Day.today(), Day)
            True
        """
        d = date.today()
        return cls(d.year, d.month, d.day)

    @classmethod
    def from_string(cls, date_str: str, fmt: str = "%Y-%m-%d") -> Day:
        """Construct a `Day` by parsing a string.

        Args:
            date_str: The string to parse (e.g., "2025-10-24").
            fmt: A `datetime.strptime`-compatible format string.
                 Defaults to ISO date "%Y-%m-%d".

        Returns:
            A `Day` corresponding to the parsed date.

        Raises:
            ValueError: If parsing fails or produces an invalid date.

        Examples:
            >>> Day.from_string("2025-10-24")
            Day(2025, 10, 24)
            >>> Day.from_string("24/10/2025", fmt="%d/%m/%Y")
            Day(2025, 10, 24)
        """
        dt = datetime.strptime(date_str, fmt).date()
        return cls(dt.year, dt.month, dt.day)

    @classmethod
    def from_date(cls, d: date) -> Day:
        """Construct a `Day` from a `datetime.date`.

        Args:
            d: A `datetime.date` instance.

        Returns:
            A `Day` with the same year, month, and day.

        Example:
            >>> Day.from_date(date(2025, 10, 24))
            Day(2025, 10, 24)
        """
        return cls(d.year, d.month, d.day)

    # ---------- Representation ----------

    def __str__(self) -> str:
        """Return the ISO-8601 string representation (YYYY-MM-DD).

        Example:
            >>> str(Day(2025, 10, 24))
            '2025-10-24'
        """
        return self._date.isoformat()

    def __repr__(self) -> str:
        """Return an unambiguous constructor-style representation.

        Example:
            >>> repr(Day(2025, 10, 24))
            'Day(2025, 10, 24)'
        """
        return f"Day({self.year}, {self.month}, {self.day})"

    def to_string(self, fmt: str = "%Y-%m-%d") -> str:
        """Format the day as a string using the specified format.

        Args:
            fmt: A `datetime.strftime`-compatible format string.
                 Defaults to ISO date "%Y-%m-%d".

        Returns:
            The formatted string representation of the day.

        Examples:
            >>> Day(2025, 10, 24).to_string()
            '2025-10-24'
            >>> Day(2025, 10, 24).to_string("%d/%m/%Y")
            '24/10/2025'
        """
        return self._date.strftime(fmt)

    # ---------- Accessors ----------

    @property
    def year(self) -> int:
        """The four-digit year component.

        Example:
            >>> Day(2025, 10, 24).year
            2025
        """
        return self._date.year

    @property
    def month(self) -> int:
        """The month component in [1, 12].

        Example:
            >>> Day(2025, 10, 24).month
            10
        """
        return self._date.month

    @property
    def day(self) -> int:
        """The day-of-month component.

        Example:
            >>> Day(2025, 10, 24).day
            24
        """
        return self._date.day

    # ---------- Arithmetic ----------

    def add_days(self, n: int) -> Day:
        """Return a new `Day` offset by `n` days.

        This method does not mutate the instance; it returns a new `Day`.

        Args:
            n: Number of days to add (may be negative).

        Returns:
            A new `Day` representing `self + n days`.

        Example:
            >>> Day(2025, 10, 24).add_days(7)
            Day(2025, 10, 31)
        """
        return Day.from_date(self._date + timedelta(days=n))

    def __add__(self, other: int | Day) -> Day:
        """Add days or another Day to this Day.

        Args:
            other: Either an integer (number of days) or another Day.
                   If Day, adds years, months, and days from the other Day.

        Returns:
            A new Day representing the sum.

        Examples:
            >>> Day(2025, 10, 24) + 7
            Day(2025, 10, 31)
            >>> Day(2020, 1, 1) + Day(1, 2, 3)
            Day(2021, 3, 4)
        """
        if isinstance(other, int):
            return self.add_days(other)
        elif isinstance(other, Day):
            # Add years, months, and days from the other Day
            new_year = self.year + other.year
            new_month = self.month + other.month
            new_day = self.day + other.day
            
            # Handle month overflow
            while new_month > 12:
                new_month -= 12
                new_year += 1
            
            # Handle day overflow by creating a date and adding remaining days
            try:
                result = Day(new_year, new_month, new_day)
            except ValueError:
                # Day is too large for the month, adjust
                import calendar
                max_day = calendar.monthrange(new_year, new_month)[1]
                overflow_days = new_day - max_day
                result = Day(new_year, new_month, max_day)
                result = result.add_days(overflow_days)
            
            return result
        raise NotImplementedError(f"Cannot add Day and {type(other).__name__}")

    # ---------- Comparison operators ----------

    def __eq__(self, other: object) -> bool:
        """Return `True` if two `Day` instances represent the same calendar day.

        Non-`Day` objects compare as `False`.

        Example:
            >>> Day(2025, 10, 24) == Day(2025, 10, 24)
            True
            >>> Day(2025, 10, 24) == "2025-10-24"
            False
        """
        return isinstance(other, Day) and self._date == other._date

    def __lt__(self, other: Day) -> bool:
        """Return `True` if `self` occurs before `other` in calendar order.

        Args:
            other: Another `Day` to compare to.

        Returns:
            Whether `self` is earlier than `other`.

        Example:
            >>> Day(2025, 10, 24) < Day(2025, 10, 31)
            True
        """
        if not isinstance(other, Day):
            return NotImplemented
        return self._date < other._date

    def __le__(self, other: Day) -> bool:
        """Return `True` if `self` is earlier than or equal to `other`."""
        if not isinstance(other, Day):
            return NotImplemented
        return self._date <= other._date

    def __gt__(self, other: Day) -> bool:
        """Return `True` if `self` occurs after `other`."""
        if not isinstance(other, Day):
            return NotImplemented
        return self._date > other._date

    def __ge__(self, other: Day) -> bool:
        """Return `True` if `self` is later than or equal to `other`."""
        if not isinstance(other, Day):
            return NotImplemented
        return self._date >= other._date

    # ---------- Interop ----------

    def to_date(self) -> date:
        """Return the underlying `datetime.date`.

        Useful when interoperating with standard library or third-party code
        that expects a `datetime.date`.

        Returns:
            The wrapped `datetime.date`.

        Example:
            >>> isinstance(Day(2025, 10, 24).to_date(), date)
            True
        """
        return self._date
