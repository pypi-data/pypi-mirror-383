# ----------- Count Paths in Grid -----------

def Count_Paths(m, n):
    """
    Count the number of unique paths in an m x n grid from top-left to bottom-right.
    Only moves allowed: right and down.
    """
    dp = [[1]*n for _ in range(m)]  # Initialize first row and first column with 1

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]  # Paths from top + paths from left

    return dp[m-1][n-1]
