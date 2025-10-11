# dlab/graphs.py

class Graph:
    def __init__(self, vertices=0):
        self.V = vertices
        self.adj_list = {i: [] for i in range(vertices)}
    
    def add_vertex(self):
        """Add a new vertex."""
        self.V += 1
        self.adj_list[self.V - 1] = []

    def add_edge(self, u, v):
        """Add an undirected edge."""
        self.adj_list[u].append(v)
        self.adj_list[v].append(u)

    def remove_edge(self, u, v):
        """Remove an undirected edge."""
        if v in self.adj_list[u]:
            self.adj_list[u].remove(v)
        if u in self.adj_list[v]:
            self.adj_list[v].remove(u)

    def display(self):
        """Display adjacency list."""
        for vertex in self.adj_list:
            print(f"{vertex}: {self.adj_list[vertex]}")

class UndirectedGraph(Graph):
    # Inherits all methods from Graph
    pass

class DirectedGraph(Graph):
    def add_edge(self, u, v):
        """Add a directed edge."""
        self.adj_list[u].append(v)

    def remove_edge(self, u, v):
        """Remove a directed edge."""
        if v in self.adj_list[u]:
            self.adj_list[u].remove(v)

    def display(self):
        """Display adjacency list."""
        for vertex in self.adj_list:
            print(f"{vertex}: {self.adj_list[vertex]}")

class WeightedGraph:
    def __init__(self, vertices=0, directed=False):
        self.V = vertices
        self.adj_list = {i: [] for i in range(vertices)}  # list of (neighbor, weight)
        self.directed = directed

    def add_vertex(self):
        """Add a new vertex."""
        self.V += 1
        self.adj_list[self.V - 1] = []

    def add_edge(self, u, v, weight):
        """Add a weighted edge."""
        self.adj_list[u].append((v, weight))
        if not self.directed:
            self.adj_list[v].append((u, weight))

    def remove_edge(self, u, v):
        """Remove an edge."""
        self.adj_list[u] = [pair for pair in self.adj_list[u] if pair[0] != v]
        if not self.directed:
            self.adj_list[v] = [pair for pair in self.adj_list[v] if pair[0] != u]

    def display(self):
        """Display adjacency list."""
        for u in self.adj_list:
            print(f"{u}: {self.adj_list[u]}")

class BipartiteGraph:
    def __init__(self):
        self.set1 = set()
        self.set2 = set()
        self.adj_list = {}

    def add_edge(self, u, v):
        """Add an edge between vertices in set1 and set2."""
        if u not in self.set1:
            self.set1.add(u)
        if v not in self.set2:
            self.set2.add(v)
        if u not in self.adj_list:
            self.adj_list[u] = []
        self.adj_list[u].append(v)

    def display(self):
        """Display bipartite graph details."""
        print("Set1:", self.set1)
        print("Set2:", self.set2)
        print("Edges:")
        for u in self.adj_list:
            print(f"{u} -> {self.adj_list[u]}")