#TODO: how to skip slow tests http://blog.devork.be/2009/12/skipping-slow-test-by-default-in-pytest.html

import haydy as hd
import syn as syn_solver

def test_small_example1():
    n_events = 2
    searched_lts = hd.DLTSFromGraph(hd.Graph([
        (0, 0, 1),
        (0, 1, 2),
        (1, 1, 3),
        (2, 0, 3),
        (3, 1, 4)
    ]), hd.Range(n_events))
    init_state = 0

    results = syn_solver.compute(searched_lts,
                                 init_state,
                                 n_events,
                                 1, # maximal number of input arc's weight
                                 1, # maximal number of output arc's weight
                                 1) # maximal number of tokens in initial marking

    results = results.run()
    assert len(results) == 2

    # TODO assert the resulting values
    r = results[0]
    # ...

def test_small_example2(): # the same test as small_example1 but tasked in a different way
    n_events = 2
    solution = ( # pn system with RG: 0->1->1 | 1->0->1
        # m0
        { 0: 1, 1: 1 },
        # wi
        {(0, 0): 1,
         (0, 1): 0,
         (1, 0): 0,
         (1, 1): 1},
        # wo
        {(0, 0): 0,
         (0, 1): 1,
         (1, 0): 0,
         (1, 1): 0}
    )
    searched_lts = PnLTS(solution, hd.Range(n_events))
    init_state = hashabledict({0: 1, 1: 1})

    results = syn_solver.compute(searched_lts,
                                 init_state,
                                 n_events,
                                 1,
                                 1,
                                 1)

    results = resutls.run()
    assert len(results) == 2

    # TODO: the samem as before; i.e. assert the results


def test_3letter_cycle1(): # real test - 3letter cycle
    n_events = 3
    searched_lts = hd.DLTSFromGraph(hd.Graph([
        (0, 0, 1),
        (1, 0, 2),
        (2, 1, 3),
        (3, 1, 4),
        (4, 2, 5),
        (5, 2, 0),
    ]), hd.Range(n_events))
    init_state = 0

    results = syn_solver.compute(searched_lts,
                                 init_state,
                                 n_events,
                                 2,
                                 2,
                                 2)

    results = resutls.run()
    # assert len(results) == 2 # TODO: assert according to right number

    # TODO:  assert the results

def test_3letter_cycle2():
    solution = ( # pn system with RG: 0->0->1->1->2->2->0 ...
        # m0
        {0: 2, 1: 0, 2: 2},
        # wi
        {(0, 0): 2,
         (0, 1): 1,
         (1, 0): 0,
         (1, 1): 2,
         (0, 2): 0,
         (2, 0): 1,
         (2, 2): 2,
         (1, 2): 1,
         (2, 1): 0},
        # wo
        {(0, 0): 2,
         (0, 1): 1,
         (1, 0): 0,
         (1, 1): 2,
         (0, 2): 0,
         (2, 0): 1,
         (2, 2): 2,
         (1, 2): 1,
         (2, 1): 0}
    )
    searched_lts = PnLTS(solution, hd.Range(n_events))
    init_state = hashabledict({0: 2, 1: 0, 2: 2})

    results = syn_solver.compute(searched_lts,
                                 init_state,
                                 n_events,
                                 2,
                                 2,
                                 2)

    results = resutls.run()
    # assert len(results) == 2 # TODO: assert according to right number

    # TODO:  assert the results
