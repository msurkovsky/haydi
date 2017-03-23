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

    places = hd.Range(n_events, name="P")
    trans = hd.Range(n_events, name="T")
    in_arc = hd.Product((places, trans), name="in_arc")
    out_arc = hd.Product((trans, places), name="out_arc")

    wi = hd.Mapping(in_arc, hd.Range(max_in_arc_weight + 1))
    wo = hd.Mapping(out_arc, hd.Range(max_out_arc_weight + 1))
    m0 = hd.Mapping(places, hd.Range(max_init_marking + 1))

    pn = m0 * wi * wo

    def equivalent(pn_system):
        pn_lts = PnLTS(pn_system, trans)

        pair = hd.DLTSProduct((searched_lts, pn_lts))
        init_state = (searched_lts_init_state, hashabledict(pn_system[0]))

        for states in pair.bfs(init_state):
            a = set(frozenset(sy.get_enabled_actions(st))
                    for sy, st in zip ((searched_lts, pn_lts), states))
            if len(a) > 1:
                return False

        return True

    if count is None:
        source = pn
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
        for (p, t), w in self.wi.iteritems():
            if w > 0:
                if t not in actions:
                    actions[t] = True
                actions[t] &= (w <= marking[p])
        return set(t for t, enabled in actions.iteritems() if enabled)

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


if __name__ == "__main__":
    env = ExperimentEnv("pnsynthesis",
                        globals(),
                        ["COUNT"])

    ## SMALL TEST -- test_small_example1 (from tests)
    n_events = 2
    max_in_arc_weight = 1
    max_out_arc_weight = 1
    max_init_marking = 1
    searched_lts = hd.DLTSFromGraph(hd.Graph([
        (0, 0, 1),
        (0, 1, 2),
        (1, 1, 3),
        (2, 0, 3),
        (3, 1, 4)
    ]), hd.Range(n_events))
    init_state = 0

    searched_lts.make_graph(init_state).write("input-lts.dot")
    results = env.run(
        compute(searched_lts,
                init_state,
                n_events, max_in_arc_weight, max_out_arc_weight, max_init_marking,
                count=COUNT),
        write=True)

    for result in results:
       print result
