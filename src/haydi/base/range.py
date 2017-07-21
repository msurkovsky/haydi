
from .domain import Domain

from random import randint


class Range(Domain):
    """Domain that contains a range of integers

    The domain of integers in a given range. The interface is similar to
    :func:`xrange`.

    
    It may be called only just as ``Range(stop)`` that behaves like ``Range(0,
    stop, 1).``

    When a single argument is provided:

    Args:
        end (int): End of interval (not included). Interval stards at 0,
                   step is 1.

    When two arguments are provided:

    Args:
        start (int): Start of the range
        end (int): End of the range (not included), step is 1.

    When three arguments are provided:

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

    step_jumps = True
    strict = True

    def __init__(self, start, end=None, step=1, name=None):
        super(Range, self).__init__(name)
        if end is None:
            end = start
            start = 0
        end = max(start, end)

        if step == 1 and end == 1:
            size = end
        else:
            size = (end - start) / step
        self._size = size
        self.start = start
        self.end = end
        self.step = step

    def generate_one(self):
        if self.step == 1:
            return randint(self.start, self.end - 1)
        else:
            return randint(0, self.size - 1) * self.step

    def create_iter(self, step=0):
        return iter(xrange(self.start + step * self.step, self.end, self.step))

    def create_cn_iter(self):
        return self.create_iter()

    def decompose(self):
        return tuple()

    def is_same(self, domain):
        if not isinstance(domain, Range):
            return False

        return self.start == domain.start and \
            self.end == domain.end and \
            self.step == domain.step
