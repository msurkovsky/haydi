from testutils import init
init()

import haydi as hd # noqa


def test_permutations_iterate():
    v = hd.Values(("A", "B", "C"))
    p = hd.Permutations(v)
    assert p.size == 6

    result = set(p)
    expected = set([('A', 'B', 'C'), ('A', 'C', 'B'), ('B', 'A', 'C'),
                    ('B', 'C', 'A'), ('C', 'A', 'B'), ('C', 'B', 'A')])
    assert result == expected


def test_permutations_to_values():
    r = hd.Range(3)
    p = hd.Permutations(r)

    v = p.to_values()

    assert isinstance(v, hd.Values)
    assert list(v) == list(p)


def test_permutations_to_values_maxsize():
    r = hd.Range(3)
    p = hd.Permutations(r)

    v = p.to_values(max_size=r.size)

    assert isinstance(v, hd.Permutations)
    assert isinstance(v.domain, hd.Values)
    assert list(v) == list(p)

def test_permutations_decompose():
    r = hd.Range(3)
    p = hd.Permutations(r)

    assert p.decompose() == (r,)

def test_permutations_is_same():
    n = 3
    r = hd.Range(n)
    p = hd.Permutations(r)

    assert p.is_same(hd.Permutations(hd.Range(n)))
