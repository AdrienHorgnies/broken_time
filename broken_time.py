"""Representation of time supporting math operations with the particularity 
that hours can overflow (25 hours and more is legit)"""
import re

TIME_PATTERN = re.compile(r'(?P<hours>\d+):(?P<minutes>\d\d):(?P<seconds>\d\d)')


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

    class Decorators:
        @staticmethod
        def cast_args(function=None, after=-1):
            """cast arguments of decorated function to BrokenTime
            :param function: decorated function 
            :param after: index after which arguments must be casted (after is excluded)
            :type after: int
            """

            def wrapper(wrapped_function):
                def fresh_function(*args, **kwargs):
                    recycled_args = args[:after + 1]

                    t = BrokenTime._ensure_object
                    fresh_args = tuple(t(arg) for arg in args[after + 1:])

                    args = recycled_args + fresh_args

                    return wrapped_function(*args, **kwargs)

                return fresh_function

            if function is not None:
                return wrapper(function)

            return wrapper

    # ## COMPARISON OPERATORS

    @Decorators.cast_args
    def __eq__(self, other):
        return self._seconds == other._seconds

    @Decorators.cast_args
    def __ne__(self, other):
        return self._seconds != other._seconds

    @Decorators.cast_args
    def __gt__(self, other):
        return self._seconds > other._seconds

    @Decorators.cast_args
    def __ge__(self, other):
        return self._seconds >= other._seconds

    @Decorators.cast_args
    def __lt__(self, other):
        return self._seconds < other._seconds

    @Decorators.cast_args
    def __le__(self, other):
        return self._seconds <= other._seconds

    # ## ARITHMETICS OPERATORS

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.sub(other)

    # ## ITERATION PROTOCOL

    def __iter__(self):
        return iter(BrokenTimeIterable(self))

    @staticmethod
    @Decorators.cast_args
    def range(*args):
        if len(args) == 1:
            return BrokenTimeIterable(start=BrokenTime(), end=args[0])
        elif len(args) == 2:
            return BrokenTimeIterable(start=args[0], end=args[1])
        elif len(args) == 3:
            return BrokenTimeIterable(start=args[0], end=args[1], step=args[2])
        else:
            raise ValueError('Expects 1 to 3 arguments')

    @Decorators.cast_args
    def since(self):
        return BrokenTimeIterable(self)

    @Decorators.cast_args
    def to(self, end):
        return BrokenTimeIterable(self, end)

    # ## METHODS

    @Decorators.cast_args
    def add(self, other):
        return BrokenTime(seconds=self._seconds + other._seconds)

    @Decorators.cast_args
    def sub(self, other):
        return BrokenTime(seconds=self._seconds - other._seconds)

    def mul(self, coefficient):
        return BrokenTime(seconds=round(self._seconds * coefficient))

    @staticmethod
    def from_str(time_str):
        try:
            matches = TIME_PATTERN.match(time_str).groupdict()
        except AttributeError:
            raise ValueError('string do not match time pattern')

        casted_matches = {key: int(value) for key, value in matches.items()}

        return BrokenTime(**casted_matches)

    @staticmethod
    def _ensure_object(thing):
        if type(thing) == BrokenTime:
            return thing
        elif type(thing) == str:
            return BrokenTime.from_str(thing)

        raise ValueError(f'{thing} cannot be converted to BrokenTime')


class BrokenTimeIterable:
    def __init__(self, start, end=None, step=BrokenTime(1, 0, 0)):
        self.start = start
        self.step = step
        self.end = end

    def __repr__(self):
        return f"['{self.start}':'{self.end}':'{self.step}']"

    def __iter__(self):
        return BrokenTimeIterator(self)

    @BrokenTime.Decorators.cast_args(after=0)
    def to(self, end):
        return BrokenTimeIterable(self.start, end, self.step)

    @BrokenTime.Decorators.cast_args(after=0)
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
