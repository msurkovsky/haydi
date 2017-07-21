from .domain import Domain
from .cnf import expand

import random


class Values(Domain):
    """
    A domain created from a collection.

    Args:
        values (collection): A collection of items that is
                             used as the content for the new domain
        name (string): Name of domain

    Examples:

        >>> hd.Values(("a", "b", 123, 431))
        <Values size=4 {'a', 'b', 123, 431}>
    """

    step_jumps = True

    def __init__(self, values=None, name=None):
        super(Values, self).__init__(name)
        values = tuple(values)
        self._size = len(values)
        self.values = values

    def generate_one(self):
        return random.choice(self.values)

    def create_iter(self, step=0):
        while step < len(self.values):
            yield self.values[step]
            step += 1
        raise StopIteration()

    def to_values(self, max_size=None):
        return self

    def decompose(self):
        return tuple()

    def is_same(self, domain):
        if not isinstance(domain, Values):
            return False

        return self.values == domain.values

class CnfValues(Domain):

    def __init__(self, values, name=None):
        super(CnfValues, self).__init__(name)
        values = tuple(values)
        self.values = values

    def _compute_size(self):
        return None

    def create_cn_iter(self):
        return iter(self.values)

    def create_iter(self, step=0):
        assert step == 0
        for item in self.values:
            for item2 in expand(item):
                yield item2

    def to_cnf_values(self, max_size=None):
        return self

    def decompose(self):
        return tuple()

    def is_same(self, domain):
        if not isinstance(domain, CnfValues):
            return False

        return self.values == domain.values
