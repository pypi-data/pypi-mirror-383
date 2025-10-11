def Bfs(graph, start):
    """
    Breadth-First Search (BFS)
    graph: adjacency list, e.g., {node: [neighbors]}
    start: starting node
    returns: list of visited nodes in BFS order
    """
    visited = set()
    queue = []
    order = []

    queue.append(start)
    visited.add(start)

    while queue:
        current = queue.pop(0)
        order.append(current)
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order