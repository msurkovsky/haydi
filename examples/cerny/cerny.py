
# Script for verifying Cerny's conjuncture
#
# This programs goes over finite state automata of a given
# size and finds the maximal length of a minimal reset word
import sys
sys.path.insert(0, "/home/sur096/projects/haydi/src/")

import haydi as hd
from haydi.algorithms import search
from haydi.ext.automata import transition_fn_to_graph


def main():

    n_states = 4   # Number of states
    n_symbols = 2  # Number of symbols in alphabet

    # states = hd.USet(n_states, "q")  # set of states q0, q1, ..., q_{n_states}
    # alphabet = hd.USet(n_symbols, "a")  # set of symbols a0, ..., a_{a_symbols}
    states = hd.Range(n_states)
    alphabet = hd.Range(n_symbols)

    # Mappings (states * alphabet) -> states
    delta = hd.Mappings(states * alphabet, states)

    # Let us precompute some values that will be repeatedly used
    init_state = frozenset(states)
    max_steps = (n_states**3 - n_states) / 6

    def check_automaton(delta):
        # This function takes automaton as a transition function and
        # returns the minimal length of synchronizing word or 0 if there
        # is no such word

        def step((state, path), depth):
            # A step in bread-first search; gives a set of states
            # and return a set reachable by one step
            for a in alphabet:
                yield (frozenset(delta[(s, a)] for s in state), path + (a,))

        delta = delta.to_dict()

        bfs_val = search.bfs(
            (init_state, ()),
            step,
            lambda (state, path), depth: (depth, path) if len(state) == 1 else None,
            max_depth = max_steps,
            not_found_value=(0, ()))

        return (bfs_val, delta)

        # return search.bfs(
        #     init_state,  # Initial state
        #     step,        # Step
        #     lambda state, depth: depth if len(state) == 1 else None,
        #                  # Run until we reach a single state
        #     max_depth=max_steps,  # Limit depth of search
        #     not_found_value=0)    # Return 0 when we exceed depth limit

    # Create & run pipeline
    # pipeline = delta.cnfs().map(check_automaton).max(size=1)
    pipeline = delta.generate()\
                    .map(check_automaton)\
                    .take(1000)\
                    .max(value_fn=lambda ((s, path), delta): s,
                         size=1)

    (size, path), delta = result = pipeline.run()[0]

    # graph = transition_fn_to_graph(
    #     delta,
    #     lambda (s1, a), s2: (s1, a, s2),
    #     init_state
    # )
    # graph.show()

    print ("The maximal length of a minimal reset word for an "
           "automaton with {} states and {} symbols is {}.".
           format(n_states, n_symbols, result))


if __name__ == "__main__":
    main()
