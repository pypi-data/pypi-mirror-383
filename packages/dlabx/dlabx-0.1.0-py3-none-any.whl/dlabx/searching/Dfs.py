def Dfs(graph, start, visited=None):
    """
    Depth-First Search (DFS)
    graph: adjacency list, e.g., {node: [neighbors]}
    start: starting node
    visited: set of visited nodes (for recursion)
    returns: list of visited nodes in DFS order
    """
    if visited is None:
        visited = set()
    visited.add(start)
    order = [start]
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            order.extend(Dfs(graph, neighbor, visited))
    return order