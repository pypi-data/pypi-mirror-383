# graph_representations.py

class AdjacencyMatrix:
    def __init__(self, vertices=0, directed=False):
        self.V = vertices
        self.directed = directed
        self.matrix = [[0] * vertices for _ in range(vertices)]
    
    def add_vertex(self):
        """Add a new vertex."""
        self.V += 1
        # Expand existing rows
        for row in self.matrix:
            row.append(0)
        # Add new row
        self.matrix.append([0] * self.V)
    
    def add_edge(self, u, v, weight=1):
        """Add an edge with optional weight."""
        self.matrix[u][v] = weight
        if not self.directed:
            self.matrix[v][u] = weight
    
    def remove_edge(self, u, v):
        """Remove an edge."""
        self.matrix[u][v] = 0
        if not self.directed:
            self.matrix[v][u] = 0
    
    def display(self):
        """Display the adjacency matrix."""
        print("Adjacency Matrix:")
        for row in self.matrix:
            print(" ".join(map(str, row)))


class AdjacencyList:
    def __init__(self, vertices=0, directed=False):
        self.V = vertices
        self.directed = directed
        self.adj_list = {i: [] for i in range(vertices)}
    
    def add_vertex(self):
        """Add a new vertex."""
        self.V += 1
        self.adj_list[self.V - 1] = []
    
    def add_edge(self, u, v, weight=None):
        """Add an edge. For weighted graphs, specify weight."""
        if weight is not None:
            self.adj_list[u].append((v, weight))
            if not self.directed:
                self.adj_list[v].append((u, weight))
        else:
            self.adj_list[u].append(v)
            if not self.directed:
                self.adj_list[v].append(u)
    
    def remove_edge(self, u, v):
        """Remove an edge."""
        # Remove from u's list
        if self.adj_list[u]:
            self.adj_list[u] = [neighbor for neighbor in self.adj_list[u] if neighbor != v and (isinstance(neighbor, tuple) and neighbor[0] != v)]
        # For undirected, remove from v's list
        if not self.directed:
            if self.adj_list[v]:
                self.adj_list[v] = [neighbor for neighbor in self.adj_list[v] if neighbor != u and (isinstance(neighbor, tuple) and neighbor[0] != u)]
    
    def display(self):
        """Display adjacency list."""
        print("Adjacency List:")
        for vertex in self.adj_list:
            print(f"{vertex}: {self.adj_list[vertex]}")