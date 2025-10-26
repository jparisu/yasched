"""
YAML reading functions for timing classes (Day, Moment, TimeSlot).
Provides versatile construction from YAML data.
"""

from __future__ import annotations

import timing_constants

from yasched.timing.Day import Day
from yasched.timing.DayTime import DayTime
from yasched.timing.Moment import Moment
from yasched.timing.TimeSlot import TimeSlot
from yasched.yaml_utils.exceptions import YamlFormatError
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
    if yaml_node.has(timing_constants.DAY_DATE_KEYS):
        date_str = yaml_node.get(timing_constants.DAY_DATE_KEYS, force_type=[str])
        fmt = yaml_node.get(timing_constants.DAY_FORMAT_KEYS, default="%Y-%m-%d", throw=False)
        try:
            return Day.from_string(date_str, fmt=fmt)
        except ValueError as e:
            raise YamlFormatError(f"Invalid date string '{date_str}' with format '{fmt}': {e}") from e

    # Method 2: From components
    if (
        yaml_node.has(timing_constants.DAY_YEAR_KEYS)
        and yaml_node.has(timing_constants.DAY_MONTH_KEYS)
        and yaml_node.has(timing_constants.DAY_DAY_KEYS)
    ):
        year = yaml_node.get(timing_constants.DAY_YEAR_KEYS, force_type=[int])
        month = yaml_node.get(timing_constants.DAY_MONTH_KEYS, force_type=[int])
        day = yaml_node.get(timing_constants.DAY_DAY_KEYS, force_type=[int])
        try:
            return Day(year, month, day)
        except ValueError as e:
            raise YamlFormatError(f"Invalid day components: year={year}, month={month}, day={day}: {e}") from e

    raise YamlFormatError("Day YAML must contain either 'date' or 'year'/'month'/'day' fields")


