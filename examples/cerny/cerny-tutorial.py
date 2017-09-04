import sys
sys.path.insert(0, "../../src/")

import haydi as hd

class DfaLTS(hd.DLTS):
   def __init__(self, deltaf, actions):
       hd.DLTS.__init__(self, actions)
       self.deltaf = deltaf

   def step(self, state_set, action):
       return frozenset(self.deltaf.get((state, action))
                        for state in state_set)

def compute(nstates, nsymbols):

   states = hd.Range(nstates)
   alphabet = hd.Range(nsymbols)

   max_steps = (n_states**3 - n_states) / 6

   def compute_shortest_sync_word(delta_f):
       dfa = DfaLTS(delta_f, alphabet)

       init_state = tuple(range(nstates))
       is_final = lambda (states, path): len(states) == 1 # singleton state
       is_shortest = lambda (states, path): -len(path)

       # (1) run BFS procedure
       # (2) filter only those paths that leads a final state
       # (3) take only shortest paths
       # sync_state, path = dfa.bfs_path(init_state, max_depth=max_steps)\
       #                       .filter(is_final)\
       #                       .max_all(is_shortest)
       results = dfa.bfs_path(init_state, max_depth=max_steps)\
                             .filter(is_final)
       if (len(results.run()) > 0):
           sync_state, path = results.max_all(is_shortest) # TODO: where is max all?

           #(transition function, the length of the shortest path, path, and synchronizing state)
           return (delta_f, len(path), path, sync_state)

       return None

   lrule = hd.Product((states, alphabet))
   deltaf = hd.Mappings(lrule, states)

   pipeline = deltaf.map(compute_shortest_sync_word).max(size=1)
   return pipeline.run()


if __name__ == "__main__":

   n_states = 3
   n_symbols = 2
   result = compute(n_states, n_symbols)
   print ("The maximal length of a minimal reset word for an "
          "automaton with {} states and {} symbols is {}.".
          format(n_states, n_symbols, result[1]))
   print result
