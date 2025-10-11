import math
from abc import abstractmethod
from datetime import date, datetime, timedelta

ONE_DAY = timedelta(days=1)


def date_from_int(val, div=1):
    val //= div
    d = val % 100
    val //= 100
    m = val % 100
    val //= 100
    return date(val, m, d)


def date_to_int(val, mul=1):
    """
    Encode a date as an integer in YYYYMMDD form, optionally scaled by a multiplier.

    Parameters:
        val (date): The date to encode.
        mul (int): Multiplier applied to the encoded integer (default 1).

    Returns:
        int: The value (YYYYMMDD) multiplied by `mul`.
    """
    return mul * (val.year * 10000 + val.month * 100 + val.day)


class IndexableMixin:
    def __getitem__(self, key):
        """
        Map an integer index or slice to the corresponding item(s) produced by _from_index.

        Parameters:
            key (int | slice): An index or slice as used on sequences; negative indices and slice semantics follow Python's range indexing behavior.

        Returns:
            The single value produced by `self._from_index(index)` when `key` selects one index, or a generator that yields `self._from_index(index)` for each index in the selected range.
        """
        idc = range(len(self))[key]
        if isinstance(idc, int):
            return self._from_index(idc)
        else:
            return SlicedProxy(self, key)


class SlicedProxy(IndexableMixin):
    def __init__(self, parent, _slice: slice):
        self.parent = parent
        self._slice = _slice

    @property
    def range_object(self):
        return range(len(self.parent))[self._slice]

    def __iter__(self):
        for idx in self.range_object:
            yield self.parent[idx]

    def _from_index(self, idx):
        return self.parent[self.range_object[idx]]

    def __len__(self):
        return len(self.range_object)

    def __repr__(self):
        s = self._slice
        s = ":".join(
            str(si) if si is not None else "" for si in (s.start, s.stop, s.step)
        )
        return f"{self.parent!r}[{s}]"


