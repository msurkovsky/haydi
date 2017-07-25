from haydi.base.graph import Graph
from haydi.base.exception import HaydiException

class GRException(HaydiException):
    pass

class GRMissingNodeDomainException(GRException):
    pass

class GRMissingEdgeDomainException(GRException):
    pass

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
