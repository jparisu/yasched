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
    3. From Day and DayTime objects

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
    from yasched.yaml_utils.timing_constants import TIME_DATE_KEYS, TIME_DAYTIME_KEYS

    # Method 1: From datetime string
    if yaml_node.has(TIME_DATETIME_KEYS):
        datetime_str = yaml_node.get(TIME_DATETIME_KEYS, force_type=[str])
        fmt = yaml_node.get(TIME_FORMAT_KEYS, default="%Y-%m-%d %H:%M:%S", throw=False)
        try:
            return Time.from_string(datetime_str, fmt=fmt)
        except ValueError as e:
            raise YamlFormatError(f"Invalid datetime string '{datetime_str}' with format '{fmt}': {e}") from e

    # Method 2: From Day and DayTime
    if yaml_node.has(TIME_DATE_KEYS) and yaml_node.has(TIME_DAYTIME_KEYS):
        day_node = yaml_node.get_child(TIME_DATE_KEYS)
        daytime_node = yaml_node.get_child(TIME_DAYTIME_KEYS)
        day = day_from_yaml(day_node)
        daytime = daytime_from_yaml(daytime_node)
        return Time.from_day_and_daytime(day, daytime)

    # Method 3: From components
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

    raise YamlFormatError("Time YAML must contain either 'datetime', 'date'/'daytime', or 'year'/'month'/'day' fields")



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
        # Duration can be either an int (seconds) or a Time object (nested YAML)
        try:
            # Try to get as a nested Time object first
            duration_node = yaml_node.get_child(TIMESLOT_DURATION_KEYS, throw=False)
            if duration_node and duration_node._yaml and isinstance(duration_node._yaml, dict):
                duration_time = time_from_yaml(duration_node)
                return TimeSlot.from_duration(start, duration_time)
        except (YamlFormatError, AttributeError):
            pass
        
        # Otherwise, treat as seconds (backward compatibility)
        duration_seconds = yaml_node.get(TIMESLOT_DURATION_KEYS, force_type=[int])
        # Convert seconds to Time object using epoch + seconds
        days = duration_seconds // 86400
        remaining = duration_seconds % 86400
        hours = remaining // 3600
        remaining = remaining % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        # Use 1970-01-01 as epoch plus the calculated days
        duration_time = Time(1970, 1, 1 + days, hours, minutes, seconds)
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
    from yasched.timing.DayTime import DayTime
    from yasched.yaml_utils.timing_constants import (
        DAYTIME_FORMAT_KEYS,
        DAYTIME_HOUR_KEYS,
        DAYTIME_MINUTE_KEYS,
        DAYTIME_SECOND_KEYS,
        DAYTIME_TIME_KEYS,
    )

    # Method 1: From time string
    if yaml_node.has(DAYTIME_TIME_KEYS):
        time_str = yaml_node.get(DAYTIME_TIME_KEYS, force_type=[str])
        fmt = yaml_node.get(DAYTIME_FORMAT_KEYS, default="%H:%M:%S", throw=False)
        try:
            return DayTime.from_string(time_str, fmt=fmt)
        except ValueError as e:
            raise YamlFormatError(f"Invalid time string '{time_str}' with format '{fmt}': {e}") from e

    # Method 2: From components
    hour = yaml_node.get(DAYTIME_HOUR_KEYS, default=0, throw=False, force_type=[int])
    minute = yaml_node.get(DAYTIME_MINUTE_KEYS, default=0, throw=False, force_type=[int])
    second = yaml_node.get(DAYTIME_SECOND_KEYS, default=0, throw=False, force_type=[int])
    try:
        return DayTime(hour, minute, second)
    except ValueError as e:
        raise YamlFormatError(f"Invalid daytime components: hour={hour}, minute={minute}, second={second}: {e}") from e


