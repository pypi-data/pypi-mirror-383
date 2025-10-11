# ----------- Optimal Binary Search Tree -----------

def Optimal_Bst(p, q):
    n = len(p) - 1
    # Initialize 2D arrays
    e = [[0 for _ in range(n+1)] for _ in range(n+1)]
    w = [[0 for _ in range(n+1)] for _ in range(n+1)]
    # root array not used here, so omitted
    for i in range(n+1):
        e[i][i] = q[i]
        w[i][i] = q[i]
    for l in range(1, n+1):
        for i in range(n - l + 1):
            j = i + l
            e[i][j] = float('inf')
            w[i][j] = w[i][j-1] + p[j-1] + q[j]
            for r in range(i+1, j+1):
                t = e[i][r-1] + e[r][j] + w[i][j]
                if t < e[i][j]:
                    e[i][j] = t
    return e[0][n]
