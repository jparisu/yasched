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

# Moment construction keys
MOMENT_YEAR_KEYS = YamlKey({"year", "y"})
MOMENT_MONTH_KEYS = YamlKey({"month", "m"})
MOMENT_DAY_KEYS = YamlKey({"day", "d"})
MOMENT_HOUR_KEYS = YamlKey({"hour", "h", "hours"})
MOMENT_MINUTE_KEYS = YamlKey({"minute", "min", "minutes"})
MOMENT_SECOND_KEYS = YamlKey({"second", "sec", "seconds", "s"})
MOMENT_DATETIME_KEYS = YamlKey({"datetime", "time_string", "time_str", "timestamp"})
MOMENT_FORMAT_KEYS = YamlKey({"format", "fmt", "time_format"})
MOMENT_DATE_KEYS = YamlKey({"date", "day_part"})
MOMENT_DAYTIME_KEYS = YamlKey({"daytime", "time_part"})

# TimeSlot construction keys
TIMESLOT_START_KEYS = YamlKey({"start", "begin", "from"})
TIMESLOT_END_KEYS = YamlKey({"end", "finish", "to"})
TIMESLOT_DURATION_KEYS = YamlKey({"duration", "length", "duration_seconds"})
