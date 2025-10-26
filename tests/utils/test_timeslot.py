import unittest

from yasched.timing.Time import Time
from yasched.timing.TimeSlot import TimeSlot


class TestTimeSlot(unittest.TestCase):
    # ---------- Construction & Basics ----------

    def test_init_valid(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end = Time(2025, 10, 24, 16, 0, 0)
        slot = TimeSlot(start, end)
        self.assertEqual(slot.start, start)
        self.assertEqual(slot.end, end)
        self.assertEqual(str(slot), "2025-10-24 14:00:00 - 2025-10-24 16:00:00")
        self.assertEqual(repr(slot), "TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))")

    # ---------- Alternate Constructors ----------

    def test_from_duration(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        # Duration: 2 hours (1970, 1, 1 = epoch day 1, so just time components)
        duration = Time(1970, 1, 1, 2, 0, 0)
        slot = TimeSlot.from_duration(start, duration)
        self.assertEqual(slot.start, start)
        self.assertEqual(str(slot.end), "2025-10-24 16:00:00")

    def test_from_duration_zero(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        # Zero duration (epoch = 1970-01-01 00:00:00)
        duration = Time(1970, 1, 1, 0, 0, 0)
        slot = TimeSlot.from_duration(start, duration)
        self.assertEqual(slot.start, start)
        self.assertEqual(slot.end, start)

    # ---------- Methods ----------

    def test_duration(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end = Time(2025, 10, 24, 16, 0, 0)
        slot = TimeSlot(start, end)
        self.assertEqual(slot.duration(), 7200)  # 2 hours = 7200 seconds

    def test_duration_zero(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        slot = TimeSlot(start, start)
        self.assertEqual(slot.duration(), 0)

    def test_duration_negative(self):
        start = Time(2025, 10, 24, 16, 0, 0)
        end = Time(2025, 10, 24, 14, 0, 0)
        slot = TimeSlot(start, end)
        self.assertEqual(slot.duration(), -7200)  # negative duration

    # ---------- Representation ----------

    def test_str(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end = Time(2025, 10, 24, 16, 0, 0)
        slot = TimeSlot(start, end)
        self.assertEqual(str(slot), "2025-10-24 14:00:00 - 2025-10-24 16:00:00")

    def test_repr_unambiguous(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end = Time(2025, 10, 24, 16, 0, 0)
        slot = TimeSlot(start, end)
        self.assertEqual(repr(slot), "TimeSlot(Time(2025, 10, 24, 14, 0, 0), Time(2025, 10, 24, 16, 0, 0))")

    def test_to_string_default(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end = Time(2025, 10, 24, 16, 0, 0)
        slot = TimeSlot(start, end)
        self.assertEqual(slot.to_string(), "2025-10-24 14:00:00 - 2025-10-24 16:00:00")

    def test_to_string_custom_format(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end = Time(2025, 10, 24, 16, 0, 0)
        slot = TimeSlot(start, end)
        self.assertEqual(slot.to_string("%H:%M"), "14:00 - 16:00")

    # ---------- Comparisons ----------

    def test_equality(self):
        start1 = Time(2025, 10, 24, 14, 0, 0)
        end1 = Time(2025, 10, 24, 16, 0, 0)
        start2 = Time(2025, 10, 24, 14, 0, 0)
        end2 = Time(2025, 10, 24, 16, 0, 0)
        start3 = Time(2025, 10, 24, 15, 0, 0)
        end3 = Time(2025, 10, 24, 17, 0, 0)

        a = TimeSlot(start1, end1)
        b = TimeSlot(start2, end2)
        c = TimeSlot(start3, end3)

        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == "slot")  # non-TimeSlot -> False

    def test_ordering_basic(self):
        start1 = Time(2025, 10, 24, 14, 0, 0)
        end1 = Time(2025, 10, 24, 16, 0, 0)
        start2 = Time(2025, 10, 24, 15, 0, 0)
        end2 = Time(2025, 10, 24, 17, 0, 0)

        a = TimeSlot(start1, end1)
        b = TimeSlot(start2, end2)

        self.assertTrue(a < b)
        self.assertTrue(a <= b)
        self.assertTrue(b > a)
        self.assertTrue(b >= a)

    def test_ordering_same_start(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end1 = Time(2025, 10, 24, 16, 0, 0)
        end2 = Time(2025, 10, 24, 17, 0, 0)

        a = TimeSlot(start, end1)
        b = TimeSlot(start, end2)

        # Since comparison is based on start time, they should be equal
        self.assertFalse(a < b)
        self.assertTrue(a <= b)
        self.assertFalse(b > a)
        self.assertTrue(b >= a)

    def test_ordering_with_non_timeslot_raises_typeerror(self):
        start = Time(2025, 10, 24, 14, 0, 0)
        end = Time(2025, 10, 24, 16, 0, 0)
        slot = TimeSlot(start, end)

        with self.assertRaises(TypeError):
            slot < "x"
        with self.assertRaises(TypeError):
            slot <= 123
        with self.assertRaises(TypeError):
            slot > object()
        with self.assertRaises(TypeError):
            slot >= None

    def test_sorting(self):
        start1 = Time(2025, 10, 24, 15, 0, 0)
        end1 = Time(2025, 10, 24, 17, 0, 0)
        start2 = Time(2025, 10, 24, 13, 0, 0)
        end2 = Time(2025, 10, 24, 15, 0, 0)
        start3 = Time(2025, 10, 24, 14, 0, 0)
        end3 = Time(2025, 10, 24, 16, 0, 0)

        slots = [
            TimeSlot(start1, end1),
            TimeSlot(start2, end2),
            TimeSlot(start3, end3),
        ]
        sorted_slots = sorted(slots)

        self.assertEqual(sorted_slots[0].start, start2)
        self.assertEqual(sorted_slots[1].start, start3)
        self.assertEqual(sorted_slots[2].start, start1)


if __name__ == "__main__":
    unittest.main()