class TimeunitKindMeta(IndexableMixin, type):
    kind_int = None
    formatter = None
    _pre_registered = []
    _registered = None
    _multiplier = None
    first_date = date.min
    last_date = date.max

    def __init__(cls, name, bases, attrs):
        """
        Initialize the metaclass for a TimeunitKind subclass and register the class if it defines a kind identifier.

        If the created class has a non-None `kind_int`, the class is appended to TimeunitKindMeta._pre_registered and the cached registry and multiplier on TimeunitKindMeta are cleared (set to None) so they will be rebuilt on next access. This method has the side effect of mutating TimeunitKindMeta's class-level registration caches.
        """
        super().__init__(name, bases, attrs)
        if cls.kind_int is not None:
            TimeunitKindMeta._pre_registered.append(cls)
            TimeunitKindMeta._registered = None
            TimeunitKindMeta._multiplier = None

    def _from_index(cls, idx):
        """
        Create a time-unit instance corresponding to the numeric index.

        Parameters:
            idx (int): Numeric index into this kind's sequence (0 corresponds to the unit containing date.min).

        Returns:
            Timeunit: An instance of this kind representing the unit at the given index.
        """
        return cls(cls.get_date_from_index(idx))

    def __repr__(cls):
        return cls.__qualname__

    @property
    def unit_register(self):
        """
        Lazily construct and return the registry that maps each time-unit kind integer to its corresponding TimeunitKind class.

        Only classes with a defined kind_int are included; the mapping is cached on first access and reused thereafter.

        Returns:
            dict[int, type]: Mapping from a kind's integer identifier to the TimeunitKind subclass.
        """
        result = TimeunitKindMeta._registered
        if result is None:
            result = {
                k.kind_int: k
                for k in TimeunitKindMeta._pre_registered
                if k.kind_int is not None
            }
            TimeunitKindMeta._registered = result
        return result

    @property
    def multiplier(cls):
        """
        Compute and return a power-of-ten multiplier sized to encode registered kind integers.

        The returned integer is the smallest power of ten that is greater than or equal to the largest
        `kind_int` among pre-registered Timeunit kinds (with a minimum of 1). The computed value is cached
        on TimeunitKindMeta._multiplier for subsequent accesses.

        Returns:
            int: Power-of-ten multiplier (>= 1) suitable for composing integer encodings with `kind_int`.
        """
        result = TimeunitKindMeta._multiplier
        if result is None:
            result = max(1, *[k.kind_int for k in TimeunitKindMeta._pre_registered])
            result = 10 ** math.ceil(math.log10(result))
            TimeunitKindMeta._multiplier = result
        return result

    def __len__(cls):
        """
        Total number of units of this kind representable within the supported date range.

        Returns:
            int: The count of discrete units (computed as highest index for date.max plus one).
        """
        return cls.get_index_for_date(cls.last_date) + 1

    def __int__(self):
        """
        Provide the integer identifier for this time unit kind.

        Returns:
            int: The kind's integer identifier.
        """
        return self.kind_int

    def __index__(cls):
        return int(cls)

    def __hash__(cls):
        """
        Return the hash value of the time unit, based on its integer encoding.
        """
        return hash(int(cls))

    def __eq__(cls, other):
        """
        Return True if this time unit kind is the same as another kind or matches the
        kind registered for the given integer.

        Parameters:
            other: Another kind instance or an integer representing a registered kind.

        Returns:
            bool: True if both refer to the same time unit kind, otherwise False.
        """
        if isinstance(other, int):
            other = TimeunitKind.unit_register[other]
        return cls is other

    def __call__(cls, dt):
        """
        Creates a `Timeunit` instance of this kind from a given date or `Timeunit`.

        If a `Timeunit` is provided, its date is extracted and used.
        """
        if isinstance(dt, Timeunit):
            dt = dt.dt
        return Timeunit(cls, dt)

    def __lt__(cls, other):
        return cls.kind_int < other.kind_int

    def from_int(cls, val):
        mul = cls.multiplier
        return TimeunitKind.unit_register[val % mul](date_from_int(val, mul))

    def get_previous(cls, dt):
        if isinstance(dt, Timeunit):
            dt = dt.dt
        dt -= timedelta(days=1)
        return cls(dt)

    def last_day(cls, dt):
        """
        Return the last date of the time unit containing the given date.

        Parameters:
                dt (date): The date for which to find the last day of its time unit.

        Returns:
                date: The last date within the same time unit as `dt`.
        """
        return cls._next(dt) - timedelta(days=1)

    def _next(cls, dt):
        """
        Return the first day of the next time unit following the given date.

        Parameters:
                dt (date): The reference date.

        Returns:
                date: The first day of the next time unit.
        """
        return cls.last_day(dt) + timedelta(days=1)

    def get_next(cls, dt):
        """
        Return the next time unit instance of this kind after the given date.

        If a `Timeunit` is provided, its date is used. The returned instance
        represents the time unit immediately following the one containing `dt`.
        """
        if isinstance(dt, Timeunit):
            dt = dt.dt
        return cls(cls._next(cls.truncate(dt)))

    def to_str(cls, dt):
        """
        Format a date using the class's formatter.

        Parameters:
            dt (date | datetime): The date or datetime to format.

        Returns:
            str: String representation of `dt` formatted with `cls.formatter`.
        """
        return dt.strftime(cls.formatter.replace("%Y", f"{dt.year:04d}"))

    @abstractmethod
    def get_index_for_date(cls, dt):
        """
        Compute the unit-specific ordinal index for the given date.

        This base implementation returns `None`; concrete TimeunitKind subclasses override this to map a date to an integer index counting units from date.min.

        Parameters:
            dt (datetime.date | datetime.datetime): Date to convert to an index for this time unit kind.

        Returns:
            int: The zero-based index of the unit containing `dt` relative to `date.min`.
        """

    @abstractmethod
    def get_date_from_index(cls, dt):
        """
        Map an index value for this time unit kind to its corresponding start date.

        Parameters:
                dt (int): Integer index representing the offset of the unit (e.g., number of days/weeks/months/years since date.min).

        Returns:
                date (datetime.date): The start date corresponding to `dt`.
        """

    def __iter__(cls):
        """
        Iterate over every time unit of this kind in chronological order.

        Yields:
            Timeunit: A Timeunit instance for each valid index, from the earliest to the latest.
        """
        for i in range(len(cls)):
            yield cls._from_index(i)

    def truncate(cls, dt):
        """
        Return the date obtained by formatting and parsing `dt` with the kind's formatter, effectively truncating `dt` to the unit's boundary.

        Parameters:
                dt (datetime.date | datetime.datetime): The input date or datetime to truncate.

        Returns:
                datetime.date: The truncated date representing the unit's start as determined by `cls.formatter`.
        """
        return datetime.strptime(cls.to_str(dt), cls.formatter).date()

    def _inner_shift(cls, cur, dt, amount):
        return None

    def _shift(cls, cur, dt, amount):
        new_dt = cls._inner_shift(cur, dt, amount)
        if new_dt is not None:
            return cls(new_dt)
        if amount > 0:
            for _ in range(amount):
                cur = cur.next
            return cur
        elif amount < 0:
            for _ in range(-amount):
                cur = cur.previous
            return cur
        else:
            return cur


