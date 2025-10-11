# ----------- Longest Increasing Path in a Matrix -----------

def Longest_Increasing_Path(matrix):
    # No external imports, implement DFS with recursion
    m, n = len(matrix), len(matrix[0])
    cache = [[0 for _ in range(n)] for _ in range(m)]
    
    def dfs(i, j):
        if cache[i][j] != 0:
            return cache[i][j]
        max_len = 1
        for x, y in [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]:
            if 0 <= x < m and 0 <= y < n and matrix[x][y] > matrix[i][j]:
                length = 1 + dfs(x, y)
                if length > max_len:
                    max_len = length
        cache[i][j] = max_len
        return max_len
    
    max_path = 0
    for i in range(m):
        for j in range(n):
            max_path = max(max_path, dfs(i, j))
    return max_path