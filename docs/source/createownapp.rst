
How to create your own program
==============================

This text presents an introductory guide that should help people to create their own program using **Haydi** framework. Here a user can find a **step-by-step tutorial built upon a specific problem**; particulary, Cerny's hypothesis about `synchronizing words`_ in deterministic finite automata (DFA). The hypotesis states the question: *if a DFA has a synchronizing word, must it have one of length at most* :math:`\mathit{(n − 1)^2}` *?* This is an open question and the resulting program does not have an ambition to solve it. But it shows how much or rather how little effort it may take to create such a program and how large instances can be checked with it.

.. _synchronizing words: https://en.wikipedia.org/wiki/Synchronizing_word

Definitions
-----------

**Deterministic finite automaton**, is a 5-tuple, :math:`(Q,\Sigma, \delta, q_0, F)`, consisting of:

 - :math:`Q`, a finite set of states
 - :math:`\Sigma`, a finite set of symbols called aplphabet
 - :math:`\delta: Q \times S \to Q`, a transition function
 - :math:`q_0 \in Q`, an initial state,
 - :math:`F \subseteq Q`, a subset of final states
 

**Synchronizing word**, is a finite sequnce of symbols from alphabet, :math:`\sigma \in \Sigma^*`, with a property that no matter at which state an automaton starts, following :math:`\sigma` word leads to the same state, i.e. :math:`\forall q \in Q, \exists q' \in Q: q \xrightarrow{\sigma} q'`.

Making a program
----------------
Here we start making our first program using Haydi framwork. The problem of *synchronizing words* is well-known among people from the area of theoretical computer science. This problem was chosen because it is easily explainable to people while containing enough complexity; such programm will contain most of the structures and constructs that can help you to create your own program.

Before we start
~~~~~~~~~~~~~~~
Before we can even start we need to **install Haydi**, The installation is described :doc:`here <./install>`. 

Link the project and import Haidy modul
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All the structures that are part of public API are located in package ``haydi``, hence all of the program starts with a line like this one:

>>> import haydi as hd

Prepare the structures
~~~~~~~~~~~~~~~~~~~~~~
Here we are in a state when we successfully installed Haydi and import the basic module. Now, we can start to make our program.

Haydi is a suitable framework for programs that either systematicaly or randomly explore a bunch of a problem's instances and find those satisfying certain criteria. In this context, **the first task** we are going to address, is to define that *bunch* of the problem's instances.

The very basic structure in Haydi is :class:`haydi.Domain`. It represents a common interface for defining a set of data and how to work with it. A domain can be created by using one from the predefined or as composition of those already created. An example of simple domain is :class:`haydi.Range`, that defines a sequence of integers going from *start* upto *end* with *step* between values.

To find a synchronizing automanton, we need to define its structure. From definition we see that finite automaton is 5-tuple of specific items. First two are a set of states :math:`Q` and alphabet :math:`\Sigma`. We can describe them by using *Range* domain as follows.

>>> # our structure is describing all finite automata with three states and two symbols in alphabet.
>>> nstates = 3  # number of states
>>> nsymbols = 2 # number of letters in alphabet
>>>
>>> states = hd.Range(nstates)
>>> alphabet = hd.Range(nsymbols)

The thrid item is transition function. The definition states that from a pair of state and symbol we derive a new state. We split definition of the transition function into two steps. First of all, we define its left-hand side. To do that we need to create Cartesian product upon the sets of *states* and *alphabet*. Cartesian product is represented by :class:`haydi.Product` domain. For the right-hand side we already have the domain, *states*. Now we can put both sides together via :class:`haidy.Mapping`.

>>> lrule = hd.Product((states, alphabet)) # define the left rule of the transition function
>>> 
>>> # alternatively we can define lrule by using a '*' operator:
>>> # lrule = states * alphabet
>>> 
>>> deltaf = hd.Mapping(lrule, states)
>>>
>>> # upper bound of the sync word maximal length
>>> max_steps = (n_states**3 - n_states) / 6

At this moment, we have defined all basic structures we need to check whether or not a given DFA is synchronizable.

Compute synchronizing word
~~~~~~~~~~~~~~~~~~~~~~~~~~
The problem of finding the shortest synchronizing word is known to be NP-Complete; therefore, to compute the shortest synchronizing word we need to find a sequence, :math:`\sigma \in \Sigma^*` of as many simultaneous runs as the number of states. Each run starts in different state and the aim is to find the :math:`\sigma` sequence leading to one state.

In other words, we can imagine that we have as many copies of the automaton as the number of states that run concurrently, but each one starts at different state. The run of such system ends when all automata reach the same state.

