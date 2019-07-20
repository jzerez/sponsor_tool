class Graph():
    def __init__(self, root_node):
        self.root = root_node;
        self.nodes = {root_node, []};
    def add_node(self, node):
        neighbors = node.find_neighbors();
        self.nodes[node] = neighbors;
