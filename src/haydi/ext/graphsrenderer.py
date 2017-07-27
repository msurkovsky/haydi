from collections import Iterable
from haydi.base.graph import Graph
from haydi.base.exception import HaydiException
from haydi.base.basictypes import Atom

class GRException(HaydiException):
    pass


class GRWrongEdgeFormatException(GRException):
    pass


class GRMissingNodeDomainException(GRException):
    pass


class GRMissingEdgeDomainException(GRException):
    pass

PRIMITIVE_TYPES = (int, str, Atom)

def is_primitive(type):
    return type in PRIMITIVE_TYPES

class InstGraphRenderer(object):

    def __init__(self, g_structure):
        self.g_structure = tuple(g_structure)

        # TODO: even these two parameters should respect a hierarchy
        # If it was like this, it means that GraphRenderer works for one graph!

        self.nodes = None # however nodes and edges should be compound for the category, i.e.: (nodes, edges)=G
        self.edges = None

    def nodes(self, nodes):
        """Set the set of nodes. All graphs are consisted from the same
        collection of nodes.
        """

        self.nodes = nodes
        return self

    def edges(self, edges): # TODO: do I need such a method?
        raise Exception("Not implemented yet.")
        # """Set edges data.

        # - imho, i don't want the entire set of edges, especially not in a case where it would set of sets of edges.
        # - a natural information is about a type, i.e. description saying **how one edge looks**.

        # (?) What if the data is a set of graphs? -> would 'edges' be a set of lists of edges?
        # """
        # self.edges = edges
        # return self

    def assemble_graph(self):
        def assemble_edge(e_structure, vertices, data_print=lambda data: str(data)):
            nodes = []
            data = []

            for elem in e_structure:
                if elem in vertices:
                    nodes.append(elem)
                else:
                    data.append(elem)

            if len(nodes) != 2:
                raise GRWrongEdgeFormatException(
                    "The edge consists of more or less than two vertices."
                    " Try to use ###NAME### function to precise edge.")

            return (tuple(nodes), ", ".join(map(data_print, data)))


        # NOTE: first implementation works only with nodes; edges are ignored.

        # if not self.nodes: # not known nodes
        #     nodes = set()
        #     if depth == 1:
        #         nodes.union(identify_nodes_in_graph(self.data))
        #     elif depth == 2:
        #         for g in self.data:
        #             nodes.union(identify_nodes_in_graph(g))
        #     self.nodes = nodes

        g = Graph()
        if isinstance(self.graph_structure, dict): # graphs as mappings; ORIENTED
            if not all(k in self.nodes in self.graph_structure.keys()):
                raise GRMissingNodeDomainException(
                    "There are nodes in structure out of"
                    " specified set of nodes.")

            for from_node, to_nodes in self.graph_structure.iteritems():
                if isinstance(to_nodes, dict):
                    raise GRWrongEdgeFormatException("Unknown format of edge.")

                n1 = g.node(from_node)

                if not isinstance(to_nodes, Iterable):
                    to_nodes = (to_nodes,)

                for n in to_nodes:
                    n2 = g.node(n)
                    n1.add_arc(n1) # TODO, solve data

        else: # collection of edges; (NOT-)ORIENTED
            for e in self.graph_structure:
                (n1, n2), data = assemble_edge(e, self.nodes)
                n1 = g.node(n1)
                n2 = g.node(n2)
                n1.add_arc(n2, data)
                if isinstance(e, set):
                    n2.add_arc(n1, data)
        return g

    # #TODO: compose HTML page consisting of processed graphs

    def _identify_nodes(self, graph_structure):
        # NOTE: - nodes should be of the same type; does it make sense to have a list of nodes like: (1,2,"hello", (1,2,3), ...)? -> imho NO
        pass
    # def _identify_graph_structure(self):
    #     depth = 0 # how deep has to go in a structure to iterate over edges
    #     if self.nodes is None:
    #         if self.edges is None:
    #              = self.data
    #             # try to find edges
    #             if
    #         else:
    #             pass

    #     # at this point nodes are already known
    #     if self.edges is None:
    #         pass # TODO:

    #     if self.nodes is None:
    #         raise GRMissingNodeDomainException("Identification of node domain "
    #                                            "failed.")
    #     if self.edges is None:
    #         raise GRMissingEdgeDomainException("Identification of edge domain "
    #                                            "failed.")
    #     return depth


class GraphsRenderer(object):

    def __init__(self, domain, values=None):
        self.data_domain = domain
        if values is None:
            values = domain.run()
        self.values = tuple(values)

        self.node_domain = None
        self.edge_domain = None

    def nodes(self, domain, colors=None):
        self.node_domain = domain
        # TODO: colors
        return self

    def edges(self, domain, reorder_edge_params_fn=None):
        """Set edges domain.

        Parameters
        ----------
        domain : haydi.Domain

        reorder_edge_params_fn : function taking three parameters (the last one is optional) and returns triple with starting node, ending node, and edge's data. If such an order in original domain is not preserved a user may change it by this function.
        """

        self.edge_domain = domain

        if reorder_edge_params_fn=None:
            reorder_edge_params_fn = lambda (n1, n2, data=None): (n1, n2, data)
        self.reorder_edge_params_fn = reorder_edge_params_fn

        return self

    def filter(self): # pick up only a specific category
        pass

    def render(self):
        def assemble_graph(edges):
            pass

        def process_category (depth, data):
            c_data = []
            if depth > 1:
                for c in data:
                    c_data.append(process_category(depth-1, c))
                category.append(c_data)

            else if depth == 1:
                g = assemble_graph(data)
                c_data.append(g)

            else:
                raise GRException("Cannot process separate edges")

            return c_data

        depth = self._identify_graph_structure()

        #TODO: compose HTML page consisting of processed graphs
        return process_category(depth, self.values)


    def _identify_graph_structure(self):
        depth = 0 # how deep has to go in a structure to iterate over edges
        if self.node_domain is None:
            if self.edge_domain is None:
                 = self.data
                # try to find edges
                if
            else:
                pass

        # at this point nodes are already known
        if self.edge_domain is None:
            pass # TODO:

        if self.node_domain is None:
            raise GRMissingNodeDomainException("Identification of node domain "
                                               "failed.")
        if self.edge_domain is None:
            raise GRMissingEdgeDomainException("Identification of edge domain "
                                               "failed.")
        return depth
