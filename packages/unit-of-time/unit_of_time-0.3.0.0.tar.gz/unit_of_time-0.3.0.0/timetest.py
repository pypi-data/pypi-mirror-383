import unittest
from datetime import date, datetime, time, timedelta

from unit_of_time import Year, Quarter, Month, Week, Day, TimeunitKind, Timeunit
from itertools import islice


class Decade(TimeunitKind):
    kind_int = 0
    formatter = "%Ys"

    @classmethod
    def truncate(cls, dt):
        """
        Return the first day of the decade containing the given date.

        Parameters:
                dt (date or datetime): The date to truncate to the start of its decade.

        Returns:
                date: The first day (January 1) of the decade in which `dt` falls.
        """
        return date(max(10 * (dt.year // 10), 1), 1, 1)

    @classmethod
    def get_index_for_date(cls, dt):
        """
        Return the zero-based decade index for the given date.

        Parameters:
            dt (date or datetime): The date for which to compute the decade index.

        Returns:
            int: The decade index equal to the calendar year divided by 10 using integer division (year // 10).
        """
        return dt.year // 10

    @classmethod
    def get_date_from_index(cls, idx):
        """
        Return the start date (January 1) of the decade represented by the given index.

        Parameters:
            idx (int): Decade index; the corresponding year is 10 * idx.

        Returns:
            datetime.date: January 1 of the year 10 * idx.
        """
        return date(max(10 * idx, 1), 1, 1)

    @classmethod
    def last_day(cls, dt):
        """
        Return the last date of the decade that contains the given date.

        Parameters:
            dt (date | datetime): Date or datetime within the target decade.

        Returns:
            date: The last day of that decade.
        """
        dt = cls.truncate(dt)
        return date(dt.year + 10, 1, 1) - timedelta(days=1)


TIME_UNITS = [Decade, Year, Quarter, Month, Week, Day]
START_DATE = date(902, 7, 11)
END_DATE = date(1019, 11, 25)


class TimeUnitTest(unittest.TestCase):
    def date_range_yield(self):
        """
        Yields each date from the start date up to, but not including, the end date.

        Yields:
            datetime.date: The next date in the range from START_DATE to END_DATE.
        """
        dd = (END_DATE - START_DATE).days
        for i in range(dd):
            yield START_DATE + timedelta(days=i)

    def test_to_int(self):
        """
        Comprehensively tests the integrity, uniqueness, ordering, and temporal relationships of all time unit kinds across a historical date range.

        This test validates that each time unit instance:
        - Is uniquely and consistently represented by its integer and string forms.
        - Correctly implements equality, ordering, and membership semantics.
        - Properly defines its temporal boundaries, adjacency, and overlap behavior.
        - Supports correct iteration, ancestor/successor traversal, and inclusion checks for dates and ranges.
        - Raises appropriate errors for invalid membership checks.
        """
        prev_set = set()
        prev_name = set()
        cur_set = set()
        cur_name = set()
        d = [False] * 202101019
        for kind in TIME_UNITS:
            prev_name.update(cur_name)
            prev_set.update(cur_set)
            cur_set = set()
            cur_name = set()
            for dt in self.date_range_yield():
                with self.subTest(kind=kind, dt=dt):
                    tu = kind(dt)
                    self.assertEqual(tu, kind(datetime.combine(dt, time(14, 25))))
                    self.assertEqual(d[tu], tu in cur_set)
                    self.assertEqual(d[tu], int(tu) in cur_set)
                    d[tu] = True
                    cur_set.add(int(tu))
                    cur_name.add(str(tu))
                    self.assertNotIn(int(tu), prev_set)
                    self.assertNotIn(str(tu), prev_name)
                    tu2 = kind(tu.first_date)
                    self.assertEqual(Timeunit(int(tu.kind), tu.dt), tu)
                    self.assertEqual(int(tu), int(tu2))
                    self.assertEqual(repr(tu), repr(tu2))
                    self.assertEqual(kind(tu), tu)
                    self.assertEqual(tu == tu2, str(tu) == str(tu2))
                    self.assertNotEqual(str(tu), str(tu.next))
                    self.assertNotEqual(str(tu.previous), str(tu))
                    self.assertEqual(tu.next.previous, tu)
                    self.assertEqual(tu.previous.next, tu)
                    self.assertLess(tu.previous, tu)
                    self.assertLess(tu, tu.next)
                    self.assertLessEqual(tu.previous, tu)
                    self.assertLessEqual(tu, tu.next)
                    idx = kind.get_index_for_date(tu.dt)
                    self.assertEqual(
                        idx,
                        kind.get_index_for_date(tu.next.dt) - 1,
                    )
                    self.assertEqual(tu.dt, kind.get_date_from_index(idx))
                    self.assertEqual(tu, kind[idx])
                    if dt == tu.first_date:
                        for idx2, dt2 in enumerate(tu):
                            self.assertEqual(idx, kind.get_index_for_date(dt2))
                            self.assertEqual(dt2, tu[idx2])
                    self.assertGreater(tu, tu.previous)
                    self.assertGreater(tu.next, tu)
                    self.assertGreaterEqual(tu, tu.previous)
                    self.assertGreaterEqual(tu.next, tu)
                    self.assertLess(int(tu), int(tu.next))
                    self.assertLess(int(tu.previous), int(tu))
                    self.assertLessEqual(tu.dt, tu.last_date)
                    self.assertEqual(TimeunitKind.from_int(int(tu)), tu)
                    self.assertIn(dt, tu)
                    self.assertIn((dt, dt), tu)
                    with self.assertRaises(TypeError):
                        (dt, None) in tu
                    self.assertIn((tu.first_date, tu.last_date), tu)
                    with self.assertRaises(TypeError):
                        self.assertIn(1425, tu)
                    self.assertIn(dt, list(tu))
                    self.assertEqual(len(tu), len(list(tu)))
                    ance = tu.ancestors
                    self.assertEqual(tu.previous, next(ance))
                    self.assertEqual(tu.previous.previous, next(ance))
                    succ = tu.successors
                    self.assertEqual(tu.next, next(succ))
                    self.assertEqual(tu.next.next, next(succ))
                    self.assertEqual(tu, tu)
                    self.assertLessEqual(tu, tu)
                    self.assertGreaterEqual(tu, tu)
                    self.assertIn(tu, tu)
                    self.assertNotIn(dt, tu.next)
                    self.assertNotIn(dt, tu.previous)
                    self.assertNotIn(tu, tu.next)
                    self.assertEqual(tu.previous, kind.get_previous(tu))
                    self.assertEqual(tu.next, kind.get_next(tu))
                    self.assertNotIn(tu, tu.previous)
                    self.assertNotIn(tu.previous, tu)
                    self.assertNotIn(tu.next, tu)
                    self.assertTrue(tu.overlaps_with(tu))
                    self.assertFalse(tu.next.overlaps_with(tu))
                    self.assertFalse(tu.previous.overlaps_with(tu))
                    self.assertFalse(tu.overlaps_with(tu.next))
                    self.assertFalse(tu.overlaps_with(tu.previous))
                    self.assertEqual(tu, tu << 0)
                    self.assertEqual(tu, tu >> 0)
                    self.assertEqual(tu, 0 >> tu)
                    self.assertEqual(tu, 0 << tu)
                    self.assertEqual(tu.next.next.next, tu << 3)
                    self.assertEqual(tu.next.next.next, tu >> -3)
                    self.assertEqual(tu.next.next.next, 3 >> tu)
                    self.assertEqual(tu.next.next.next, -3 << tu)
                    self.assertEqual(tu.previous.previous.previous, tu << -3)
                    self.assertEqual(tu.previous.previous.previous, tu >> 3)
                    self.assertEqual(tu.previous.previous.previous, -3 >> tu)
                    self.assertEqual(tu.previous.previous.previous, 3 << tu)
                    self.assertLess(tu.last_date, tu.next.first_date)
                    self.assertLess(tu.previous.last_date, tu.first_date)
                    self.assertEqual(
                        (tu.next.first_date - tu.last_date), timedelta(days=1)
                    )
                    self.assertEqual(
                        (tu.first_date - tu.previous.last_date), timedelta(days=1)
                    )

    def test_repr(self):
        self.assertEqual("Week", repr(Week))
        self.assertEqual("Week[102123:105341:]", repr(Week[102123:105341:]))

    def test_hierarchy(self):
        """
        Test hierarchical relationships between time unit kinds for correct ordering, duration, and overlap.

        Verifies that for each pair of coarser (superkind) and finer (kind) time units:
        - The finer unit is shorter in duration than the coarser unit.
        - Integer representations of adjacent units are ordered correctly.
        - Units of different kinds are not equal by value, string, or representation.
        - Units of different kinds overlap temporally as expected.
        """
        for i, superkind in enumerate(TIME_UNITS, 1):
            for kind in TIME_UNITS[i:]:
                self.assertLess(superkind, kind)
                for dt in self.date_range_yield():
                    with self.subTest(superkind=superkind, kind=kind, dt=dt):
                        stu = superkind(dt)
                        tu = kind(dt)
                        self.assertLess(len(tu), len(stu))
                        self.assertLess(int(stu.previous), int(tu))
                        self.assertLess(int(tu), int(stu.next))
                        self.assertNotEqual(stu, tu)
                        self.assertNotEqual(str(stu), str(tu))
                        self.assertNotEqual(repr(stu), repr(tu))
                        self.assertNotEqual(int(stu), int(tu))
                        self.assertTrue(stu.overlaps_with(tu))
                        self.assertTrue(tu.overlaps_with(stu))

    def test_kinds(self):
        """
        Test the identity, equality, and ordering properties of time unit kinds.

        Verifies that each time unit kind is equal to itself and its integer identifier, tracks membership in a set and a boolean list, and checks that kinds are ordered by increasing granularity.
        """
        seen = set()
        d = [False] * 10
        for i, kind in enumerate(TIME_UNITS, 1):
            self.assertEqual(kind, kind)
            self.assertEqual(kind, kind.kind_int)
            self.assertEqual(kind.kind_int, kind)
            self.assertEqual(d[kind], kind in seen)
            self.assertEqual(kind.get_index_for_date(date.min), 0)
            d[kind] = True
            self.assertEqual(list(kind[10:110:10][5:9:2]), list(kind[60:100:20]))
            self.assertEqual(list(islice(kind, 3)), list(kind[:3]))
            self.assertNotIn(kind, seen)
            seen.add(kind)
            for kind2 in TIME_UNITS[i:]:
                self.assertLess(kind, kind2)


if __name__ == "__main__":
    unittest.main()
