"""Representation of time supporting math operations with the particularity 
that hours can overflow (25 hours and more is legit)"""
import re
import functools

TIME_PATTERN = re.compile(r'(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)')


def str_to_bt(decorated):
    """
    Decoration for functions which want to accept str representation of BrokenTime in place of BrokenTime

    :param decorated: function to wrap
    :type decorated: function
    :return: function with same logic and which accepts str arguments in place of BrokenTime
    :rtype: function
    """
    @functools.wraps(decorated)
    def fresh_function(*args, **kwargs):
        t = BrokenTime.from_str
        fresh_args = tuple(t(arg) if type(arg) == str else arg for arg in args)

        return decorated(*fresh_args, **kwargs)

    return fresh_function


class BrokenTime:
    def __init__(self, hours=0, minutes=0, seconds=0):
        self._seconds = hours * 3600 + minutes * 60 + seconds

    @property
    def hours(self):
        return abs(self._seconds) // 3600

    @property
    def minutes(self):
        return abs(self._seconds) // 60 % 60

    @property
    def seconds(self):
        return abs(self._seconds) % 60

    def __repr__(self):
        display_sign = "-" if self._seconds < 0 else ""
        return f'{display_sign}{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}'

    # ## COMPARISON OPERATORS

    @str_to_bt
    def __eq__(self, other):
        """
        :param other: the right operand of the comparison
        :type other: BrokenTime
        """
        return self._seconds == other._seconds

    @str_to_bt
    def __ne__(self, other):
        """
        :param other: the right operand of the comparison
        :type other: BrokenTime
        """
        return self._seconds != other._seconds

    @str_to_bt
    def __gt__(self, other):
        """
        :param other: the right operand of the comparison
        :type other: BrokenTime
        """
        return self._seconds > other._seconds

    @str_to_bt
    def __ge__(self, other):
        """
        :param other: the right operand of the comparison
        :type other: BrokenTime
        """
        return self._seconds >= other._seconds

    @str_to_bt
    def __lt__(self, other):
        """
        :param other: the right operand of the comparison
        :type other: BrokenTime
        """
        return self._seconds < other._seconds

    @str_to_bt
    def __le__(self, other):
        """
        :param other: the right operand of the comparison
        :type other: BrokenTime
        """
        return self._seconds <= other._seconds

    # ## ARITHMETIC'S OPERATORS

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.sub(other)

    def __mul__(self, coefficient):
        return self.mul(coefficient)

    def __truediv__(self, right_operand):
        return self.truediv(right_operand)

    def __floordiv__(self, right_operand):
        return self.floordiv(right_operand)

    def __mod__(self, other):
        return self.mod(other)

    # ## UNARY

    def __neg__(self):
        self.neg()

    # ## ITERATION PROTOCOL

    def __iter__(self):
        return iter(BrokenTimeIterable(self))

    @staticmethod
    @str_to_bt
    def range(*args):
        if len(args) == 1:
            return BrokenTimeIterable(start=BrokenTime(), end=args[0])
        elif len(args) == 2:
            return BrokenTimeIterable(start=args[0], end=args[1])
        elif len(args) == 3:
            return BrokenTimeIterable(start=args[0], end=args[1], step=args[2])
        else:
            raise ValueError('Expects 1 to 3 arguments')

    @str_to_bt
    def since(self):
        return BrokenTimeIterable(self)

    @str_to_bt
    def to(self, end):
        return BrokenTimeIterable(self, end)

    # ## METHODS

    @str_to_bt
    def add(self, other):
        """
        :param other: the right operand of the addition
        :type other: BrokenTime
        """
        return BrokenTime(seconds=self._seconds + other._seconds)

    @str_to_bt
    def sub(self, other):
        """
        :param other: the right operand of the subtraction
        :type other: BrokenTime
        """
        return BrokenTime(seconds=self._seconds - other._seconds)

    def mul(self, coefficient):
        """
        :param coefficient: the right operand of the multiplication
        :type coefficient: int | float
        :rtype: BrokenTime
        :return: result of the multiplication, with seconds rounded to closest integer
        """
        return BrokenTime(seconds=round(self._seconds * coefficient))

    @str_to_bt
    def truediv(self, right_operand):
        """
        :param right_operand: right operand of the division
        :type right_operand: BrokenTime | int | float
        :rtype: int | float | BrokenTime
        :return: if right_operand is a BrokenTime, the number of times self contains it
        :return: if right_operand is a number, the BrokenTime that self contains right_operand times, seconds rounded to
        closest integer
        """
        if type(right_operand) == BrokenTime:
            return self._seconds / right_operand._seconds
        return BrokenTime(seconds=round(self._seconds / right_operand))

    @str_to_bt
    def floordiv(self, right_operand):
        """
        :param right_operand: right operand of the division
        :type right_operand: BrokenTime | int | float
        :rtype:  int | float | BrokenTime
        :return: if right_operand is a BrokenTime, the number of times self fully contains it
        :return: if right_operand is a number, the biggest BrokenTime that self contains fully right_operand times
        """
        if type(right_operand) == BrokenTime:
            return self._seconds // right_operand._seconds
        return BrokenTime(seconds=self._seconds // right_operand)

    @str_to_bt
    def mod(self, other):
        """
        :param other: the base of the modulo
        :type other: BrokenTime
        :return: The rest of the division of self by other
        :rtype: BrokenTime
        """
        return BrokenTime(seconds=self._seconds % other._seconds)

    def neg(self):
        """
        :return: the opposite of self, relative to zero
        :rtype: BrokenTime
        """
        return BrokenTime(seconds=-self._seconds)

    @staticmethod
    def from_str(time_str):
        tentative_match = TIME_PATTERN.match(time_str)
        if hasattr(tentative_match, 'groupdict'):
            match = tentative_match.groupdict()
        else:
            raise ValueError(f'string do not match time pattern "{TIME_PATTERN.pattern}"')

        time_values = {key: int(value) for key, value in match.items()}

        return BrokenTime(**time_values)


class BrokenTimeIterable:
    def __init__(self, start, end=None, step=BrokenTime(1, 0, 0)):
        self.start = start
        # todo if step is a number, understands it is the number of wanted steps (step = (end-start)/step)
        self.step = step
        self.end = end

    def __repr__(self):
        return f"['{self.start}':'{self.end}':'{self.step}']"

    def __iter__(self):
        return BrokenTimeIterator(self)

    @str_to_bt
    def to(self, end):
        return BrokenTimeIterable(self.start, end, self.step)

    @str_to_bt
    def by(self, step):
        return BrokenTimeIterable(self.start, self.end, step)


class BrokenTimeIterator:
    def __init__(self, iterable):
        self.iterable = iterable
        self.current = iterable.start

    def __repr__(self):
        return f"{self.iterable}<-'{self.current}'"

    def __next__(self):
        if self.iterable.end is not None and self.current > self.iterable.end:
            raise StopIteration

        current = self.current
        self.current += self.iterable.step
        return current
