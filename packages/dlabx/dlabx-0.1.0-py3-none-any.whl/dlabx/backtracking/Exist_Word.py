# ----------- N-Dimensional Word Search (without itertools) -----------

def Exist_Word(grid, word):

    # Determine the shape of the grid
    def shape(g):
        if isinstance(g, list):
            return [len(g)] + shape(g[0])
        else:
            return []

    grid_shape = shape(grid)
    n_dims = len(grid_shape)
    
    if n_dims == 0:
        return False
    
    # Generate all possible directions in N dimensions recursively
    def gen_directions(n):
        if n == 0:
            return [[]]
        subdirs = gen_directions(n-1)
        directions = []
        for d in subdirs:
            for i in (-1, 0, 1):
                directions.append(d + [i])
        return directions
    
    directions = gen_directions(n_dims)
    directions = [d for d in directions if any(x != 0 for x in d)]  # exclude zero vector
    
    visited = set()  # store visited coordinates as tuples
    
    def in_bounds(pos):
        return all(0 <= pos[i] < grid_shape[i] for i in range(n_dims))
    
    def get_value(pos):
        g = grid
        for idx in pos:
            g = g[idx]
        return g
    
    def dfs(pos, idx):
        if idx == len(word):
            return True
        if not in_bounds(pos) or get_value(pos) != word[idx] or tuple(pos) in visited:
            return False
        
        visited.add(tuple(pos))
        for d in directions:
            next_pos = [pos[i] + d[i] for i in range(n_dims)]
            if dfs(next_pos, idx + 1):
                return True
        visited.remove(tuple(pos))
        return False
    
    # Generate all starting positions recursively
    def gen_positions(dims, prefix=[]):
        if not dims:
            yield prefix
        else:
            for i in range(dims[0]):
                yield from gen_positions(dims[1:], prefix + [i])
    
    for start in gen_positions(grid_shape):
        if get_value(start) == word[0] and dfs(start, 0):
            return True
    return False