class TimeunitKind(metaclass=TimeunitKindMeta):
    kind_int = None
    formatter = None


class Year(TimeunitKind):
    kind_int = 1
    formatter = "%Y"

    @classmethod
    def truncate(cls, dt):
        """
        Return the first day of the year containing the given date.

        Parameters:
            dt (date or datetime): A date or datetime whose year will be used.

        Returns:
            date: A date representing January 1 of dt's year.
        """
        return date(dt.year, 1, 1)

    @classmethod
    def _next(cls, dt):
        """
        Return the first day of the year following the given date.

        Parameters:
                dt (date): A date within the current year.

        Returns:
                date: January 1 of the year after `dt.year`.
        """
        return date(dt.year + 1, 1, 1)

    @classmethod
    def get_index_for_date(cls, dt):
        """
        Compute the year index of a date relative to date.min.

        Parameters:
                dt (date): The date whose year will be indexed.

        Returns:
                index (int): Number of years between dt.year and date.min.year.
        """
        return dt.year - date.min.year

    @classmethod
    def get_date_from_index(cls, idx):
        """
        Map a year index to the corresponding first day of that year.

        Parameters:
            idx (int): Number of years since date.min.year (0 maps to January 1 of date.min.year).

        Returns:
            datetime.date: January 1 of the year at index `idx`.
        """
        return date(idx + date.min.year, 1, 1)

    @classmethod
    def _inner_shift(cls, cur, dt, amount):
        """
        Shift the provided date by a number of years and return the first day of the resulting year.

        Parameters:
            cur: The current Timeunit or index (not used by this implementation).
            dt (datetime.date): The date to shift.
            amount (int): Number of years to shift; may be negative.

        Returns:
            datetime.date: January 1 of the year `dt.year + amount`.
        """
        return date(dt.year + amount, 1, 1)


