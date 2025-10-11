# ----------- Longest Palindromic Subsequence -----------

def Longest_Palindromic_Subsequence(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]

    # Base case: single characters are palindromes of length 1
    for i in range(n):
        dp[i][i] = 1

    # Fill DP table
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = 2 + (dp[i + 1][j - 1] if i + 1 <= j - 1 else 0)
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])

    # Reconstruct the subsequence
    i, j = 0, n - 1
    lps = [""] * dp[0][n - 1]
    start, end = 0, dp[0][n - 1] - 1

    while i <= j:
        if s[i] == s[j]:
            lps[start], lps[end] = s[i], s[j]
            start += 1
            end -= 1
            i += 1
            j -= 1
        elif dp[i + 1][j] > dp[i][j - 1]:
            i += 1
        else:
            j -= 1

    return dp[0][n - 1], ''.join(lps)
