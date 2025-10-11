# ----------- Graph Coloring (m colors) -----------

def Graph_Coloring(graph, m):

    n = len(graph)
    color_assignment = [0] * n

    def is_safe(node, c):
        for neighbor in graph[node]:
            if color_assignment[neighbor] == c:
                return False
        return True

    def backtrack(node):
        if node == n:
            return True
        for c in range(1, m + 1):  # use m directly
            if is_safe(node, c):
                color_assignment[node] = c
                if backtrack(node + 1):
                    return True
                color_assignment[node] = 0
        return False

    if backtrack(0):
        return color_assignment
    return []
