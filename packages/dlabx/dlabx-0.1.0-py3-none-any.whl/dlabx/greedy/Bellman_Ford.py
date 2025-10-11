def Bellman_Ford(graph, start):
    """
    Bellman-Ford Algorithm to find shortest paths from start node.

    Parameters:
        graph: dict, adjacency list {node: [(neighbor, weight), ...], ...}
        start: starting node

    Returns:
        distances: dict {node: shortest distance from start}
        negative_cycle: bool, True if a negative weight cycle exists
    """
    nodes = list(graph.keys())
    distances = {node: float('inf') for node in nodes}
    distances[start] = 0

    # Relax edges |V| - 1 times
    for _ in range(len(nodes) - 1):
        for u in graph:
            for v, w in graph[u]:
                if distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w

    # Check for negative-weight cycles
    negative_cycle = False
    for u in graph:
        for v, w in graph[u]:
            if distances[u] + w < distances[v]:
                negative_cycle = True
                break

    return distances, negative_cycle