def periodic_from_yaml(yaml_node: YamlReader) -> Periodic:
    """Construct a Periodic from YAML data.

    Supports multiple construction methods:
    1. From start, end, and repetitions list
    2. From start, interval, and count
    3. From start, end, and daily interval
    4. From start, end, and weekly interval

    Args:
        yaml_node: YamlReader containing the periodic data.

    Returns:
        A Periodic instance.

    Raises:
        YamlFormatError: If the YAML data is invalid or incomplete.

    Examples:
        >>> # From start, end, and repetitions
        >>> yaml_str = '''
        ... start:
        ...   start:
        ...     datetime: '2025-01-01 09:00:00'
        ...   end:
        ...     datetime: '2025-01-01 10:00:00'
        ... end:
        ...   start:
        ...     datetime: '2025-01-31 09:00:00'
        ...   end:
        ...     datetime: '2025-01-31 10:00:00'
        ... repetitions:
        ...   - datetime: '1970-01-03 00:00:00'
        ... '''
        >>> periodic_from_yaml(YamlReader(yaml_str))
        Periodic(...)
    """
    from yasched.timing.Periodic import Periodic
    from yasched.yaml_utils.timing_constants import (
        PERIODIC_COUNT_KEYS,
        PERIODIC_DAILY_KEYS,
        PERIODIC_END_KEYS,
        PERIODIC_INTERVAL_KEYS,
        PERIODIC_REPETITIONS_KEYS,
        PERIODIC_START_KEYS,
        PERIODIC_WEEKLY_KEYS,
    )

    # Start slot is always required
    if not yaml_node.has(PERIODIC_START_KEYS):
        raise YamlFormatError("Periodic YAML must contain 'start' field")

    start_node = yaml_node.get_child(PERIODIC_START_KEYS)
    start = timeslot_from_yaml(start_node)

    # Method 1: From start, interval, and count
    if yaml_node.has(PERIODIC_INTERVAL_KEYS) and yaml_node.has(PERIODIC_COUNT_KEYS):
        interval_node = yaml_node.get_child(PERIODIC_INTERVAL_KEYS)
        interval = time_from_yaml(interval_node)
        count = yaml_node.get(PERIODIC_COUNT_KEYS, force_type=[int])
        return Periodic.from_count(start, interval, count)

    # Method 2: From start, end, and daily interval
    if yaml_node.has(PERIODIC_END_KEYS) and yaml_node.has(PERIODIC_DAILY_KEYS):
        end_node = yaml_node.get_child(PERIODIC_END_KEYS)
        end = timeslot_from_yaml(end_node)
        daily_interval = yaml_node.get(PERIODIC_DAILY_KEYS, force_type=[int])
        return Periodic.from_daily(start, end, interval_days=daily_interval)

    # Method 3: From start, end, and weekly interval
    if yaml_node.has(PERIODIC_END_KEYS) and yaml_node.has(PERIODIC_WEEKLY_KEYS):
        end_node = yaml_node.get_child(PERIODIC_END_KEYS)
        end = timeslot_from_yaml(end_node)
        weekly_interval = yaml_node.get(PERIODIC_WEEKLY_KEYS, force_type=[int])
        return Periodic.from_weekly(start, end, interval_weeks=weekly_interval)

    # Method 4: From start, end, and repetitions list
    if yaml_node.has(PERIODIC_END_KEYS) and yaml_node.has(PERIODIC_REPETITIONS_KEYS):
        end_node = yaml_node.get_child(PERIODIC_END_KEYS)
        end = timeslot_from_yaml(end_node)

        # Get repetitions as a list
        reps_data = yaml_node.get(PERIODIC_REPETITIONS_KEYS)
        if not isinstance(reps_data, list):
            raise YamlFormatError("Repetitions must be a list")

        repetitions = []
        for rep_data in reps_data:
            rep_reader = YamlReader.from_dict(rep_data)
            repetitions.append(time_from_yaml(rep_reader))

        return Periodic(start, end, repetitions)

    raise YamlFormatError(
        "Periodic YAML must contain either 'end' with 'repetitions', 'daily', or 'weekly', "
        "or 'interval' with 'count'"
    )
