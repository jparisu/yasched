"""
YAML constants for timing-related keys.
These constants define the alternative YAML keys that can be used
to construct Day, Time, and TimeSlot objects.
"""

from yasched.yaml_utils.YamlReader import YamlKey

# Day construction keys
DAY_YEAR_KEYS = YamlKey({"year", "y"})
DAY_MONTH_KEYS = YamlKey({"month", "m"})
DAY_DAY_KEYS = YamlKey({"day", "d"})
DAY_DATE_KEYS = YamlKey({"date", "day_string", "day_str"})
DAY_FORMAT_KEYS = YamlKey({"format", "fmt", "date_format"})

# DayTime construction keys
DAYTIME_HOUR_KEYS = YamlKey({"hour", "h", "hours"})
DAYTIME_MINUTE_KEYS = YamlKey({"minute", "min", "minutes"})
DAYTIME_SECOND_KEYS = YamlKey({"second", "sec", "seconds", "s"})
DAYTIME_TIME_KEYS = YamlKey({"time", "daytime", "time_string"})
DAYTIME_FORMAT_KEYS = YamlKey({"format", "fmt", "time_format"})

# Time construction keys
TIME_YEAR_KEYS = YamlKey({"year", "y"})
TIME_MONTH_KEYS = YamlKey({"month", "m"})
TIME_DAY_KEYS = YamlKey({"day", "d"})
TIME_HOUR_KEYS = YamlKey({"hour", "h", "hours"})
TIME_MINUTE_KEYS = YamlKey({"minute", "min", "minutes"})
TIME_SECOND_KEYS = YamlKey({"second", "sec", "seconds", "s"})
TIME_DATETIME_KEYS = YamlKey({"datetime", "time_string", "time_str", "timestamp"})
TIME_FORMAT_KEYS = YamlKey({"format", "fmt", "time_format"})
TIME_DATE_KEYS = YamlKey({"date", "day_part"})
TIME_DAYTIME_KEYS = YamlKey({"daytime", "time_part"})

# TimeSlot construction keys
TIMESLOT_START_KEYS = YamlKey({"start", "begin", "from"})
TIMESLOT_END_KEYS = YamlKey({"end", "finish", "to"})
TIMESLOT_DURATION_KEYS = YamlKey({"duration", "length", "duration_seconds"})

# Periodic construction keys
PERIODIC_START_KEYS = YamlKey({"start", "start_slot", "first"})
PERIODIC_END_KEYS = YamlKey({"end", "end_slot", "last"})
PERIODIC_REPETITIONS_KEYS = YamlKey({"repetitions", "reps", "pattern"})
PERIODIC_INTERVAL_KEYS = YamlKey({"interval", "repeat_interval"})
PERIODIC_COUNT_KEYS = YamlKey({"count", "occurrences", "n"})
PERIODIC_DAILY_KEYS = YamlKey({"daily", "days", "day_interval"})
PERIODIC_WEEKLY_KEYS = YamlKey({"weekly", "weeks", "week_interval"})

