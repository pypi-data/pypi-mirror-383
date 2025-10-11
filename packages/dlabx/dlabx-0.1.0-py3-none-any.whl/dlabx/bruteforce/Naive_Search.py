# ----------- String Pattern Matching (Naive Search) -----------

def Naive_Search(text, pattern):
    occurrences = []
    n, m = len(text), len(pattern)
    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            occurrences.append(i)
    return occurrences
