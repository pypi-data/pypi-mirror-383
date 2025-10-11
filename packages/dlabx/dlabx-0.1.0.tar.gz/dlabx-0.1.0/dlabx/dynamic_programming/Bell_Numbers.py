# ----------- Bell Numbers -----------

def Bell_Numbers(n):
    # Use Pascal's triangle approach
    bell = [[0 for _ in range(n+1)] for _ in range(n+1)]
    bell[0][0] = 1
    for i in range(1, n+1):
        bell[i][0] = bell[i-1][i-1]
        for j in range(1, i+1):
            bell[i][j] = bell[i][j-1] + bell[i-1][j-1]
    total = 0
    for j in range(n+1):
        total += bell[n][j]
    return total