import unittest

from yasched.timing.Time import Time

from yasched.timing.Day import Day
from yasched.timing.DayTime import DayTime
from yasched.timing.TimeSlot import TimeSlot
from yasched.yaml_utils.exceptions import YamlFormatError
from yasched.yaml_utils.timing_reader import (
    day_from_yaml,
    daytime_from_yaml,
    time_from_yaml,
    timeslot_from_yaml,
)
from yasched.yaml_utils.YamlReader import YamlReader


class TestDayFromYaml(unittest.TestCase):
    # ---------- Construction from components ----------

    def test_day_from_components(self):
        yaml_str = """year: 2025
month: 10
day: 24"""
        day = day_from_yaml(YamlReader(yaml_str))
        self.assertEqual(day, Day(2025, 10, 24))

    def test_day_from_components_short_keys(self):
        yaml_str = """y: 2025
m: 10
d: 24"""
        day = day_from_yaml(YamlReader(yaml_str))
        self.assertEqual(day, Day(2025, 10, 24))

    def test_day_from_components_mixed_keys(self):
        yaml_str = """y: 2025
month: 10
d: 24"""
        day = day_from_yaml(YamlReader(yaml_str))
        self.assertEqual(day, Day(2025, 10, 24))

    # ---------- Construction from string ----------

    def test_day_from_string_default_format(self):
        yaml_str = """date: '2025-10-24'"""
        day = day_from_yaml(YamlReader(yaml_str))
        self.assertEqual(day, Day(2025, 10, 24))

    def test_day_from_string_custom_format(self):
        yaml_str = """date: '24/10/2025'
format: '%d/%m/%Y'"""
        day = day_from_yaml(YamlReader(yaml_str))
        self.assertEqual(day, Day(2025, 10, 24))

    def test_day_from_string_alternative_keys(self):
        yaml_str = """day_string: '2025-10-24'"""
        day = day_from_yaml(YamlReader(yaml_str))
        self.assertEqual(day, Day(2025, 10, 24))

    # ---------- Error cases ----------

    def test_day_missing_fields_raises(self):
        yaml_str = """year: 2025
month: 10"""  # missing day
        with self.assertRaises(YamlFormatError):
            day_from_yaml(YamlReader(yaml_str))

    def test_day_invalid_date_raises(self):
        yaml_str = """year: 2025
month: 2
day: 30"""  # Feb 30 doesn't exist
        with self.assertRaises(YamlFormatError):
            day_from_yaml(YamlReader(yaml_str))

    def test_day_invalid_string_format_raises(self):
        yaml_str = """date: 'not-a-date'"""
        with self.assertRaises(YamlFormatError):
            day_from_yaml(YamlReader(yaml_str))

    def test_day_no_valid_keys_raises(self):
        yaml_str = """invalid: field"""
        with self.assertRaises(YamlFormatError):
            day_from_yaml(YamlReader(yaml_str))


class TestTimeFromYaml(unittest.TestCase):
    # ---------- Construction from components ----------

    def test_time_from_components_full(self):
        yaml_str = """year: 2025
month: 10
day: 24
hour: 14
minute: 30
second: 0"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 30, 0))

    def test_time_from_components_short_keys(self):
        yaml_str = """y: 2025
m: 10
d: 24
h: 14
min: 30
s: 0"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 30, 0))

    def test_time_from_components_defaults(self):
        yaml_str = """year: 2025
month: 10
day: 24"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 0, 0, 0))

    def test_time_from_components_partial(self):
        yaml_str = """year: 2025
month: 10
day: 24
hour: 14"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 0, 0))

    # ---------- Construction from string ----------

    def test_time_from_string_default_format(self):
        yaml_str = """datetime: '2025-10-24 14:30:00'"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 30, 0))

    def test_time_from_string_custom_format(self):
        yaml_str = """datetime: '24/10/2025 14:30'
format: '%d/%m/%Y %H:%M'"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 30, 0))

    def test_time_from_string_alternative_keys(self):
        yaml_str = """time_string: '2025-10-24 14:30:00'"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 30, 0))

    # ---------- Error cases ----------

    def test_time_missing_fields_raises(self):
        yaml_str = """year: 2025
month: 10"""  # missing day
        with self.assertRaises(YamlFormatError):
            time_from_yaml(YamlReader(yaml_str))

    def test_time_invalid_datetime_raises(self):
        yaml_str = """year: 2025
month: 2
day: 30
hour: 14"""  # Feb 30 doesn't exist
        with self.assertRaises(YamlFormatError):
            time_from_yaml(YamlReader(yaml_str))

    def test_time_invalid_string_format_raises(self):
        yaml_str = """datetime: 'not-a-datetime'"""
        with self.assertRaises(YamlFormatError):
            time_from_yaml(YamlReader(yaml_str))

    def test_time_no_valid_keys_raises(self):
        yaml_str = """invalid: field"""
        with self.assertRaises(YamlFormatError):
            time_from_yaml(YamlReader(yaml_str))


class TestTimeSlotFromYaml(unittest.TestCase):
    # ---------- Construction from start and end ----------

    def test_timeslot_from_start_end(self):
        yaml_str = """
start:
  datetime: '2025-10-24 14:00:00'
