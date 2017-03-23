import copy
import sys
sys.path.insert(0, "../../src")

import haydi as hd #noqa
from haydi.ext.xenv import ExperimentEnv  # noqa

COUNT = None

def compute(searched_lts,
            searched_lts_init_state,
            n_events,
            max_in_arc_weight,
            max_out_arc_weight,
            max_init_marking,
            max_depth=None,
            count=None):

    places = hd.ASet(n_events, "P")
    # places = hd.Range(n_events, name="P")
    trans = hd.ASet(n_events, "T")
    # trans = hd.Range(n_events, name="T")
    in_arc = places * trans
    out_arc = trans * places
    # in_arc = hd.Product((places, trans), name="in_arc")
    # out_arc = hd.Product((trans, places), name="out_arc")

    wi = hd.Mapping(in_arc, hd.ASet(max_in_arc_weight + 1, "iw"))
    # wi = hd.Mapping(in_arc, hd.Range(max_in_arc_weight + 1))

    wo = hd.Mapping(out_arc, hd.ASet(max_out_arc_weight + 1, "ow"))
    # wo = hd.Mapping(out_arc, hd.Range(max_out_arc_weight + 1))

    m0 = hd.Mapping(places, hd.ASet(max_init_marking + 1, "im"))
    # m0 = hd.Mapping(places, hd.Range(max_init_marking + 1))

    pn = m0 * wi * wo

    def check_equivalence(pn_system):
        pn_lts = PnLTS(pn_system, trans)

        pair = hd.DLTSProduct((searched_lts, pn_lts))

        # pn_tmp = pn_system[0].to_dict() # TODO (FIXME): pn_system[0] is a strict map
        init_state = (searched_lts_init_state, pn_system[0])

        for states in pair.bfs(init_state):
            a1 = searched_lts.get_enabled_actions(states[0])
            a2 = pn_lts.get_enabled_actions(states[1])
            for aa2 in a2:
                print type (aa2), aa2
            # print "A1:", set(a1), "A2:", set(a2)
            # set(frozenset(((a1), set(a2))))
            # print set(frozenset((a1, a2)))
            return False
            # a = set(frozenset(sy.get_enabled_actions(st))
            #         for sy, st in zip ((searched_lts, pn_lts), states))
            if len(a) > 1:
                return False
        return True

    if count is None:
        source = pn
    else:
        source = pn.generate(count)

    return source.filter(check_equivalence)

class hashabledict(dict):

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

class PnLTS(hd.DLTS):

    def __init__(self, pn_system, actions=None):
        super(PnLTS, self).__init__(actions)
        self.init_marking = pn_system[0]
        self.wi = pn_system[1]
        self.wo = pn_system[2]

    def get_enabled_actions(self, marking):
        actions = {} # { action: enabled }
        for (p, t), w in self.wi.to_dict().iteritems():
            if w > 0:
                if t not in actions:
                    actions[t] = True
                actions[t] &= (w <= marking[p])
        return set(t for t, enabled in actions.iteritems() if enabled)

    def is_enabled(self, marking, transition):
        for (p, t), w in self.wi.to_dict().iteritems():
            if (t == transition and w > marking[p]):
                return False
        return True;

    def fire(self, marking, transition):
        new_marking = copy.deepcopy(marking)
        for (p, t), w in self.wi.to_dict().iteritems():
            if (t == transition):
                new_marking[p] -= w

        for (t, p), w in self.wo.to_dict().iteritems():
            if (t == transition):
                new_marking[p] += w
        return new_marking

    def step(self, marking, transition):
        if self.is_enabled(marking, transition):
            return self.fire(marking, transition)
        return None


if __name__ == "__main__":
    env = ExperimentEnv("pnsynthesis",
                        globals(),
                        ["COUNT"])

    ## SMALL TEST
    n_events = 2
    max_in_arc_weight = 1
    max_out_arc_weight = 1
    max_init_marking = 1
    searched_lts = hd.DLTSByGraph(hd.Graph([
        (0, "T0", 1),
        (0, "T1", 2),
        (1, "T1", 3),
        (2, "T0", 3),
        (3, "T1", 4)
    ]), hd.Range(n_events))
    init_state = 0
    # solution = ( # pn system with RG: 0->1->1 | 1->0->1
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
    # solution_lts = PnLTS(solution, hd.Range(n_events))
    # solution_lts_init_state = hashabledict({0: 1, 1: 1})


    ## REAL TEST
    # n_events = 3
    # max_in_arc_weight = 2
    # max_out_arc_weight = 2
    # max_init_marking = 2
    # searched_lts = hd.DLTSByGraph(hd.Graph([
    #     (0, 0, 1),
    #     (1, 0, 2),
    #     (2, 1, 3),
    #     (3, 1, 4),
    #     (4, 2, 5),
    #     (5, 2, 0),
    # ]), hd.Range(n_events))
    # init_state = 0

    # solution = ( # pn system with RG: 0->0->1->1->2->2->0 ...
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
    # solution_lts = PnLTS(solution, hd.Range(n_events))
    # solution_lts_init_state = hashabledict({0: 2, 1: 0, 2: 2})


    searched_lts.make_graph(init_state).write("input-lts.dot")
    results = compute(searched_lts, init_state,
                      n_events, max_in_arc_weight, max_out_arc_weight, max_init_marking)
    # results = env.run(
    #     compute(searched_lts,
    #             init_state,
    #             n_events, max_in_arc_weight, max_out_arc_weight, max_init_marking,
    #             count=COUNT),
    #     write=True)

    i = 0
    for result in results:
       i += 1
       print result
    print "#resuts: ", i
