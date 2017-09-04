
How to create your own program
==============================

This text presents an introductory guide that should help people to create their own program using **Haydi** framework. Haydi is a framework focusing on combinatorics problems. It allows users to formulate their problems easily and lets them check whether or not certain criteria are met. Moreover, instances confirming or contradicting the hypotheses are provided. The advantage of using Haydi is that the **resulting program can run directly on a supercomputer**, hence quite large structures can be examined. On the other hand, such infrastructure is not demanded and programs may run on one standard PC or distributively among a specific number of PCs.


Here a user can find a **step-by-step tutorial built upon a specific problem**; particulary, Cerny's hypothesis about `synchronizing words`_ in deterministic finite automata (DFA). The hypotesis states the question: *if a DFA has a synchronizing word, must it have one of length at most* :math:`\mathit{(n − 1)^2}` *?* This is an open question and the resulting program does not have an ambition to solve it. But it shows how much or perhaps how little effort it may take to create such a program and how large instances can be checked with it.

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
Before we can even start we need to **install Haydi**. Haydi is available on `GitHub`_ as an open-source project. It is distributed as a module that can be used in `Python`_ language. All the necessary information about instalaction and project's structure can be found on its page.

.. _GitHub: https://github.com/spirali/haydi
.. _Python: https://www.python.org/

Link the project and import Haidy modul
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First of all, when we start making our new program, we need to tell where Haydi modul is located and put the location into program's path. We can do this as follows:

>>> import sys
>>> sys.path.insert(0, "../src") # the program is placed in subdirectory of project's root

At this point we can import Haydi modul. It cointain all of the structures that are par of public API. All the structures with their description can be found in the `reference manual`_.

.. _reference manual: http://haydi.readthedocs.io/en/scheduler/index.html

>>> import haydi as hd

Prepare the structures
~~~~~~~~~~~~~~~~~~~~~~
Here we are in state when we succesfully installed Haydi, linked it to our program, and import the module. Now, we can start to make our program.

As stated in the introduction, Haydi is a suitable framework for programs that either systematicaly or randomly explore a bunch of a problem's instances and find those satisfying certain criteria. In this context, **the first task** we are going to address, is to define that *bunch* of the problem's instances.

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

At this moment, we have defined all basic structures we need to check whether or not a given DFA is synchronizable.

Compute synchronizing word
~~~~~~~~~~~~~~~~~~~~~~~~~~
The problem of finding the shortest synchronizing word is known to be NP-Complete; therefore, to compute the shortest synchronizing word we need to find a sequence, :math:`\sigma \in \Sigma^*` of as many simultaneous runs as the number of states. Each run starts in different state and the aim is to find the :math:`\sigma` sequence leading to one state.

In other words, we are looking for a path in a new automaton :math:`A'` that is build from the original one; the set of states makes power set of original automanton states, as the initial state is used a state representing a set containing all original states, and the set of final states are all singleton sets.

Such a system can be also viewed as a `Label Transition System`_ (LTS). For this purpose Haydi contains a basic (abstract) implementation of :class:`haydi.DLTS`, where *D* states for *Deterministic*. For a specific system we need to create a new class, that inherits from the basic *DLTS* and implement **step(state, action)** method. We define **DfaLTS** as follows:

.. _Label Transition System: https://en.wikipedia.org/wiki/Transition_system

>>> class DfaLTS(hd.DLTS):
>>>     def __init__(self, deltaf, actions):
>>>         hd.DLTS.__init__(self, actions)
>>>         self.deltaf = deltaf
>>>  
>>>     def step(self, state, action):
>>>         return self.deltaf[(state, action)]

Now, we can define a procedure that computes the shortest synchronizing word of a given DFA. Firstly, we instantiate DFA with **DfaLTS** and the definition of :math:`\mathbf{\delta}` **function**. Then we create :math:`n` -tuple, where :math:`n` is a number of states. For this purpose we use a specific implementation of product for DLTS; **DLTSProduct((dlts1[, dlts2[, ...]]))**. Such a system we can explore and find the shortest path from the initial state, :math:`\{q_1, q_2, \cdots, q_n\}, q_i \in Q, i \in \mathbb{N}`, to a singleton state, :math:`\{q\}, q \in Q`.

DLTS object supports a set of Breath First Search (BFS) procedures. In this case we use **bfs_path** that returns not only resulting found element (state) but also a path leading to it.

**TODO: document run (? actions)**

>>> def compute_shortest_sync_word(delta_f):
>>>    dfa = DfaLTS(delta_f, alphabet)
>>>    dfa_n_tuple = hd.DLTSProduct(tuple(dfa for i in range(nstates)))
>>>    
>>>    init_state = range(nstates)
>>>    is_final = lambda (states, path): len(set(states)) == 1 # singleton state
>>>    is_shortest = lambda (states, path): -len(path)
>>>    
>>>    # (1) run BFS procedure
>>>    # (2) filter only those paths that leads a final state
>>>    # (3) take only shortest paths
>>>    # (4) take one representative
>>>    sync_state, path = dfa_n_tuple.bfs_path(init_state)\
>>>                                  .filter(is_final)\
>>>                                  .max_all(is_shortest)\
>>>                                  .take(1)\
>>>                                  .run()
>>>                    
>>>    #(transition function, the length of the shortest path, path, and synchronizing state)
>>>    return (delta_f, len(path), path, sync_state)

We have all parts we need and cat put it alltogether into resulting program.

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
>>>        return self.deltaf[(state, action)]
>>>    
>>> def compute(nstates, nsymbols):
>>>    
>>>    states = hd.Range(nstates)
>>>    alphabet = hd.Range(nsymbols)
>>> 
>>>    print states, alphabet
>>>    def compute_shortest_sync_word(delta_f):
>>>        dfa = DfaLTS(delta_f, alphabet)
>>>        dfa_n_tuple = hd.DLTSProduct(tuple(dfa for i in range(nstates)))
>>>        print dfa_n_tuple
>>> 
>>>        init_state = tuple(range(nstates))
>>>        is_final = lambda (states, path): len(set(states)) == 1 # singleton state
>>>        is_shortest = lambda (states, path): -len(path)
>>> 
>>>        # (1) run BFS procedure
>>>        # (2) filter only those paths that leads a final state
>>>        # (3) take only shortest paths
>>>        sync_state, path = dfa_n_tuple.bfs_path(init_state)\
>>>                                      .filter(is_final)\
>>>                                      .max_all(is_shortest) # TODO: what's the result of max_all?
>>>        print sync_state, path
>>>        #(transition function, the length of the shortest path, path, and synchronizing state)
>>>        return (delta_f, len(path), path, sync_state)
>>>    
>>>    lrule = hd.Product((states, alphabet))
>>>    deltaf = hd.Mapping(lrule, states)
>>>    
>>>    return deltaf.take(1).map(compute_shortest_sync_word).run()
>>>    
>>> 
>>> if __name__ == "__main__":
>>>    
>>>    result = compute(3, 2)
>>>    print result
