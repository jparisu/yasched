import unittest
from datetime import date

from yasched.timing.Day import Day


class TestDay(unittest.TestCase):
    # ---------- Construction & Basics ----------

    def test_init_valid(self):
        d = Day(2025, 10, 24)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 10)
        self.assertEqual(d.day, 24)
        self.assertEqual(str(d), "2025-10-24")
        self.assertEqual(repr(d), "Day(2025, 10, 24)")

    def test_init_invalid_raises(self):
        with self.assertRaises(ValueError):
            Day(2025, 2, 30)  # invalid date

    def test_slots_restrict_attributes(self):
        d = Day(2025, 1, 1)
        with self.assertRaises(AttributeError):
            d.foo = "bar"  # __slots__ prevents this

    # ---------- Alternate Constructors ----------

    def test_today(self):
        # Just verifies consistency with system's date at runtime
        today = date.today()
        d = Day.today()
        self.assertEqual(d.year, today.year)
        self.assertEqual(d.month, today.month)
        self.assertEqual(d.day, today.day)

    def test_from_string_default_iso(self):
        d = Day.from_string("2025-10-24")
        self.assertEqual((d.year, d.month, d.day), (2025, 10, 24))
        self.assertEqual(str(d), "2025-10-24")

    def test_from_string_custom_format(self):
        d = Day.from_string("24/10/2025", fmt="%d/%m/%Y")
        self.assertEqual((d.year, d.month, d.day), (2025, 10, 24))

    def test_from_string_invalid_raises(self):
        with self.assertRaises(ValueError):
            Day.from_string("not-a-date")

    def test_from_date(self):
        base = date(2025, 10, 24)
        d = Day.from_date(base)
        self.assertEqual(d.to_date(), base)

    # ---------- Representation ----------

    def test_str_isoformat(self):
        d = Day(2025, 1, 9)
        self.assertEqual(str(d), "2025-01-09")

    def test_repr_unambiguous(self):
        d = Day(1999, 12, 31)
        self.assertEqual(repr(d), "Day(1999, 12, 31)")

    # ---------- Accessors ----------

    def test_accessors(self):
        d = Day(2000, 2, 29)
        self.assertEqual(d.year, 2000)
        self.assertEqual(d.month, 2)
        self.assertEqual(d.day, 29)

    # ---------- Arithmetic ----------

    def test_add_days_positive(self):
        d = Day(2025, 10, 24)
        d2 = d.add_days(7)
        self.assertEqual(str(d2), "2025-10-31")
        # immutability behavior: returns new instance
        self.assertIsNot(d, d2)

    def test_add_days_negative(self):
        d = Day(2025, 10, 24)
        d2 = d.add_days(-10)
        self.assertEqual(str(d2), "2025-10-14")

    def test_add_days_cross_month(self):
        d = Day(2025, 1, 30)
        self.assertEqual(str(d.add_days(2)), "2025-02-01")

    def test_add_days_cross_year(self):
        d = Day(2024, 12, 31)
        self.assertEqual(str(d.add_days(1)), "2025-01-01")

    def test_add_days_leap_year_forward(self):
        # 2024 is a leap year; Feb 28 + 1 day -> Feb 29
        d = Day(2024, 2, 28)
        self.assertEqual(str(d.add_days(1)), "2024-02-29")

    def test_add_days_leap_year_backward(self):
        d = Day(2024, 3, 1)
        self.assertEqual(str(d.add_days(-1)), "2024-02-29")

    # ---------- Comparisons ----------

    def test_equality(self):
        a = Day(2025, 10, 24)
        b = Day(2025, 10, 24)
        c = Day(2025, 10, 25)
        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == "2025-10-24")  # non-Day -> False per __eq__

    def test_ordering_basic(self):
        a = Day(2025, 10, 24)
        b = Day(2025, 10, 25)
        self.assertTrue(a < b)
        self.assertTrue(a <= b)
        self.assertTrue(b > a)
        self.assertTrue(b >= a)
        self.assertTrue(a <= Day(2025, 10, 24))
        self.assertTrue(a >= Day(2025, 10, 24))

    def test_ordering_across_boundaries(self):
        a = Day(2024, 12, 31)
        b = Day(2025, 1, 1)
        c = Day(2025, 1, 2)
        self.assertTrue(a < b < c)
        self.assertTrue(c > b > a)

    def test_ordering_with_non_day_returns_notimplemented(self):
        # Access the special methods directly to assert NotImplemented
        a = Day(2025, 1, 1)
        self.assertIs(Day.__lt__(a, "x"), NotImplemented)
        self.assertIs(Day.__le__(a, 123), NotImplemented)
        self.assertIs(Day.__gt__(a, object()), NotImplemented)
        self.assertIs(Day.__ge__(a, None), NotImplemented)

    def test_sorting(self):
        seq = [Day(2025, 1, 3), Day(2024, 12, 31), Day(2025, 1, 1)]
        self.assertEqual(sorted(seq), [Day(2024, 12, 31), Day(2025, 1, 1), Day(2025, 1, 3)])

    # ---------- Interop ----------

    def test_to_date(self):
        d = Day(2025, 10, 24)
        self.assertIsInstance(d.to_date(), date)
        self.assertEqual(d.to_date(), date(2025, 10, 24))

    # ---------- New methods ----------

    def test_to_string_default(self):
        d = Day(2025, 10, 24)
        self.assertEqual(d.to_string(), "2025-10-24")

    def test_to_string_custom_format(self):
        d = Day(2025, 10, 24)
        self.assertEqual(d.to_string("%d/%m/%Y"), "24/10/2025")
        self.assertEqual(d.to_string("%B %d, %Y"), "October 24, 2025")

    def test_add_operator_int(self):
        d = Day(2025, 10, 24)
        d2 = d + 7
        self.assertEqual(str(d2), "2025-10-31")
        self.assertIsNot(d, d2)

    def test_add_operator_negative(self):
        d = Day(2025, 10, 24)
        d2 = d + (-7)
        self.assertEqual(str(d2), "2025-10-17")


if __name__ == "__main__":
    unittest.main()
