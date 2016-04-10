import sys
from decimal import Decimal
sys.path.insert(0, "../../src")

import qit
import qit.ext.automata

def compute(n_size, a_size, count=None):
    """Find out two non-equivalent automata that follow each other
    as long as possible.

    Arguments:
    n_size -- number of states
    a_size -- the size of alphabet

    Keyword arguments:
    depth -- depth of BFS
    max_states -- maximal number of states
    count -- number of generated results (None = iterate all)
    """

    if (a_size > ord('z') - ord('a')):
        msg = "This program works only for alphabet" \
              " with at most {} letters.".format(ord('z')-ord('a'))
        raise Exception(msg)

    states = qit.Range(n_size)
    alphabet = qit.Range(a_size).map(lambda n: chr(ord('a') + n))
    finals = qit.Mapping(states, qit.Boolean()).filter(
        # at least one filnal state
        lambda m: any(map(lambda (state, is_final): is_final, m.iteritems())))
    delta = qit.Mapping(states * alphabet, states)

    fa = delta * finals
    fa_pairs = qit.UnorderedProduct((fa, fa))

    print "#states = {}; #actions = {}".format(n_size, a_size)
    print "count = {}".format("All" if count is None else count)
    print "total = {}".format(fa_pairs.size)

    if count is not None:
        source = fa_pairs.generate(count)
    else:
        source = fa_pairs.iterate()

    def is_witness(fa1_finals, fa2_finals):
        def f(state_depth_pair):
            s1 = state_depth_pair[0][0]
            s2 = state_depth_pair[0][1]
            return (fa1_finals[s1] and not fa2_finals[s2]) or \
                (not fa1_finals[s1] and fa2_finals[s2])
        return f

    def compute_eqlevel_of_two_fa(fa_pair):
        fa1 = FaLTS(fa_pair[0], alphabet)
        fa2 = FaLTS(fa_pair[1], alphabet)

        x = (fa1 * fa2).bfs((0, 0), pow(n_size, 2), True) \
            .filter(is_witness(fa1.final_states, fa2.final_states)) \
            .map(lambda s: s[1]).first(default=-1).run()
        return (fa_pair, x)

    results = source.map(compute_eqlevel_of_two_fa).max_all(lambda x: x[1]).run()
    (fa1, fa2), eq_level = results[0]
    print "\nEq level =", eq_level

    fa_to_graph(fa1).write("result-fa1.dot")
    fa_to_graph(fa2).write("result-fa2.dot")

class FaLTS(qit.LTS):

    def __init__(self, fa, actions):
        super(FaLTS, self).__init__(actions)
        self.delta = fa[0]
        self.final_states = fa[1]

    def step(self, state, action):
        return self.delta[(state, action)]

def fa_to_graph(fa):
    def rule_fn(lhs, rhs):
        state, action = lhs
        new_state = rhs
        label = str(action)
        return (state, label, new_state)
    final_states = [state for state, is_final in fa[1].iteritems() if is_final]
    return qit.ext.automata.transition_fn_to_graph(fa[0], rule_fn, 0, final_states)

if __name__ == "__main__":
     if len(sys.argv) < 2:
         count = 1e4
     else:
         count = Decimal(sys.argv[1])
     compute(3, 2, count)
