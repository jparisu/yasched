import unittest
from datetime import datetime

from yasched.timing.Day import Day
from yasched.timing.Time import Time


class TestTime(unittest.TestCase):
    # ---------- Construction & Basics ----------

    def test_init_valid(self):
        t = Time(2025, 10, 24, 14, 30, 0)
        self.assertEqual(t.day, Day(2025, 10, 24))
        self.assertEqual(t.hour, 14)
        self.assertEqual(t.minute, 30)
        self.assertEqual(t.second, 0)
        self.assertEqual(str(t), "2025-10-24 14:30:00")
        self.assertEqual(repr(t), "Time(2025, 10, 24, 14, 30, 0)")

    def test_init_defaults(self):
        t = Time(2025, 10, 24)
        self.assertEqual(t.hour, 0)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)

    def test_init_invalid_raises(self):
        with self.assertRaises(ValueError):
            Time(2025, 2, 30, 14, 30, 0)  # invalid date
        with self.assertRaises(ValueError):
            Time(2025, 10, 24, 25, 0, 0)  # invalid hour

    # ---------- Alternate Constructors ----------

    def test_now(self):
        # Just verifies it returns a Time instance
        t = Time.now()
        self.assertIsInstance(t, Time)
        self.assertIsInstance(t.day, Day)

    def test_from_string_default(self):
        t = Time.from_string("2025-10-24 14:30:00")
        self.assertEqual((t.day.year, t.day.month, t.day.day), (2025, 10, 24))
        self.assertEqual((t.hour, t.minute, t.second), (14, 30, 0))

    def test_from_string_custom_format(self):
        t = Time.from_string("24/10/2025 14:30", fmt="%d/%m/%Y %H:%M")
        self.assertEqual((t.day.year, t.day.month, t.day.day), (2025, 10, 24))
        self.assertEqual((t.hour, t.minute), (14, 30))

    def test_from_string_invalid_raises(self):
        with self.assertRaises(ValueError):
            Time.from_string("not-a-datetime")

    def test_from_datetime(self):
        dt = datetime(2025, 10, 24, 14, 30, 0)
        t = Time.from_datetime(dt)
        self.assertEqual(t.to_datetime(), dt)

    # ---------- Representation ----------

    def test_str(self):
        t = Time(2025, 1, 9, 8, 5, 3)
        self.assertEqual(str(t), "2025-01-09 08:05:03")

    def test_repr_unambiguous(self):
        t = Time(1999, 12, 31, 23, 59, 59)
        self.assertEqual(repr(t), "Time(1999, 12, 31, 23, 59, 59)")

    def test_to_string_default(self):
        t = Time(2025, 10, 24, 14, 30, 0)
        self.assertEqual(t.to_string(), "2025-10-24 14:30:00")

    def test_to_string_custom_format(self):
        t = Time(2025, 10, 24, 14, 30, 0)
        self.assertEqual(t.to_string("%d/%m/%Y %H:%M"), "24/10/2025 14:30")
        self.assertEqual(t.to_string("%H:%M:%S"), "14:30:00")

    # ---------- Accessors ----------

    def test_accessors(self):
        t = Time(2025, 10, 24, 14, 30, 45)
        self.assertEqual(t.day, Day(2025, 10, 24))
        self.assertEqual(t.hour, 14)
        self.assertEqual(t.minute, 30)
        self.assertEqual(t.second, 45)

    # ---------- Arithmetic ----------

    def test_add_seconds_positive(self):
        t = Time(2025, 10, 24, 14, 30, 0)
        t2 = t + 3600  # Add 1 hour
        self.assertEqual(str(t2), "2025-10-24 15:30:00")
        self.assertIsNot(t, t2)

    def test_add_seconds_negative(self):
        t = Time(2025, 10, 24, 14, 30, 0)
        t2 = t + (-3600)  # Subtract 1 hour
        self.assertEqual(str(t2), "2025-10-24 13:30:00")

    def test_add_seconds_cross_day(self):
        t = Time(2025, 10, 24, 23, 30, 0)
        t2 = t + 3600  # Add 1 hour, should go to next day
        self.assertEqual(str(t2), "2025-10-25 00:30:00")

    def test_add_negative_seconds(self):
        t = Time(2025, 10, 24, 14, 30, 0)
        t2 = t + (-7200)  # Subtract 2 hours
        self.assertEqual(str(t2), "2025-10-24 12:30:00")

    def test_add_time_to_time(self):
        # Test adding Time objects - other Time is interpreted as duration
        t1 = Time(2025, 1, 1, 10, 30, 45)
        # Time(1970, 1, 2, 5, 15, 30) = 1 day + 5 hours + 15 minutes + 30 seconds
        t2 = Time(1970, 1, 2, 5, 15, 30)
        result = t1 + t2
        self.assertEqual(result, Time(2025, 1, 2, 15, 46, 15))

    def test_add_time_simple(self):
        t1 = Time(2025, 1, 1, 10, 0, 0)
        # Time(1970, 1, 1, 2, 30, 0) = 0 days + 2 hours + 30 minutes
        t2 = Time(1970, 1, 1, 2, 30, 0)
        result = t1 + t2
        self.assertEqual(result, Time(2025, 1, 1, 12, 30, 0))

    # ---------- Comparisons ----------

    def test_equality(self):
        a = Time(2025, 10, 24, 14, 30, 0)
        b = Time(2025, 10, 24, 14, 30, 0)
        c = Time(2025, 10, 24, 14, 30, 1)
        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == "2025-10-24 14:30:00")  # non-Time -> False

    def test_ordering_basic(self):
        a = Time(2025, 10, 24, 14, 30, 0)
        b = Time(2025, 10, 24, 15, 30, 0)
        self.assertTrue(a < b)
        self.assertTrue(a <= b)
        self.assertTrue(b > a)
        self.assertTrue(b >= a)
        self.assertTrue(a <= Time(2025, 10, 24, 14, 30, 0))
        self.assertTrue(a >= Time(2025, 10, 24, 14, 30, 0))

    def test_ordering_across_days(self):
        a = Time(2025, 10, 24, 23, 59, 59)
        b = Time(2025, 10, 25, 0, 0, 0)
        self.assertTrue(a < b)
        self.assertTrue(b > a)

    def test_ordering_with_non_time_returns_notimplemented(self):
        t = Time(2025, 1, 1, 0, 0, 0)
        self.assertIs(Time.__lt__(t, "x"), NotImplemented)
        self.assertIs(Time.__le__(t, 123), NotImplemented)
        self.assertIs(Time.__gt__(t, object()), NotImplemented)
        self.assertIs(Time.__ge__(t, None), NotImplemented)

    def test_sorting(self):
        seq = [
            Time(2025, 1, 3, 10, 0, 0),
            Time(2024, 12, 31, 23, 59, 59),
            Time(2025, 1, 1, 0, 0, 0),
        ]
        sorted_seq = sorted(seq)
        self.assertEqual(
            sorted_seq,
            [
                Time(2024, 12, 31, 23, 59, 59),
                Time(2025, 1, 1, 0, 0, 0),
                Time(2025, 1, 3, 10, 0, 0),
            ],
        )

    # ---------- Interop ----------

    def test_to_datetime(self):
        t = Time(2025, 10, 24, 14, 30, 0)
        self.assertIsInstance(t.to_datetime(), datetime)
        self.assertEqual(t.to_datetime(), datetime(2025, 10, 24, 14, 30, 0))


if __name__ == "__main__":
    unittest.main()
