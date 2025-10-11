# ----------- Can Partition (Partition Equal Subset Sum) -----------
def Can_Partition(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False, []

    target = total // 2
    n = len(nums)
    dp = [[False]*(target+1) for _ in range(n+1)]
    for i in range(n+1):
        dp[i][0] = True

    for i in range(1, n+1):
        for s in range(1, target+1):
            if nums[i-1] <= s:
                dp[i][s] = dp[i-1][s] or dp[i-1][s-nums[i-1]]
            else:
                dp[i][s] = dp[i-1][s]

    if not dp[n][target]:
        return False, []

    # Reconstruct one subset
    subset = []
    i, s = n, target
    while i > 0 and s > 0:
        if dp[i][s] and not dp[i-1][s]:
            subset.append(nums[i-1])
            s -= nums[i-1]
        i -= 1

    subset.reverse()
    return True, subset
