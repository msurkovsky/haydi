from testutils import init
init()

from haydi.ext.graphrenderer import GraphRenderer
import haydi as hd

import itertools

def test_make_oriented_graph():

    # TEST 1 ===================================================================
    nodes = hd.ASet(2, "n")
    n0, n1 = nodes.run()

    graphs = hd.Subsets(nodes * nodes)

    g_structure = graphs.filter(lambda gs: len(gs) > 2).first().run()
    # g_structure = {(n0, n0), (n0, n1), (n1, n0)}

    gr = GraphRenderer(g_structure)
    g = gr.nodes(nodes,
                {n: "A({})".format(i)
                for i, n in enumerate(nodes)}) \
        .assemble_graph()
    assert g is not None
    a0, a0_presented = g.node_check(n0)
    assert a0_presented
    a1, a1_presented = g.node_check(n1)
    assert a1_presented

    assert len(a0.arcs) == 2
    a0_targets = map(lambda a: a.node, a0.arcs)
    assert a0 in a0_targets and  a1 in a0_targets

    # TEST 2 ===================================================================
    nodes = (0, 1, 2, 3, 4)
    g_structure = {(1, 2, 2.3),
                   (2,3, 1.4),
                   (1,3, 3.4),
                   (3, 3, 6)} # the '6' make automatic nodes identification impossible,
                              # the same type, but when the exact nodes are specified,
                              # it's OK.
    gr = GraphRenderer(g_structure)
    try:
        # assembling without specifying nodes throws exception in this case
        g = gr.assemble_graph()
    except Exception:
        assert True

    # --------------------------------------------------------------------------

    g = gr \
        .nodes(nodes) \
        .assemble_graph()

    n0= g.node(0)
    assert len(n0.arcs) == 0


def test_make_unoriented_graph():

    # hasse diagram of powerset above three elements
    s = (0, 1, 2)
    powerset = list(itertools.chain.from_iterable(itertools.combinations(s, r)
                                                  for r in range(len(s)+1)))
    edges = ({a, b} for a, b in itertools.product(powerset, powerset)
             if a != b and # different elements
             set(a).issubset(b) and # subset relation
             len(set(b).difference(a)) == 1) # exclude transitive edges


    gr = GraphRenderer(edges)
    g = gr \
        .nodes(powerset,
                {n: "{" + ", ".join(map(str, n)) + "}" for n in powerset}) \
        .assemble_graph()
    assert not g.directed
