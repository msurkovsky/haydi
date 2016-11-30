
from .domain import Domain, DomainIterator

from random import randint
from copy import copy


class Range(Domain):
    """Range of integers

    It is domain with a similar interface as :func:`xrange`.

    It may be called only just as ``Range(stop)`` that behaves like ``Range(0,
    stop).``

    Args:
        start (int): Start of the range
        end (int): End of the range (not included)
        step (int): Step between two numbers

    Examples:

        >>> hd.Range(4)
        <Range size=4 {0, 1, 2, 3}>

        >>> list(hd.Range(4))
        [0, 1, 2, 3]

        >>> hd.Range(10, 20)  # From 10 upto 20
        <Range size=10 {10, 11, 12, 13, ...}>

        >>> hd.Range(4, 15, 3)  # From 4 upto 15, step 3
        <Range size=3 {4, 7, 10}>

    """

    exact_size = True

    def __init__(self, start, end=None, step=1, name=None):
        if end is None:
            end = start
            start = 0
        end = max(start, end)

        if step == 1 and end == 1:
            size = end
        else:
            size = (end - start) / step

        super(Range, self).__init__(size, True, size, name)

        self.start = start
        self.end = end
        self.step = step

    def generate_one(self):
        if self.step == 1:
            return randint(self.start, self.end - 1)
        else:
            return randint(0, self.size - 1) * self.step

    def create_iterator(self):
        return RangeIterator(self)


class RangeIterator(DomainIterator):

    def __init__(self, domain):
        super(RangeIterator, self).__init__(domain)
        self.value = domain.start

    def skip(self, start_index, count):
        start = self.domain.start + start_index
        end = start + count

        return RangeIterator(Range(start, end))

    def copy(self):
        return copy(self)

    def reset(self):
        self.value = self.domain.start

    def next(self):
        v = self.value
        if v < self.domain.end:
            self.value += self.domain.step
            return v
        raise StopIteration()

    def step(self):
        return self.next()

    def __repr__(self):
        return "{} iterator".format(str(self.domain))

    def set_step(self, index):
        self.value = self.domain.start + self.domain.step * index