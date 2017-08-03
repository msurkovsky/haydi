from collections import Iterable
from haydi.base.graph import Graph
from haydi.base.exception import HaydiException
from haydi.base.basictypes import Atom


class GraphRenderer(object):

    def __init__(self, graph_structure):
        if not isinstance(graph_structure, Iterable):
            raise Exception("Invalid graph structure."
                            " It is expected a list of edges.")

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
                    " It is expected that each edge consists of two vertices.")

            # format data values into edge label
            if labeling_edge_fn is None:
                edge_label = ", ".join(map(str, data))
            else:
                edge_label = labeling_edge_fn(tuple(data))

            # couple of nodes and string describing edge label
            return (tuple(nodes), edge_label)


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

        for node in self._nodes: # add all nodes into graph
            n = g.node(node)
            n.label = self._node_labels[node]

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

                if not isinstance(to_nodes, Iterable):
                    to_nodes = (to_nodes,)

                for n in to_nodes:
                    n2 = g.node(n)
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
        """
        CAUTION: Automatic identification of nodes take the information about
                 them from edges. If there are nodes not connected by any edges,
                 then such nodes are not included and user have to specify the
                 set of nodes manually.
        """
        # NOTE: is supposed that all nodes are of the same type

        nodes = set()

        # == PSEUDO CODE ==
        # if graph_structure represents dictionary then:
        #     1. use keys as nodes # starting nodes
        #     2. add nodes that are only the ends of edges # ending node
        # else:

        # for each element of graph_structure:
        #     1. count the number of different types in structure describing edge
        #     2. pick the types that appears exactly twice (edge vertices)
        #     2.1. if there are more types with exactly two appearances:
        #             FAIL; can't guess
        #     2.2. else:
        #             place these elements among nodes

        # == IMPLEMENTATION ==
        if isinstance(graph_structure, dict):
            nodes = nodes.union(graph_structure.keys())

            for elem in graph_structure.itervalues():
                if isinstance(elem, Iterable):
                    nodes = nodes.union(elem)
                else:
                    nodes.add(elem)
        else:
            if graph_structure:
                # NOTE: each edge has to consists of two nodes at least
                sample_edge = graph_structure[0]

                counts = {v: 0 for v in set(map(type, sample_edge))}
                for elem in sample_edge:
                    counts[type(elem)] += 1

                relevant = filter(lambda (t, c): c == 2, counts.iteritems())
                if len(relevant) != 1:
                    raise Exception(
                        "Unable to identify nodes from the given structure."
                        " Please specify nodes manually.")

                node_t, _ = relevant.pop()
                for edge in graph_structure:
                    nodes = nodes.union(elem for elem in edge
                                        if isinstance(elem, node_t))

        return (nodes, get_default_node_labels(nodes))


def get_default_node_labels(nodes):
    return {node: str(node) for node in nodes}
