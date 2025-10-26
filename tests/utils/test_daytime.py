import unittest
from datetime import time

from yasched.timing.DayTime import DayTime


class TestDayTime(unittest.TestCase):
    # ---------- Construction & Basics ----------

    def test_init_valid(self):
        dt = DayTime(14, 30, 0)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)
        self.assertEqual(dt.second, 0)
        self.assertEqual(str(dt), "14:30:00")
        self.assertEqual(repr(dt), "DayTime(14, 30, 0)")

    def test_init_defaults(self):
        dt = DayTime()
        self.assertEqual(dt.hour, 0)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)

    def test_init_invalid_raises(self):
        with self.assertRaises(ValueError):
            DayTime(25, 0, 0)  # invalid hour
        with self.assertRaises(ValueError):
            DayTime(0, 60, 0)  # invalid minute

    # ---------- Alternate Constructors ----------

    def test_from_string_default(self):
        dt = DayTime.from_string("14:30:00")
        self.assertEqual((dt.hour, dt.minute, dt.second), (14, 30, 0))

    def test_from_string_custom_format(self):
        dt = DayTime.from_string("2:30 PM", fmt="%I:%M %p")
        self.assertEqual((dt.hour, dt.minute), (14, 30))

    def test_from_string_invalid_raises(self):
        with self.assertRaises(ValueError):
            DayTime.from_string("not-a-time")

    def test_from_time(self):
        t = time(14, 30, 0)
        dt = DayTime.from_time(t)
        self.assertEqual(dt.to_time(), t)

    # ---------- Representation ----------

    def test_str(self):
        dt = DayTime(8, 5, 3)
        self.assertEqual(str(dt), "08:05:03")

    def test_repr_unambiguous(self):
        dt = DayTime(23, 59, 59)
        self.assertEqual(repr(dt), "DayTime(23, 59, 59)")

    def test_to_string_default(self):
        dt = DayTime(14, 30, 0)
        self.assertEqual(dt.to_string(), "14:30:00")

    def test_to_string_custom_format(self):
        dt = DayTime(14, 30, 0)
        self.assertEqual(dt.to_string("%I:%M %p"), "02:30 PM")

    # ---------- Accessors ----------

    def test_accessors(self):
        dt = DayTime(14, 30, 45)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)
        self.assertEqual(dt.second, 45)

    def test_to_seconds(self):
        self.assertEqual(DayTime(1, 0, 0).to_seconds(), 3600)
        self.assertEqual(DayTime(0, 1, 30).to_seconds(), 90)
        self.assertEqual(DayTime(0, 0, 0).to_seconds(), 0)

    # ---------- Comparisons ----------

    def test_equality(self):
        a = DayTime(14, 30, 0)
        b = DayTime(14, 30, 0)
        c = DayTime(14, 30, 1)
        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == "14:30:00")  # non-DayTime -> False

    def test_ordering_basic(self):
        a = DayTime(14, 30, 0)
        b = DayTime(15, 30, 0)
        self.assertTrue(a < b)
        self.assertTrue(a <= b)
        self.assertTrue(b > a)
        self.assertTrue(b >= a)
        self.assertTrue(a <= DayTime(14, 30, 0))
        self.assertTrue(a >= DayTime(14, 30, 0))

    def test_sorting(self):
        seq = [DayTime(15, 0, 0), DayTime(10, 0, 0), DayTime(12, 30, 0)]
        sorted_seq = sorted(seq)
        self.assertEqual(sorted_seq, [DayTime(10, 0, 0), DayTime(12, 30, 0), DayTime(15, 0, 0)])

    # ---------- Interop ----------

    def test_to_time(self):
        dt = DayTime(14, 30, 0)
        self.assertIsInstance(dt.to_time(), time)
        self.assertEqual(dt.to_time(), time(14, 30, 0))


if __name__ == "__main__":
    unittest.main()