We are not going to run concurrent copies of an automaton, but only one automaton with initial state represented by set containing all of the automanton's states. The run ends when the size of the set is reduced to one; reach a singleton set.

Such a system can be also viewed as a `Label Transition System`_ (LTS). For this purpose Haydi contains a basic (abstract) implementation of :class:`haydi.DLTS`, where *D* states for *Deterministic*. A user can derive from this class, implement `step` method, and use such a structure; or there is already implemented a search algorithm upon an LTS system in package ``haydi.algorithms``.

.. _Label Transition System: https://en.wikipedia.org/wiki/Transition_system

The first option may look as follows. Firstly we define class ``DfaLTS`` and then a function computing the shortest synchronization word using it.


>>> class DfaLTS(hd.DLTS):
>>>     def __init__(self, deltaf, actions):
>>>         hd.DLTS.__init__(self, actions)
>>>         self.deltaf = deltaf
>>>  
>>>     def step(self, state_set, action):
>>>         return frozenset(self.deltaf[(state, action)]
>>>                          for state in state_set)
>>>
>>>
>>> def compute_shortest_sync_word(delta_f):
>>>    dfa = DfaLTS(delta_f, alphabet)
>>>    
>>>    init_state = range(nstates)
>>>    is_final = lambda (states, path): len(states) == 1 # singleton state
>>>    is_shortest = lambda (states, path): -len(path)
>>>    
>>>    # (1) run BFS procedure
>>>    # (2) filter only those paths that leads a final state
>>>    # (3) take only shortest paths
>>>    # (4) take one representative
>>>    sync_state, path = dfa.bfs_path(init_state, max_depth=max_steps)\
>>>                          .filter(is_final)\
>>>                          .max_all(is_shortest)\
>>>                          .take(1)\
>>>                          .run()
>>>                    
>>>    #(transition function, the length of the shortest path, path, and synchronizing state)
>>>    return (delta_f, len(path), path, sync_state)

The second option using ``search`` function from ``haydi.algorithms`` would look very similarly.

>>> def check_automaton(delta):
>>>     def step(state, depth):
>>>         # A step in bread-first search; gives a set of states
>>>         # and return a set reachable by one step
>>>         for a in alphabet:
>>>             yield frozenset(delta[(s, a)] for s in state)
>>>
>>>     delta = delta.to_dict()
>>>     return search.bfs(
>>>         init_state,  # Initial state
>>>         step,        # Step
>>>         lambda state, depth: depth if len(state) == 1 else None,
>>>                      # Run until we reach a single state
>>>         max_depth=max_steps,  # Limit depth of search
>>>         not_found_value=0)    # Return 0 when we exceed depth limit

Now, we have all parts we need and cat put it alltogether into resulting program.

Entire program
~~~~~~~~~~~~~~

>>> import haydi as hd
>>> 
>>> class DfaLTS(hd.DLTS):
>>>    def __init__(self, deltaf, actions):
>>>        hd.DLTS.__init__(self, actions)
>>>        self.deltaf = deltaf
>>> 
>>>    def step(self, state, action):
>>>        return frozenset(self.deltaf[(state, action)]
>>>                         for state in state_set)
>>>    
>>> def compute(nstates, nsymbols):
>>>    
>>>    states = hd.Range(nstates)
>>>    alphabet = hd.Range(nsymbols)
>>> 
>>>    def compute_shortest_sync_word(delta_f):
>>>        dfa = DfaLTS(delta_f, alphabet)
>>>
>>>        init_state = range(nstates)
>>>        is_final = lambda (states, path): len(states) == 1 # singleton state
>>>        is_shortest = lambda (states, path): -len(path)
>>> 
>>>        # (1) run BFS procedure
>>>        # (2) filter only those paths that leads a final state
>>>        # (3) take only shortest paths
>>>        sync_state, path = dfa_n_tuple.bfs_path(init_state, max_depth=max_states)\
>>>                                      .filter(is_final)\
>>>                                      .max_all(is_shortest)
>>>
>>>        #(transition function, the length of the shortest path, path, and synchronizing state)
>>>        return (delta_f, len(path), path, sync_state)
>>>    
>>>    lrule = hd.Product((states, alphabet))
>>>    deltaf = hd.Mapping(lrule, states)
>>>    
>>>    pipeline deltaf.map(compute_shortest_sync_word).max(size=1)
>>>    return pipeline.run()
>>>    
>>> 
>>> if __name__ == "__main__":
>>>    
>>>    n_states = 3
>>>    n_symbols = 2
>>>    result = compute(n_states, n_symbols)
>>>    print ("The maximal length of a minimal reset word for an "
>>>           "automaton with {} states and {} symbols is {}.".
>>>           format(n_states, n_symbols, result[1]))
>>>    print result
