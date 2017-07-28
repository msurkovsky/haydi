from graph_tool.all import Graph, graph_draw

class Arc(object):

    def __init__(self, edge, node, data):
        self.node = node
        self.data = data

        self._edge = edge

# TODO: maybe I should make a wrapper Node above graph_tool.Vertex

class Node(object):

    def __init__(self, vertex, graph):
        self.vertex = vertex
        self.arcs = []

        self._graph = graph

    def add_arc(self, node, data=None):
        edge = self._graph.add_edge(self.vertex, node.vertex)
        self.arcs.append(Arc(edge, node, data))

    def arc_by_data(self, data):
        for arc in self.arcs:
            if arc.data == data:
                return arc
        return None

# class Node(object):

#     color = None
#     fillcolor = None
#     label = ""
#     shape = "circle"

#     def __init__(self, key):
#         self.key = key
#         self.arcs = []

#     def add_arc(self, node, data=None):
#         self.arcs.append(Arc(node, data))

#     def arc_by_data(self, data):
#         for arc in self.arcs:
#             if arc.data == data:
#                 return arc
#         return None

#     def merge_arcs(self, merge_fn):
#         if len(self.arcs) < 2:
#             return
#         node_to_arcs = {}
#         for arc in self.arcs[:]:
#             a = node_to_arcs.get(arc.node)
#             if a is None:
#                 node_to_arcs[arc.node] = arc
#             else:
#                 self.arcs.remove(arc)
#                 a.data = merge_fn(a.data, arc.data)

#     def __repr__(self):
#         return "<Node {}>".format(self.key)


class Graph(object):

    def __init__(self):
        self.graph = Graph()
        self._nodes = {}

        self._vnames = self.graph.new_vertex_property("string")
        self.graph.vertex_properties["name"] = self._vnames

    @property
    def size(self):
        return len(self._nodes)

    def has_node(self, key):
        return key in self._nodes

    def node_check(self, key):
        node = self._nodes.get(key)
        if node is not None:
            return (node, True)
        node = self._create_node(key)
        return (node, False)

    def node(self, key):
        node = self._nodes.get(key)
        if node is not None:
            return node
        node = self._create_node(key)
        return node

    def show(self):
        run_xdot(self.make_dot("G"))

    def write(self, filename):
        dot = self.make_dot("G")
        with open(filename, "w") as f:
            f.write(dot)

    def make_dot(self, name):
        # TODO: use graph_tool graph_draw method, xdot should be supported
        stream = ["digraph " + name + " {\n"]
        for node in self.nodes.values():
            extra = ""
            if node.color is not None:
                extra += " color=" + node.color
            if node.fillcolor is not None:
                extra += " style=filled fillcolor=" + node.fillcolor
            stream.append("v{} [label=\"{}\" shape=\"{}\"{}]\n".format(
                id(node), node.label, node.shape, extra))
            for arc in node.arcs:
                stream.append("v{} -> v{} [label=\"{}\"]\n".format(
                    id(node), id(arc.node), str(arc.data)))
        stream.append("}\n")
        return "".join(stream)

    def merge_arcs(self, merge_fn): # TODO: 
        raise Exception("Need a new implementation.")
        for node in self.nodes.values():
            node.merge_arcs(merge_fn)

    def _create_node(self, key):
        v = self.graph.add_vertex()
        self._vnames[v] = str(key)
        self._nodes[key] = v
        return v


def run_xdot(dot):
    import subprocess
    import tempfile
    with tempfile.NamedTemporaryFile() as f:
        f.write(dot)
        f.flush()
        subprocess.call(("xdot", f.name))
