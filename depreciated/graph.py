from Node import Node
class Graph():
    def __init__(self, url, domain):
        self.root = Node(url, domain);
        self.node_graph = {}
        self.depths = {self.root.url:self.root.depth}
        self.add_node(self.root)
        self.emails = set()

    def add_node(self, node):
        self.node_graph[node] = [];
        for url in node.find_links():
            if url in self.depth.keys():
                self.depths[url] = min([self.depths[url], node.depth+1])
            else:
                self.depths[url] = node.depth+1
            self.node_graph[node].append(Node(url, self.root.domain, self.depths[url]))
        for email in node.emails:
            self.emails.add(email)

if __name__ == "__main__":
    g = Graph(Node("https://cimquest-inc.com/"))
    print(len(g.all_nodes))
