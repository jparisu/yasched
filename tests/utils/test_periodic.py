import unittest

from yasched.timing.Periodic import Periodic
from yasched.timing.Time import Time
from yasched.timing.TimeSlot import TimeSlot


class TestPeriodic(unittest.TestCase):
    # ---------- Construction & Basics ----------

    def test_init_valid(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 5, 9, 0, 0), Time(2025, 1, 5, 10, 0, 0))
        reps = [Time(1970, 1, 2, 0, 0, 0)]  # Daily
        periodic = Periodic(start, end, reps)
        self.assertEqual(periodic.start, start)
        self.assertEqual(periodic.end, end)
        self.assertEqual(len(periodic.repetitions), 1)

    # ---------- Alternate Constructors ----------

    def test_from_daily(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 5, 9, 0, 0), Time(2025, 1, 5, 10, 0, 0))
        periodic = Periodic.from_daily(start, end, interval_days=1)
        self.assertEqual(periodic.start, start)
        self.assertEqual(periodic.end, end)
        self.assertEqual(len(periodic.repetitions), 1)

    def test_from_weekly(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 12, 31, 9, 0, 0), Time(2025, 12, 31, 10, 0, 0))
        periodic = Periodic.from_weekly(start, end, interval_weeks=1)
        self.assertEqual(periodic.start, start)
        self.assertEqual(periodic.end, end)
        self.assertEqual(len(periodic.repetitions), 1)

    def test_from_count(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        interval = Time(1970, 1, 2, 0, 0, 0)  # Daily
        periodic = Periodic.from_count(start, interval, 10)
        self.assertEqual(periodic.start, start)
        self.assertEqual(len(periodic.repetitions), 1)
        # The end should be 9 days after start (10 occurrences total)
        self.assertEqual(periodic.end.start.day.day, 10)

    # ---------- Methods ----------

    def test_get_occurrences(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 5, 9, 0, 0), Time(2025, 1, 5, 10, 0, 0))
        reps = [Time(1970, 1, 2, 0, 0, 0)]  # Daily
        periodic = Periodic(start, end, reps)
        occurrences = periodic.get_occurrences()
        self.assertEqual(len(occurrences), 5)
        # Check first and last
        self.assertEqual(occurrences[0].start, Time(2025, 1, 1, 9, 0, 0))
        self.assertEqual(occurrences[4].start, Time(2025, 1, 5, 9, 0, 0))

    def test_count_occurrences(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 5, 9, 0, 0), Time(2025, 1, 5, 10, 0, 0))
        reps = [Time(1970, 1, 2, 0, 0, 0)]  # Daily
        periodic = Periodic(start, end, reps)
        self.assertEqual(periodic.count_occurrences(), 5)

    def test_get_occurrences_with_multiple_days_interval(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 10, 9, 0, 0), Time(2025, 1, 10, 10, 0, 0))
        reps = [Time(1970, 1, 3, 0, 0, 0)]  # Every 2 days
        periodic = Periodic(start, end, reps)
        occurrences = periodic.get_occurrences()
        # Should have occurrences on Jan 1, 3, 5, 7, 9
        self.assertEqual(len(occurrences), 5)
        self.assertEqual(occurrences[0].start.day.day, 1)
        self.assertEqual(occurrences[1].start.day.day, 3)
        self.assertEqual(occurrences[2].start.day.day, 5)

    # ---------- Representation ----------

    def test_str(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
        reps = [Time(1970, 1, 2, 0, 0, 0)]
        periodic = Periodic(start, end, reps)
        s = str(periodic)
        self.assertIn("Periodic", s)
        self.assertIn("repetitions=1", s)

    def test_repr_unambiguous(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
        reps = [Time(1970, 1, 2, 0, 0, 0)]
        periodic = Periodic(start, end, reps)
        r = repr(periodic)
        self.assertIn("Periodic", r)

    # ---------- Comparisons ----------

    def test_equality(self):
        start = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
        reps = [Time(1970, 1, 2, 0, 0, 0)]
        p1 = Periodic(start, end, reps)
        p2 = Periodic(start, end, reps)
        self.assertTrue(p1 == p2)

    def test_equality_different_false(self):
        start1 = TimeSlot(Time(2025, 1, 1, 9, 0, 0), Time(2025, 1, 1, 10, 0, 0))
        start2 = TimeSlot(Time(2025, 1, 2, 9, 0, 0), Time(2025, 1, 2, 10, 0, 0))
        end = TimeSlot(Time(2025, 1, 31, 9, 0, 0), Time(2025, 1, 31, 10, 0, 0))
        reps = [Time(1970, 1, 2, 0, 0, 0)]
        p1 = Periodic(start1, end, reps)
        p2 = Periodic(start2, end, reps)
        self.assertFalse(p1 == p2)


if __name__ == "__main__":
    unittest.main()