end:
  datetime: '2025-10-24 16:00:00'
"""
        slot = timeslot_from_yaml(YamlReader(yaml_str))
        expected = TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))
        self.assertEqual(slot, expected)

    def test_timeslot_from_start_end_components(self):
        yaml_str = """
start:
  year: 2025
  month: 10
  day: 24
  hour: 14
  minute: 0
  second: 0
end:
  year: 2025
  month: 10
  day: 24
  hour: 16
  minute: 0
  second: 0
"""
        slot = timeslot_from_yaml(YamlReader(yaml_str))
        expected = TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))
        self.assertEqual(slot, expected)

    def test_timeslot_alternative_keys(self):
        yaml_str = """
begin:
  datetime: '2025-10-24 14:00:00'
finish:
  datetime: '2025-10-24 16:00:00'
"""
        slot = timeslot_from_yaml(YamlReader(yaml_str))
        expected = TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))
        self.assertEqual(slot, expected)

    # ---------- Construction from start and duration ----------

    def test_timeslot_from_duration(self):
        yaml_str = """
start:
  datetime: '2025-10-24 14:00:00'
duration: 7200
"""
        slot = timeslot_from_yaml(YamlReader(yaml_str))
        expected = TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))
        self.assertEqual(slot, expected)

    def test_timeslot_from_duration_alternative_keys(self):
        yaml_str = """
start:
  datetime: '2025-10-24 14:00:00'
length: 3600
"""
        slot = timeslot_from_yaml(YamlReader(yaml_str))
        expected = TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 15, 0, 0))
        self.assertEqual(slot, expected)

    def test_timeslot_from_datetime_different_formats(self):
        # Test with custom datetime format
        yaml_str = """
start:
  datetime: '24/10/2025 14:00'
  format: '%d/%m/%Y %H:%M'
end:
  datetime: '24/10/2025 16:00'
  format: '%d/%m/%Y %H:%M'
"""
        slot = timeslot_from_yaml(YamlReader(yaml_str))
        expected = TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))
        self.assertEqual(slot, expected)

    # ---------- Error cases ----------

    def test_timeslot_missing_start_raises(self):
        yaml_str = """
end:
  datetime: '2025-10-24 16:00:00'
"""
        with self.assertRaises(YamlFormatError):
            timeslot_from_yaml(YamlReader(yaml_str))

    def test_timeslot_missing_end_and_duration_raises(self):
        yaml_str = """
start:
  datetime: '2025-10-24 14:00:00'
"""
        with self.assertRaises(YamlFormatError):
            timeslot_from_yaml(YamlReader(yaml_str))

    def test_timeslot_invalid_start_raises(self):
        yaml_str = """
start:
  datetime: 'not-a-datetime'
end:
  datetime: '2025-10-24 16:00:00'
"""
        with self.assertRaises(YamlFormatError):
            timeslot_from_yaml(YamlReader(yaml_str))


class TestDayTimeFromYaml(unittest.TestCase):
    # ---------- Construction from components ----------

    def test_daytime_from_components(self):
        yaml_str = """hour: 14
minute: 30
second: 0"""
        daytime = daytime_from_yaml(YamlReader(yaml_str))
        self.assertEqual(daytime, DayTime(14, 30, 0))

    def test_daytime_from_components_short_keys(self):
        yaml_str = """h: 14
min: 30
s: 0"""
        daytime = daytime_from_yaml(YamlReader(yaml_str))
        self.assertEqual(daytime, DayTime(14, 30, 0))

    def test_daytime_from_components_defaults(self):
        yaml_str = """hour: 14"""
        daytime = daytime_from_yaml(YamlReader(yaml_str))
        self.assertEqual(daytime, DayTime(14, 0, 0))

    # ---------- Construction from string ----------

    def test_daytime_from_string_default_format(self):
        yaml_str = """time: '14:30:00'"""
        daytime = daytime_from_yaml(YamlReader(yaml_str))
        self.assertEqual(daytime, DayTime(14, 30, 0))

    def test_daytime_from_string_custom_format(self):
        yaml_str = """time: '2:30 PM'
format: '%I:%M %p'"""
        daytime = daytime_from_yaml(YamlReader(yaml_str))
        self.assertEqual(daytime, DayTime(14, 30, 0))

    # ---------- Error cases ----------

    def test_daytime_invalid_string_format_raises(self):
        yaml_str = """time: 'not-a-time'"""
        with self.assertRaises(YamlFormatError):
            daytime_from_yaml(YamlReader(yaml_str))


class TestTimeFromYamlWithDayTime(unittest.TestCase):
    # ---------- Construction from Day and DayTime ----------

    def test_time_from_day_and_daytime(self):
        yaml_str = """
date:
  year: 2025
  month: 10
  day: 24
daytime:
  hour: 14
  minute: 30
  second: 0
"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 30, 0))

    def test_time_from_day_and_daytime_with_strings(self):
        yaml_str = """
date:
  date: '2025-10-24'
daytime:
  time: '14:30:00'
"""
        time = time_from_yaml(YamlReader(yaml_str))
        self.assertEqual(time, Time(2025, 10, 24, 14, 30, 0))


if __name__ == "__main__":
    unittest.main()