def time_from_yaml(yaml_node: YamlReader) -> Moment:
    """Construct a Moment from YAML data.

    Supports multiple construction methods:
    1. From components: year, month, day, hour, minute, second
    2. From string: datetime (with optional format)
    3. From Day and DayTime objects

    Args:
        yaml_node: YamlReader containing the time data.

    Returns:
        A Moment instance.

    Raises:
        YamlFormatError: If the YAML data is invalid or incomplete.

    Examples:
        >>> # From components
        >>> yaml_str = "year: 2025\\nmonth: 10\\nday: 24\\nhour: 14\\nminute: 30\\nsecond: 0"
        >>> time_from_yaml(YamlReader(yaml_str))
        Moment(2025, 10, 24, 14, 30, 0)

        >>> # From string
        >>> yaml_str = "datetime: '2025-10-24 14:30:00'"
        >>> time_from_yaml(YamlReader(yaml_str))
        Moment(2025, 10, 24, 14, 30, 0)
    """

    # Method 1: From datetime string
    if yaml_node.has(timing_constants.TIME_DATETIME_KEYS):
        datetime_str = yaml_node.get(timing_constants.TIME_DATETIME_KEYS, force_type=[str])
        fmt = yaml_node.get(timing_constants.TIME_FORMAT_KEYS, default="%Y-%m-%d %H:%M:%S", throw=False)
        try:
            return Moment.from_string(datetime_str, fmt=fmt)
        except ValueError as e:
            raise YamlFormatError(f"Invalid datetime string '{datetime_str}' with format '{fmt}': {e}") from e

    # Method 2: From Day and DayTime
    if yaml_node.has(timing_constants.TIME_DATE_KEYS) and yaml_node.has(timing_constants.TIME_DAYTIME_KEYS):
        day_node = yaml_node.get_child(timing_constants.TIME_DATE_KEYS)
        daytime_node = yaml_node.get_child(timing_constants.TIME_DAYTIME_KEYS)
        day = day_from_yaml(day_node)
        daytime = daytime_from_yaml(daytime_node)
        return Moment.from_day_and_daytime(day, daytime)

    # Method 3: From components
    if (
        yaml_node.has(timing_constants.TIME_YEAR_KEYS)
        and yaml_node.has(timing_constants.TIME_MONTH_KEYS)
        and yaml_node.has(timing_constants.TIME_DAY_KEYS)
    ):
        year = yaml_node.get(timing_constants.TIME_YEAR_KEYS, force_type=[int])
        month = yaml_node.get(timing_constants.TIME_MONTH_KEYS, force_type=[int])
        day = yaml_node.get(timing_constants.TIME_DAY_KEYS, force_type=[int])
        hour = yaml_node.get(timing_constants.TIME_HOUR_KEYS, default=0, throw=False, force_type=[int])
        minute = yaml_node.get(timing_constants.TIME_MINUTE_KEYS, default=0, throw=False, force_type=[int])
        second = yaml_node.get(timing_constants.TIME_SECOND_KEYS, default=0, throw=False, force_type=[int])
        try:
            return Moment(year, month, day, hour, minute, second)
        except ValueError as e:
            raise YamlFormatError(
                f"Invalid time components: year={year}, month={month}, day={day}, "
                f"hour={hour}, minute={minute}, second={second}: {e}"
            ) from e

    raise YamlFormatError(
        "Moment YAML must contain either 'datetime', 'date'/'daytime', or 'year'/'month'/'day' fields"
    )


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
        TimeSlot(Moment(2025, 10, 24, 14, 0, 0), Moment(2025, 10, 24, 16, 0, 0))

        >>> # From start and duration
        >>> yaml_str = '''
        ... start:
        ...   datetime: '2025-10-24 14:00:00'
        ... duration: 7200
        ... '''
        >>> timeslot_from_yaml(YamlReader(yaml_str))
        TimeSlot(Moment(2025, 10, 24, 14, 0, 0), Moment(2025, 10, 24, 16, 0, 0))
    """
    # Start time is always required
    if not yaml_node.has(timing_constants.TIMESLOT_START_KEYS):
        raise YamlFormatError("TimeSlot YAML must contain 'start' field")

    start_node = yaml_node.get_child(timing_constants.TIMESLOT_START_KEYS)
    start = time_from_yaml(start_node)

    # Method 1: From start and end
    if yaml_node.has(timing_constants.TIMESLOT_END_KEYS):
        end_node = yaml_node.get_child(timing_constants.TIMESLOT_END_KEYS)
        end = time_from_yaml(end_node)
        return TimeSlot(start, end)

    # Method 2: From start and duration
    if yaml_node.has(timing_constants.TIMESLOT_DURATION_KEYS):
        # Duration can be either an int (seconds) or a Moment object (nested YAML)
        try:
            # Try to get as a nested Moment object first
            duration_node = yaml_node.get_child(timing_constants.TIMESLOT_DURATION_KEYS, throw=False)
            if duration_node and duration_node._yaml and isinstance(duration_node._yaml, dict):
                duration_time = time_from_yaml(duration_node)
                return TimeSlot.from_duration(start, duration_time)
        except (YamlFormatError, AttributeError):
            pass

        # Otherwise, treat as seconds (backward compatibility)
        duration_seconds = yaml_node.get(timing_constants.TIMESLOT_DURATION_KEYS, force_type=[int])
        # Convert seconds to Moment object using epoch + seconds
        days = duration_seconds // 86400
        remaining = duration_seconds % 86400
        hours = remaining // 3600
        remaining = remaining % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        # Use 1970-01-01 as epoch plus the calculated days
        duration_time = Moment(1970, 1, 1 + days, hours, minutes, seconds)
        return TimeSlot.from_duration(start, duration_time)

    raise YamlFormatError("TimeSlot YAML must contain either 'end' or 'duration' field")


def daytime_from_yaml(yaml_node: YamlReader) -> DayTime:
    """Construct a DayTime from YAML data.

    Supports multiple construction methods:
    1. From components: hour, minute, second
    2. From string: time (with optional format)

    Args:
        yaml_node: YamlReader containing the daytime data.

    Returns:
        A DayTime instance.

    Raises:
        YamlFormatError: If the YAML data is invalid or incomplete.

    Examples:
        >>> # From components
        >>> yaml_str = '''
        ... hour: 14
        ... minute: 30
        ... second: 0
        ... '''
        >>> daytime_from_yaml(YamlReader(yaml_str))
        DayTime(14, 30, 0)

        >>> # From string
        >>> yaml_str = "time: '14:30:00'"
        >>> daytime_from_yaml(YamlReader(yaml_str))
        DayTime(14, 30, 0)
    """

    # Method 1: From time string
    if yaml_node.has(timing_constants.DAYTIME_TIME_KEYS):
        time_str = yaml_node.get(timing_constants.DAYTIME_TIME_KEYS, force_type=[str])
        fmt = yaml_node.get(timing_constants.DAYTIME_FORMAT_KEYS, default="%H:%M:%S", throw=False)
        try:
            return DayTime.from_string(time_str, fmt=fmt)
        except ValueError as e:
            raise YamlFormatError(f"Invalid time string '{time_str}' with format '{fmt}': {e}") from e

    # Method 2: From components
    hour = yaml_node.get(timing_constants.DAYTIME_HOUR_KEYS, default=0, throw=False, force_type=[int])
    minute = yaml_node.get(timing_constants.DAYTIME_MINUTE_KEYS, default=0, throw=False, force_type=[int])
    second = yaml_node.get(timing_constants.DAYTIME_SECOND_KEYS, default=0, throw=False, force_type=[int])
    try:
        return DayTime(hour, minute, second)
    except ValueError as e:
        raise YamlFormatError(f"Invalid daytime components: hour={hour}, minute={minute}, second={second}: {e}") from e
