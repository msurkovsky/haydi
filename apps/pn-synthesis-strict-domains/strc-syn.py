import copy
import sys
sys.path.insert(0, "../../src")

import haydi as hd #noqa
from haydi.ext.xenv import ExperimentEnv  # noqa

COUNT = None

def compute(searched_lts,
            searched_lts_init_state,
            places,      # a set of places
            transitions, # a set of transitions
            max_in_arc_weight,
            max_out_arc_weight,
            max_init_marking,
            max_depth=None,
            count=None):

    searched_lts.make_graph(searched_lts_init_state).write("input-lts.dot")

    in_arc = places * transitions
    out_arc = transitions * places

    wi = hd.Mapping(in_arc, hd.Range(max_in_arc_weight + 1))
    wo = hd.Mapping(out_arc, hd.Range(max_out_arc_weight + 1))
    m0 = hd.Mapping(places, hd.Range(max_init_marking + 1))

    pn = m0 * wi * wo

    def equivalent(pn_system):
        pn_lts = PnLTS(pn_system, transitions)
        pair = hd.DLTSProduct((searched_lts, pn_lts))
        init_state = (searched_lts_init_state, pn_system[0])

        for states in pair.bfs(init_state):
            enabled1 = searched_lts.get_enabled_actions(states[0])
            enabled2 = pn_lts.get_enabled_actions(states[1])

            a = set((frozenset(enabled1), frozenset(enabled2)))
            if len(a) > 1:
                return False
        return True

    if count is None:
        # source = pn
        # source = pn.create_cn_iter()
        source = pn.canonize()
    else:
        source = pn.generate(count)

    return source.filter(equivalent)

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
        for (p, t), w in self.wi.items:
            if w > 0:
                if t not in actions:
                    actions[t] = True
                actions[t] &= (w <= marking.get(p))
        return set(t for t, enabled in actions.iteritems() if enabled)

    def is_enabled(self, marking, transition):
        for (p, t), w in self.wi.items:
            if (t == transition and w > marking.get(p)):
                return False
        return True;

    def fire(self, marking, transition):
        new_marking = marking.to_dict()
        for (p, t), w in self.wi.items:
            if (t == transition):
                new_marking[p] -= w

        for (t, p), w in self.wo.items:
            if (t == transition):
                new_marking[p] += w
        return hd.Map(items=tuple(new_marking.iteritems()))

    def step(self, marking, transition):
        if self.is_enabled(marking, transition):
            return self.fire(marking, transition)
        return None


if __name__ == "__main__":
    env = ExperimentEnv("pnsynthesis",
                        globals(),
                        ["COUNT"])


    ## SMALL TEST
    places = hd.ASet(2, "p")
    transitions = hd.ASet(2, "t")
    t0, t1 = transitions # because of ASet actions has to be the same instances

    max_in_arc_weight = 1
    max_out_arc_weight = 1
    max_init_marking = 1

    input_lts = hd.Map((
        ((0, t0), 1),
        ((0, t1), 2),
        ((1, t1), 3),
        ((2, t0), 3),
        ((3, t1), 4)
    ))

    canonized_input = hd.canonize(input_lts)
    searched_lts = hd.dlts_from_dict(canonized_input.to_dict(), transitions)
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


    # searched_lts.make_graph(init_state).write("input-lts.dot")
    results = compute(searched_lts, init_state,
                      places, transitions,
                      max_in_arc_weight, max_out_arc_weight, max_init_marking)
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
