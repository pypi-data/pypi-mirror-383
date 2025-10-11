def Greedy_Coloring(graph):
    result = {}
    for node in sorted(graph):
        available_colors = set()
        for neighbor in graph[node]:
            if neighbor in result:
                available_colors.add(result[neighbor])
        color = 0
        while color in available_colors:
            color += 1
        result[node] = color
    return result