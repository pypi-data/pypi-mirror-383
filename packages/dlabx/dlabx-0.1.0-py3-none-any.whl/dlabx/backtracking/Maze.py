# ----------- N-Dimensional Maze Solver -----------

def Maze(grid, start, end):
  
    dims = len(start)
    visited = set()
    path = []

    def in_bounds(coord):
        g = grid
        for i, x in enumerate(coord):
            if not (0 <= x < len(g)):
                return False
            g = g[x]
        return True

    def is_open(coord):
        g = grid
        for x in coord:
            g = g[x]
        return g == 0

    def neighbors(coord):
        for d in range(dims):
            for delta in [-1, 1]:
                new_coord = list(coord)
                new_coord[d] += delta
                yield tuple(new_coord)

    def dfs(coord):
        if coord in visited or not in_bounds(coord) or not is_open(coord):
            return False
        path.append(coord)
        visited.add(coord)
        if coord == end:
            return True
        for neigh in neighbors(coord):
            if dfs(neigh):
                return True
        path.pop()
        return False

    if dfs(start):
        return path
    return []
