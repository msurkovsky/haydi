from testutils import init
init()

import haydi as hd  # noqa


def test_values_flags():
    a = hd.Values(["a", "b", "c"])
    assert not a.filtered
    assert a.step_jumps
    assert not a.strict


def test_values_iterate():

    a = hd.Values(["a", "b", "c"])

    assert not a.filtered
    assert a.step_jumps
    assert a.size == 3
    assert list(a) == ["a", "b", "c"]
    for x in a.generate(100):
        assert x in ("a", "b", "c")

    b = hd.Values([])
    assert b.size == 0
    assert list(b) == []


def test_values_set():
    a = hd.Values(["a", "b", "c", "d"])
    i = a.create_iter(2)
    assert list(i) == ["c", "d"]


def test_values_name():
    a = hd.Values(["a", "b", "c", "d"], name="ListTest")
    assert a.name == "ListTest"


def test_cnfs_values():
    ax = hd.ASet(3, "a")
    a0, a1, a2 = ax
    assert list(hd.CnfValues((a0,)).create_cn_iter()) == [a0]
    assert list(hd.CnfValues((a0,))) == [a0, a1, a2]


def test_values_repr():
    v = hd.Values(("abc", 321, (2.2, 1)))
    assert repr(v) == "<Values size=3 {'abc', 321, (2.2, 1)}>"


def test_values_to_values():
    v = hd.Values(("A", "B", "C"))
    assert v.to_values() == v


def test_cnfs_to_values():
    ax = hd.ASet(3, "a")
    a0, a1, a2 = ax

    c = hd.CnfValues((a0, ))
    v = c.to_values()

    assert isinstance(v, hd.Values)
    assert list(c) == list(v)


def test_cnfs_to_cnf_values():
    ax = hd.ASet(3, "a")
    a0, a1, a2 = ax

    c = hd.CnfValues((a0,))
    assert c == c.to_cnf_values()

def test_values_decompose():
    return not hd.Values((1,2,3,4)).decompose() # empty decomposition

def test_values_is_same():
    v1 = hd.Values((1,2,3,4))
    v2 = hd.Values(("abc", 321, (2.2, 1)))

    assert not v1.is_same(v2)
    assert hd.Values([]).is_same(hd.Values(tuple()))