class Quarter(TimeunitKind):
    kind_int = 3

    @classmethod
    def to_str(cls, dt):
        """
        Return a compact quarter identifier for the given date.

        Parameters:
                dt (date | datetime): The date to format.

        Returns:
                quarter_str (str): A string in the form `YYYYQn` where `n` is the quarter number (1–4).
        """
        return f"{dt.year:04d}Q{(dt.month+2)//3}"

    @classmethod
    def get_index_for_date(cls, dt):
        """
        Compute the 0-based quarter index for a given date relative to date.min.

        Parameters:
            cls: The Quarter class (ignored).
            dt (date): The date to convert into a quarter index.

        Returns:
            int: Quarter index since date.min where each year contributes 4 and quarters are 0..3 based on the month.
        """
        return 4 * (dt.year - date.min.year) + max((dt.month - 1) // 3, 0)

    @classmethod
    def get_date_from_index(cls, idx):
        """
        Convert a quarter index into the first day of that quarter.

        Parameters:
            idx (int): Quarter index where 0 corresponds to year 1, quarter 1; indices increase by one per quarter.

        Returns:
            datetime.date: The date for the first day of the quarter (month = 1, 4, 7, or 10) for the computed year.
        """
        yy = idx // 4
        qq = idx - 4 * yy
        return date(yy + date.min.year, 3 * qq + 1, 1)

    @classmethod
    def truncate(cls, dt):
        """
        Get the first day of the quarter containing the given date.

        Parameters:
            dt (datetime.date | datetime.datetime): The date to truncate.

        Returns:
            datetime.date: The date representing the first day of dt's quarter (month 1, 4, 7, or 10).
        """
        return date(dt.year, 3 * ((dt.month - 1) // 3) + 1, 1)

    @classmethod
    def _inner_shift(cls, cur, dt, amount):
        q_new = dt.year * 4 + amount + (dt.month - 1) // 3
        return date(q_new // 4, 3 * (q_new % 4) + 1, 1)

    @classmethod
    def _next(cls, dt):
        q2 = 3 * (dt.month + 2) // 3 + 1
        if q2 == 13:
            return date(dt.year + 1, 1, 1)
        return date(dt.year, q2, 1)


class Month(TimeunitKind):
    kind_int = 5
    formatter = "%YM%m"

    @classmethod
    def _inner_shift(cls, cur, dt, amount):
        """
        Shift the given date by a number of months and return the first day of the resulting month.

        Parameters:
                dt (date): The base date to shift.
                amount (int): Number of months to shift `dt` by; may be negative.

        Returns:
                result (date): The first day of the month that is `amount` months from `dt`.
        """
        m_new = dt.year * 12 + amount + dt.month - 1
        return date(m_new // 12, m_new % 12 + 1, 1)

    @classmethod
    def get_index_for_date(cls, dt):
        """
        Compute the zero-based month index for a given date measured from date.min.

        Parameters:
            dt (date | datetime): The date to convert into a month index.

        Returns:
            int: Number of months since January of date.min.year (January of date.min.year == 0).
        """
        return 12 * (dt.year - date.min.year) + dt.month - 1

    @classmethod
    def get_date_from_index(cls, idx):
        """
        Map a month index to the date of its first day.

        Parameters:
            idx (int): Month index where 0 corresponds to 0001-01-01; each increment advances one month.

        Returns:
            date: The first day of the month represented by `idx`.
        """
        yy = idx // 12
        mm = (idx % 12) + 1
        return date(yy + date.min.year, mm, 1)

    @classmethod
    def _next(cls, dt):
        """
        Return the first day of the month immediately following the given date.

        Parameters:
            dt (datetime.date): A date whose next-month boundary is requested.

        Returns:
            datetime.date: Date representing the first day of the month after `dt`.
        """
        m2 = dt.month + 1
        if m2 > 12:
            return date(dt.year + 1, 1, 1)
        else:
            return date(dt.year, m2, 1)


class Week(TimeunitKind):
    kind_int = 7
    formatter = "%YW%W"
    last_date = date(9999, 12, 26)

    @classmethod
    def _inner_shift(cls, cur, dt, amount):
        """
        Shift a date by a number of whole weeks and return the resulting date.

        Parameters:
            cur: The current Timeunit instance or kind context (unused by this implementation).
            dt (datetime.date | datetime.datetime): The date to shift; time component, if any, is preserved.
            amount (int): Number of weeks to shift; may be negative to shift backward.

        Returns:
            datetime.date | datetime.datetime: The date obtained by adding `amount * 7` days to `dt`.
        """
        return dt + timedelta(days=7 * amount)

    @classmethod
    def get_index_for_date(cls, dt):
        # date.min has weekday() == 0
        """
        Compute the zero-based week index of a given date relative to date.min (weeks start on Monday).

        Parameters:
            dt (datetime.date | datetime.datetime): The date to index; when a datetime is provided, its date component is used.

        Returns:
            int: Number of whole weeks between date.min (which is a Monday) and `dt`.
        """
        return (dt - date.min).days // 7

    @classmethod
    def get_date_from_index(cls, idx):
        """
        Map a week index to the starting date of that week.

        Parameters:
            idx (int): Week index where 0 corresponds to date.min and each increment advances by one week.

        Returns:
            datetime.date: The date equal to date.min plus 7 * idx days (the start date of the indexed week).
        """
        return date.min + timedelta(days=7 * idx)

    @classmethod
    def truncate(cls, dt):
        """
        Return the Monday (start) of the week containing the given date.

        Parameters:
            dt (datetime.date | datetime.datetime): Date or datetime to truncate to the week's start. If a datetime is provided, its date portion is used.

        Returns:
            datetime.date: Date representing the Monday of the week that contains `dt`.
        """
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt - timedelta(days=dt.weekday())

    @classmethod
    def _next(cls, dt):
        return dt + timedelta(days=7)


class Day(TimeunitKind):
    kind_int = 9
    formatter = "%Y-%m-%d"

    @classmethod
    def get_index_for_date(cls, dt):
        """
        Compute the day-based index of a date relative to date.min.

        Parameters:
            dt (datetime.date | datetime.datetime): The date to convert into an index.

        Returns:
            int: Number of days between `date.min` and `dt`.
        """
        return (dt - date.min).days

    @classmethod
    def get_date_from_index(cls, idx):
        """
        Convert a day index to the corresponding calendar date.

        Parameters:
            idx (int): Number of days since date.min (0 maps to date.min).

        Returns:
            datetime.date: The date that is `idx` days after `date.min`.
        """
        return date.min + timedelta(days=idx)

    @classmethod
    def _inner_shift(cls, cur, dt, amount):
        """
        Shift the given date by a number of days.

        Parameters:
            cls: The Timeunit kind class invoking this method (unused by this implementation).
            cur: The current Timeunit instance that provides context for the shift (unused by this implementation).
            dt (date or datetime): The date to shift.
            amount (int): Number of days to shift `dt` by; may be negative.

        Returns:
            date or datetime: `dt` offset by `amount` days.
        """
        return dt + timedelta(days=amount)

    @classmethod
    def _next(cls, dt):
        """
        Return the start date of the day immediately after the given date.

        Parameters:
            dt (date | datetime): The date or datetime to advance by one day.

        Returns:
            date or datetime: The input advanced by one calendar day.
        """
        return dt + timedelta(days=1)


class Timeunit(IndexableMixin):
    def __init__(self, kind, dt):
        """
        Initialize the Timeunit by resolving the given kind and storing the kind and the unit's start date.

        Parameters:
            kind (int | TimeunitKind): Either an integer key for a registered TimeunitKind or a TimeunitKind class; if an integer is provided it is resolved via the kind registry.
            dt (date | datetime): A date or datetime that will be truncated to the unit's boundary using the kind's truncate method.
        """
        if isinstance(kind, int):
            kind = TimeunitKind.unit_register[kind]
        self.kind = kind
        self.dt = kind.truncate(dt)

    @property
    def previous(self):
        return self.kind.get_previous(self.dt)

    @property
    def first_date(self):
        return self.dt

    @property
    def last_date(self):
        return self.kind.last_day(self.dt)

    @property
    def date_range(self):
        return self.dt, self.last_date

    @property
    def ancestors(self):
        """
        Yields an infinite sequence of preceding time units, starting from the
        previous unit of this instance.

        Each iteration yields the next earlier time unit of the same kind.
        """
        result = self
        while True:
            result = result.previous
            yield result

    @property
    def successors(self):
        """
        Yields successive time units following the current one indefinitely.

        Each yielded value is the next chronological time unit of the same kind.
        """
        result = self
        while True:
            result = result.next
            yield result

    def __len__(self):
        """
        Number of days spanned by this time unit.

        Returns:
            days (int): Number of calendar days from this unit's start date up to (but not including) the start date of the next unit.
        """
        return (self.next.dt - self.dt).days

    def _from_index(self, idx):
        """
        Return a date offset from this unit's start by the given number of days.

        Parameters:
            idx (int): Number of days to add to the unit's start date; may be negative.

        Returns:
            datetime.date: Date equal to the unit's start date shifted by `idx` days.
        """
        return self.dt + timedelta(days=idx)

    def __iter__(self):
        """
        Iterate each calendar day in this time unit from its start up to (but not including) the next unit's start.

        Returns:
            Iterator[date]: Yields each day (as a `date` or `datetime.date`) within the unit's date range.
        """
        dt = self.dt
        end = self.next.dt
        while dt < end:
            yield dt
            dt += ONE_DAY

    def __rshift__(self, other):
        return self << -other

    def __rlshift__(self, other):
        return self >> other

    def __rrshift__(self, other):
        return self << other

    def __lshift__(self, other):
        return self.kind._shift(self, self.dt, other)

    @property
    def next(self):
        return self.kind.get_next(self.dt)

    def __index__(self):
        """
        Return the integer representation of the time unit kind for use in index operations.
        """
        return int(self)

    def __eq__(self, other):
        """
        Return True if this Timeunit is equal to another Timeunit or an integer representation.

        Equality is determined by matching both the kind and the truncated date.
        If `other` is an integer, it is first converted to a Timeunit instance.
        """
        if isinstance(other, int):
            other = TimeunitKind.from_int(other)
        return self.kind == other.kind and self.dt == other.dt

    def __lt__(self, other):
        """
        Return True if this time unit is less than another, based on their integer representations.
        """
        return int(self) < int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __int__(self):
        return date_to_int(self.dt, self.kind.multiplier) + self.kind.kind_int

    def __hash__(self):
        return hash(int(self))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.kind.__qualname__}, {self.dt!r})"

    @classmethod
    def _get_range(cls, item):
        """
        Extracts a date range tuple from the given item.

        If the item is a `date`, returns a tuple with the date as both start and end.
        If the item is a `Timeunit`, returns its date range.
        If the item is a tuple of two `date` objects, returns the tuple.
        Raises a `TypeError` if the item cannot be interpreted as a date range.

        Parameters:
            item: A `date`, `Timeunit`, or a tuple of two `date` objects.

        Returns:
            A tuple of two `date` objects representing the start and end of the range.

        Raises:
            TypeError: If the item cannot be interpreted as a date range.
        """
        if isinstance(item, date):
            return item, item
        if isinstance(item, Timeunit):
            return item.date_range
        # try to make a range
        try:
            dt0, dt1 = item
            if isinstance(dt0, date) and isinstance(dt1, date):
                return item
            raise TypeError(f"Cannot interpret date range of type {type(item)}")
        except TypeError:
            pass
        raise TypeError(f"Item {item!r} has no date range.")

    def overlaps_with(self, item):
        """
        Check if the time unit overlaps with a given date, date range, or another time unit.

        Parameters:
            item: A date, Timeunit, or a tuple of two dates representing a date range.

        Returns:
            bool: True if there is any overlap between this time unit and the specified range
            or unit; otherwise, False.
        """
        frm0, to0 = self._get_range(item)
        frm, to = self.date_range
        return to >= frm0 and to0 >= frm

    def __contains__(self, item):
        frm0, to0 = self._get_range(item)
        frm, to = self.date_range
        return frm <= frm0 and to0 <= to

    def __str__(self):
        return self.kind.to_str(self.dt)
