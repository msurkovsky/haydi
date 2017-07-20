from haydi.base.graph import Graph
from haydi.base.exception import HaydiException

class GRMissingNodeDomainException(HaydiException):
    pass

class GRMissingEdgeDomainException(HaydiException):
    pass

class GraphsRenderer(object):

    def __init__(self, domain):
        self.data_domain = domain

        self.node_domain = None
        self.edge_domain = None
        pass

    def nodes(self, domain, colors=None):
        self.node_domain = domain
        # TODO: colors
        return self

    def edges(self, domain):
        self.edge_domain = domain
        return self

    def render(self):
        pass

    def _identify_graph_structure(self):
        if node_domain is None:
            pass # TODO:

        if self.edge_domain is None:
            pass # TODO:

        if self.node_domain is None:
            raise GRMissingNodeDomainException("Identification of node domain "
                                               "failed.")
        if self.edge_domain is None:
            raise GRMissingEdgeDomainException("Identification of edge domain "
                                               "failed.")