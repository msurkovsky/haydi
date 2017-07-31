from collections import Iterable
from haydi.base.graph import Graph
from haydi.base.exception import HaydiException
from haydi.base.basictypes import Atom


class GraphRenderer(object):

    def __init__(self, graph_structure):
        self.graph_structure = tuple(graph_structure)

        self._nodes = None
        self._edges = None

    def nodes(self, nodes, labels=None):
        """Set the set of nodes. All graphs are consisted from the same
        collection of nodes.
        """
        if labels is None:
            labels = get_default_node_labels(nodes)
        self._node_labels = labels

        self._nodes = nodes
        return self

    def assemble_graph(self, labeling_edge_fn=None):
        """Tries to assemble haydi.base.graph.Graph from given structure."""

        def assemble_edge(e_structure, vertices, labeling_edge_fn):
            nodes = []
            data = []

            # separate edge vertices from data info
            for elem in e_structure:
                if elem in vertices:
                    nodes.append(elem)
                else:
                    data.append(elem)

            if len(nodes) != 2:
                raise Exception(
                    "The edge consists of more or less than two vertices."
                    " Try to use ###NAME### function to precise edge.") # TODO: support a mapping function or so that pick up important things to constructing an edge

            # format data values into edge label
            if labeling_edge_fn is None:
                edge_label = ", ".join(map(str, data))
            else:
                edge_label = labeling_edge_fn(tuple(data))

            # couple of nodes and string describing edge label
            return (tuple(nodes), edge_label)


        # NOTE: first implementation works only with nodes; manually specified edges are ignored.

        if self._nodes is None: # attempt to automatically identify
                                # nodes if not already specified
            nodes, labels = self._identify_nodes(self.graph_structure)

            if not nodes:
                raise Exception(
                    "Unknown nodes. Automatic identification failed."
                    " Please specify nodes manually.")

            self._nodes = nodes
            self._node_labels = labels

        g = Graph()

        # parse mappings in format `{from node : to node/[to nodes]}`
        if isinstance(self.graph_structure, dict): # graphs as mappings; ORIENTED
            if not all(k in self._nodes in self.graph_structure.keys()):
                raise Exception(
                    "There are nodes in structure out of"
                    " specified set of nodes.")

            for from_node, to_nodes in self.graph_structure.iteritems():
                if isinstance(to_nodes, dict):
                    raise Exception("Unknown format of edge.")

                n1 = g.node(from_node)
                n1.label = self._node_labels[from_node]

                if not isinstance(to_nodes, Iterable):
                    to_nodes = (to_nodes,)

                for n in to_nodes:
                    n2 = g.node(n)
                    n2.label = self._node_labels[n]
                    n1.add_arc(n1) # TODO, solve data; how to specify data within dict; tuple, list of tuples

        else: # collection of edges; (NOT-)ORIENTED
            directed = True
            for e in self.graph_structure:
                (n1, n2), data = assemble_edge(e, self._nodes, labeling_edge_fn)
                v1 = g.node(n1)
                v1.label = self._node_labels[n1]
                v2 = g.node(n2)
                v2.label = self._node_labels[n2]

                v1.add_arc(v2, data)
                if isinstance(e, set):
                    directed = False
            g.set_directed(directed)
        return g

    def _identify_nodes(self, graph_structure):
        # NOTE: - nodes should be of the same type; does it make sense to have a list of nodes like: (1,2,"hello", (1,2,3), ...)? -> imho NO

        nodes = set()

        if isinstance(graph_structure, dict):
            nodes = nodes.union(graph_structure.keys())

            for elem in graph_structure.itervalues():
                if isinstance(elem, Iterable):
                    nodes = nodes.union(elem)
                else:
                    nodes.add(elem)
        else:
            for edge in graph_structure:
                counts = {v: 0 for v in set(map(type, edge))} # TODO: what a node is tuple?
                for elem in edge:
                    counts[type(elem)] += 1

                relevant = filter(lambda (t, c): c == 2, counts.iteritems())
                if len(relevant) != 1:
                    raise Exception(
                        "Unable to identify nodes from the given structure."
                        " Please specify nodes manually.")
                node_t, _ = relevant.pop()
                nodes = nodes.union(e for e in edge if isinstance(e, node_t))

        return (nodes, get_default_node_labels(nodes))


def get_default_node_labels(nodes):
    return {node: str(node) for node in nodes}
