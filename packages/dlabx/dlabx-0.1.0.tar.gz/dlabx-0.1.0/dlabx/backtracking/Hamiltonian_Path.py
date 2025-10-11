def Hamiltonian_Path(graph):
    n = len(graph)
    path = []

    def backtrack(vertex, visited, current_path):
        if len(current_path) == n:
            path.clear()
            path.extend(current_path)
            return True
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                current_path.append(neighbor)
                if backtrack(neighbor, visited, current_path):
                    return True
                current_path.pop()
                visited.remove(neighbor)
        return False

    for start in range(n):
        visited = set([start])
        current_path = [start]
        if backtrack(start, visited, current_path):
            return True, path
    return False, []