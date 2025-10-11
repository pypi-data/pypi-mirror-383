# ----------- Unbounded Knapsack -----------

def Unbounded_Knapsack(weights, values, capacity):
    n = len(weights)
    dp = [0] * (capacity + 1)
    selected = [[] for _ in range(capacity + 1)]

    for w in range(capacity + 1):
        for i in range(n):
            if weights[i] <= w:
                val = values[i] + dp[w - weights[i]]
                if val > dp[w]:
                    dp[w] = val
                    selected[w] = selected[w - weights[i]] + [i]

    return dp[capacity], selected[capacity]
