# ----------- Catalan Numbers -----------

def Catalan_Numbers(n):
    catalan = [0]*(n+1)
    catalan[0] = 1
    for i in range(1, n+1):
        total = 0
        for j in range(i):
            total += catalan[j] * catalan[i - j - 1]
        catalan[i] = total
    return catalan[n]