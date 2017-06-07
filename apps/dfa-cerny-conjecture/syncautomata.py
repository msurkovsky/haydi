import sys
sys.path.insert(0, "../../src")

import haydi as hd # noqa
import haydi.ext.automata # noqa
from haydi.ext.xenv import ExperimentEnv # noqa
from pprint import pprint # noqa

N_SIZE = 4 # Number of states
A_SIZE = 2 # Number of actions (alphabet size)

COUNT = None        # None = iterate all

MIN_LEVEL = 3
MAX_SAMPLES_PER_LEVEL = 300

def compute(n_size, a_size, count):
    states = hd.Range(n_size)
    actions = hd.Range(a_size)

    dfa = hd.Mapping((states * actions), states)

    def are_all_states_covered(dfa):
        new_states = set([ 0 ]) # 0 is used as starting state
        processed = []

        dfa_as_dict = dfa.to_dict()
        while new_states:
            cs = new_states.pop()
            processed.append(cs)

            if len(processed) == N_SIZE:
                break

            for a in actions:
                ns = dfa_as_dict[(cs, a)]
                if ns not in processed:
                    new_states.add(ns)

        processed.sort()
        return processed == list(states)

    def is_synchronizable(dfa):
        if not are_all_states_covered(dfa):
            return False

        max = N_SIZE ** 2
        dfa_lts = DfaLTS(dfa, actions)
        synchronizable_pairs = set()

        def are_states_synchronizeable((s1, s2)):
            # both states represents the same one or
            # they alredy been marked as synchronizable
            return (s1 == s2) or (s1, s2) in synchronizable_pairs

        lts_pair = dfa_lts * dfa_lts
        state_pairs = hd.Product((states, states), unordered=True)
        for spair in state_pairs:
            witness = lts_pair.bfs(spair, max) \
                        .filter(are_states_synchronizeable) \
                        .first() \
                        .run()

            if witness is None:
                return False # non-synchronizable DFA

            # mark the pair of states as synchronizeable
            synchronizable_pairs.add(spair)
        return True

    def compute_shortes_sword(dfa):
        dfa_lts = DfaLTS(dfa, actions)
        lts_n_tuple = hd.DLTSProduct(tuple(dfa_lts for i in xrange(N_SIZE)))

        def same_states(states_path_pair):
            states = states_path_pair[0]
            return all(s == states[0] for s in states)

        witnesses = lts_n_tuple.bfs_path(tuple(range(N_SIZE))) \
                                    .filter(same_states) \
                                    .max_all(lambda (states, path): -len(path)) \
                                    .run()

        # (dfa, the length, [(sync_state, path)])
        return (dfa, len(witnesses[0][1]), [(states[0], path)
                                            for (states, path) in witnesses])

    if count is not None:
        source = dfa.generate(count)
    else:
        source = dfa

    results = source.filter(is_synchronizable).map(compute_shortes_sword)
    results = results.filter(lambda x: x[1] >= MIN_LEVEL)
    results = results.groups(lambda x: x[1], MAX_SAMPLES_PER_LEVEL)

    return results


class DfaLTS(hd.DLTS):
    def __init__(self, dfa, actions):
        hd.DLTS.__init__(self, actions)
        self.dfa = dfa.to_dict()

    def step(self, state, action):
        return self.dfa[(state, action)]


def main():
    env = ExperimentEnv("dfa",
                        globals(),
                        [ "N_SIZE", "A_SIZE", "COUNT",
                          "MIN_LEVEL", "MAX_SAMPLES_PER_LEVEL" ])

    env.parse_args()
    results = env.run(
        compute(N_SIZE, A_SIZE, COUNT),
        write=True)

    keys = results.keys()
    keys.sort(reverse=True)
    for key in keys:
        print "Level {}: {} samples".format(key, len(results[key]))

    if results:
        best = max(results.keys())
        print "Example of level {}:".format(best)
        pprint(results[best][0])
        # TODO: dfa to graph


if __name__ == "__main__":
    main()
