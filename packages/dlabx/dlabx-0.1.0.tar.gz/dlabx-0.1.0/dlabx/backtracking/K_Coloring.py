# ----------- K-Coloring of a Graph -----------

def K_Coloring(graph, k):
    n = len(graph)
    color = [0] * n

    def is_safe(node, c):
        for neighbor in graph[node]:
            if color[neighbor] == c:
                return False
        return True

    def backtrack(node):
        if node == n:
            return True
        for c in range(1, k+1):
            if is_safe(node, c):
                color[node] = c
                if backtrack(node + 1):
                    return True
        return False

    if backtrack(0):
        return True, color
    return False, []