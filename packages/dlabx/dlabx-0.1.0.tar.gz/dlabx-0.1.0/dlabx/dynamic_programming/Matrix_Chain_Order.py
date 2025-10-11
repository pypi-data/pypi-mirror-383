def Matrix_Chain_Order(p):
    n = len(p) - 1
    # Initialize DP tables
    dp = [[0 for _ in range(n)] for _ in range(n)]
    s = [[0 for _ in range(n)] for _ in range(n)]
    
    # Compute minimum costs
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + p[i] * p[k + 1] * p[j + 1]
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    s[i][j] = k

    # Function to build optimal parenthesization string
    def build_parenthesization(s, i, j):
        if i == j:
            return f"A{i+1}"
        else:
            left = build_parenthesization(s, i, s[i][j])
            right = build_parenthesization(s, s[i][j] + 1, j)
            return f"({left} x {right})"

    order = build_parenthesization(s, 0, n - 1)
    return dp[0][n - 1], order