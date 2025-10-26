"""
YAML reading functions for timing classes (Day, Time, TimeSlot).
Provides versatile construction from YAML data.
"""

from __future__ import annotations

from yasched.timing.Day import Day
from yasched.timing.Time import Time
from yasched.timing.TimeSlot import TimeSlot
from yasched.yaml_utils.exceptions import YamlFormatError
from yasched.yaml_utils.timing_constants import (
    DAY_DATE_KEYS,
    DAY_DAY_KEYS,
    DAY_FORMAT_KEYS,
    DAY_MONTH_KEYS,
    DAY_YEAR_KEYS,
    TIME_DATETIME_KEYS,
    TIME_DAY_KEYS,
    TIME_FORMAT_KEYS,
    TIME_HOUR_KEYS,
    TIME_MINUTE_KEYS,
    TIME_MONTH_KEYS,
    TIME_SECOND_KEYS,
    TIME_YEAR_KEYS,
    TIMESLOT_DURATION_KEYS,
    TIMESLOT_END_KEYS,
    TIMESLOT_START_KEYS,
)
from yasched.yaml_utils.YamlReader import YamlReader


def day_from_yaml(yaml_node: YamlReader) -> Day:
    """Construct a Day from YAML data.

    Supports multiple construction methods:
    1. From components: year, month, day
    2. From string: date (with optional format)

    Args:
        yaml_node: YamlReader containing the day data.

    Returns:
        A Day instance.

    Raises:
        YamlFormatError: If the YAML data is invalid or incomplete.

    Examples:
        >>> # From components
        >>> yaml_str = "year: 2025\\nmonth: 10\\nday: 24"
        >>> day_from_yaml(YamlReader(yaml_str))
        Day(2025, 10, 24)

        >>> # From string
        >>> yaml_str = "date: '2025-10-24'"
        >>> day_from_yaml(YamlReader(yaml_str))
        Day(2025, 10, 24)
    """
    # Method 1: From date string
    if yaml_node.has(DAY_DATE_KEYS):
        date_str = yaml_node.get(DAY_DATE_KEYS, force_type=[str])
        fmt = yaml_node.get(DAY_FORMAT_KEYS, default="%Y-%m-%d", throw=False)
        try:
            return Day.from_string(date_str, fmt=fmt)
        except ValueError as e:
            raise YamlFormatError(f"Invalid date string '{date_str}' with format '{fmt}': {e}") from e

    # Method 2: From components
    if yaml_node.has(DAY_YEAR_KEYS) and yaml_node.has(DAY_MONTH_KEYS) and yaml_node.has(DAY_DAY_KEYS):
        year = yaml_node.get(DAY_YEAR_KEYS, force_type=[int])
        month = yaml_node.get(DAY_MONTH_KEYS, force_type=[int])
        day = yaml_node.get(DAY_DAY_KEYS, force_type=[int])
        try:
            return Day(year, month, day)
        except ValueError as e:
            raise YamlFormatError(f"Invalid day components: year={year}, month={month}, day={day}: {e}") from e

    raise YamlFormatError("Day YAML must contain either 'date' or 'year'/'month'/'day' fields")


def time_from_yaml(yaml_node: YamlReader) -> Time:
    """Construct a Time from YAML data.

    Supports multiple construction methods:
    1. From components: year, month, day, hour, minute, second
    2. From string: datetime (with optional format)

    Args:
        yaml_node: YamlReader containing the time data.

    Returns:
        A Time instance.

    Raises:
        YamlFormatError: If the YAML data is invalid or incomplete.

    Examples:
        >>> # From components
        >>> yaml_str = "year: 2025\\nmonth: 10\\nday: 24\\nhour: 14\\nminute: 30\\nsecond: 0"
        >>> time_from_yaml(YamlReader(yaml_str))
        Time(2025, 10, 24, 14, 30, 0)

        >>> # From string
        >>> yaml_str = "datetime: '2025-10-24 14:30:00'"
        >>> time_from_yaml(YamlReader(yaml_str))
        Time(2025, 10, 24, 14, 30, 0)
    """
    # Method 1: From datetime string
    if yaml_node.has(TIME_DATETIME_KEYS):
        datetime_str = yaml_node.get(TIME_DATETIME_KEYS, force_type=[str])
        fmt = yaml_node.get(TIME_FORMAT_KEYS, default="%Y-%m-%d %H:%M:%S", throw=False)
        try:
            return Time.from_string(datetime_str, fmt=fmt)
        except ValueError as e:
            raise YamlFormatError(f"Invalid datetime string '{datetime_str}' with format '{fmt}': {e}") from e

    # Method 2: From components
    if yaml_node.has(TIME_YEAR_KEYS) and yaml_node.has(TIME_MONTH_KEYS) and yaml_node.has(TIME_DAY_KEYS):
        year = yaml_node.get(TIME_YEAR_KEYS, force_type=[int])
        month = yaml_node.get(TIME_MONTH_KEYS, force_type=[int])
        day = yaml_node.get(TIME_DAY_KEYS, force_type=[int])
        hour = yaml_node.get(TIME_HOUR_KEYS, default=0, throw=False, force_type=[int])
        minute = yaml_node.get(TIME_MINUTE_KEYS, default=0, throw=False, force_type=[int])
        second = yaml_node.get(TIME_SECOND_KEYS, default=0, throw=False, force_type=[int])
        try:
            return Time(year, month, day, hour, minute, second)
        except ValueError as e:
            raise YamlFormatError(
                f"Invalid time components: year={year}, month={month}, day={day}, "
                f"hour={hour}, minute={minute}, second={second}: {e}"
            ) from e

    raise YamlFormatError("Time YAML must contain either 'datetime' or 'year'/'month'/'day' fields")


def timeslot_from_yaml(yaml_node: YamlReader) -> TimeSlot:
    """Construct a TimeSlot from YAML data.

    Supports multiple construction methods:
    1. From start and end times
    2. From start time and duration (in seconds)

    Args:
        yaml_node: YamlReader containing the timeslot data.

    Returns:
        A TimeSlot instance.

    Raises:
        YamlFormatError: If the YAML data is invalid or incomplete.

    Examples:
        >>> # From start and end
        >>> yaml_str = '''
        ... start:
        ...   datetime: '2025-10-24 14:00:00'
        ... end:
        ...   datetime: '2025-10-24 16:00:00'
        ... '''
        >>> timeslot_from_yaml(YamlReader(yaml_str))
        TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))

        >>> # From start and duration
        >>> yaml_str = '''
        ... start:
        ...   datetime: '2025-10-24 14:00:00'
        ... duration: 7200
        ... '''
        >>> timeslot_from_yaml(YamlReader(yaml_str))
        TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))
    """
    # Start time is always required
    if not yaml_node.has(TIMESLOT_START_KEYS):
        raise YamlFormatError("TimeSlot YAML must contain 'start' field")

    start_node = yaml_node.get_child(TIMESLOT_START_KEYS)
    start = time_from_yaml(start_node)

    # Method 1: From start and end
    if yaml_node.has(TIMESLOT_END_KEYS):
        end_node = yaml_node.get_child(TIMESLOT_END_KEYS)
        end = time_from_yaml(end_node)
        return TimeSlot(start, end)

    # Method 2: From start and duration
    if yaml_node.has(TIMESLOT_DURATION_KEYS):
        duration = yaml_node.get(TIMESLOT_DURATION_KEYS, force_type=[int])
        return TimeSlot.from_duration(start, duration)

    raise YamlFormatError("TimeSlot YAML must contain either 'end' or 'duration' field")
