# ----------- Edit Distance (Levenshtein Distance with Operations) -----------

def Edit_Distance(str1, str2):
    m, n = len(str1), len(str2)
    dp = [[0]*(n+1) for _ in range(m+1)]

    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j

    for i in range(1, m+1):
        for j in range(1, n+1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

    # Backtrack to reconstruct the operations
    i, j = m, n
    operations = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and str1[i-1] == str2[j-1]:
            operations.append(f"Keep '{str1[i-1]}'")
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            operations.append(f"Delete '{str1[i-1]}' from position {i}")
            i -= 1
        elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
            operations.append(f"Insert '{str2[j-1]}' at position {i+1}")
            j -= 1
        else:
            operations.append(f"Replace '{str1[i-1]}' with '{str2[j-1]}' at position {i}")
            i -= 1
            j -= 1

    operations.reverse()
    return dp[m][n], operations
