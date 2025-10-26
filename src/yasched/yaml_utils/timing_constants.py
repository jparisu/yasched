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

# Time construction keys
TIME_YEAR_KEYS = YamlKey({"year", "y"})
TIME_MONTH_KEYS = YamlKey({"month", "m"})
TIME_DAY_KEYS = YamlKey({"day", "d"})
TIME_HOUR_KEYS = YamlKey({"hour", "h", "hours"})
TIME_MINUTE_KEYS = YamlKey({"minute", "min", "minutes"})
TIME_SECOND_KEYS = YamlKey({"second", "sec", "seconds", "s"})
TIME_DATETIME_KEYS = YamlKey({"datetime", "time_string", "time_str", "timestamp"})
TIME_FORMAT_KEYS = YamlKey({"format", "fmt", "time_format"})

# TimeSlot construction keys
TIMESLOT_START_KEYS = YamlKey({"start", "begin", "from"})
TIMESLOT_END_KEYS = YamlKey({"end", "finish", "to"})
TIMESLOT_DURATION_KEYS = YamlKey({"duration", "length", "duration_seconds"})
