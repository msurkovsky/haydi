import copy
import sys
sys.path.insert(0, "../../src")

import qit

def compute(searched_lts,
            searched_lts_init_state,
            n_events,
            max_in_arc_weight,
            max_out_arc_weight,
            max_init_marking,
            max_depth=None,
            count=None):

    places = qit.Range(n_events, name="P")
    trans = qit.Range(n_events, name="T")
    in_arc = qit.Product((places, trans), name="in_arc")
    out_arc = qit.Product((trans, places), name="out_arc")

    wi = qit.Mapping(in_arc, qit.Range(max_in_arc_weight + 1))
    wo = qit.Mapping(out_arc, qit.Range(max_out_arc_weight + 1))
    m0 = qit.Mapping(places, qit.Range(max_init_marking + 1))

    pn = m0 * wi * wo

    def check_equivalence(pn_system):
        pn_lts = PnLTS(pn_system, trans)
        equivalent = pn_lts.eq_check(hashabledict(pn_system[0]),
                                     searched_lts,
                                     searched_lts_init_state,
                                     max_depth)
        return (pn_system, equivalent)

    if count is None:
        source = pn.iterate()
    else:
        source = pn.generate(count)

    results = source.map(check_equivalence) \
                    .filter(lambda (pn, eq): eq) \
                    .map(lambda (pn, eq): pn) \
                    .run()

    print "total: ", len(results)
    for i, pn_system in enumerate(results):
        print "{}: ".format(i+1), pn_system
        lts = PnLTS(pn_system, trans)
        lts.make_graph(hashabledict(lts.init_marking)).write("lts-{}.dot".format(i+1))

class hashabledict(dict):

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

class PnLTS(qit.LTS):

    def __init__(self, pn_system, actions):
        super(PnLTS, self).__init__(actions)
        self.init_marking = pn_system[0]
        self.wi = pn_system[1]
        self.wo = pn_system[2]

    def is_enabled(self, marking, transition):
        for (p, t), w in self.wi.iteritems():
            if (t == transition and w > marking[p]):
                return False
        return True;

    def fire(self, marking, transition):
        new_marking = copy.deepcopy(marking)
        for (p, t), w in self.wi.iteritems():
            if (t == transition):
                new_marking[p] -= w

        for (t, p), w in self.wo.iteritems():
            if (t == transition):
                new_marking[p] += w
        return new_marking

    def step(self, marking, transition):
        if self.is_enabled(marking, transition):
            return self.fire(marking, transition)
        return None

def small_test():
    n_events = 2
    max_in_arc_weight = 1
    max_out_arc_weight = 1
    max_init_marking = 1

    # small_test = ( # pn system with RG: 0->1->1 | 1->0->1
    #     # m0
    #     { 0: 1, 1: 1 },
    #     # wi
    #     {(0, 0): 1,
    #      (0, 1): 0,
    #      (1, 0): 0,
    #      (1, 1): 1},
    #     # wo
    #     {(0, 0): 0,
    #      (0, 1): 1,
    #      (1, 0): 0,
    #      (1, 1): 0}
    # )
    # searched_lts = PnLTS(small_test, qit.Range(n_events))
    # searched_lts_init_state = hashabledict({0: 1, 1: 1})

    searched_lts = qit.LTSByGraph(qit.Graph([
        (0, 0, 1),
        (0, 1, 2),
        (1, 1, 3),
        (2, 0, 3),
        (3, 1, 4)
    ]), qit.Range(n_events))
    init_state = 0
    searched_lts.make_graph(init_state).write("input-lts.dot")

    compute(searched_lts, init_state,
            n_events, max_in_arc_weight, max_out_arc_weight, max_init_marking)

def real_test(count):
    n_events = 3
    max_in_arc_weight = 2
    max_out_arc_weight = 2
    max_init_marking = 2
    # test_pn_system = ( # pn system with RG: 0->0->1->1->2->2->0 ...
    #     # m0
    #     {0: 2, 1: 0, 2: 2},
    #     # wi
    #     {(0, 0): 2,
    #      (0, 1): 1,
    #      (1, 0): 0,
    #      (1, 1): 2,
    #      (0, 2): 0,
    #      (2, 0): 1,
    #      (2, 2): 2,
    #      (1, 2): 1,
    #      (2, 1): 0},
    #     # wo
    #     {(0, 0): 2,
    #      (0, 1): 1,
    #      (1, 0): 0,
    #      (1, 1): 2,
    #      (0, 2): 0,
    #      (2, 0): 1,
    #      (2, 2): 2,
    #      (1, 2): 1,
    #      (2, 1): 0}
    # )
    # searched_lts = PnLTS(test_pn_system, qit.Range(n_events))
    # searched_lts_init_state = hashabledict({0: 2, 1: 0, 2: 2})

    searched_lts = qit.LTSByGraph(qit.Graph([
        (0, 0, 1),
        (1, 0, 2),
        (2, 1, 3),
        (3, 1, 4),
        (4, 2, 5),
        (5, 2, 0),
    ]), qit.Range(n_events))
    init_state = 0
    searched_lts.make_graph(init_state).write("input-lts.dot")

    compute(searched_lts, init_state,
            n_events, max_in_arc_weight, max_out_arc_weight, max_init_marking,
            count=count)


if __name__ == "__main__":
    # real_test(1e8)
    small_test()


