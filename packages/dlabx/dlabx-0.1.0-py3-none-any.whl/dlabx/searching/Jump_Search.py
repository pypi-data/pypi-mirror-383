def Jump_Search(arr, target):
    """Jump Search: O(√n)"""
    length = len(arr)
    # Approximate sqrt without math.sqrt
    n = length
    i = 0
    while i * i < n:
        i += 1
    step = i
    prev = 0
    while prev < n and arr[min(n - 1, prev + step)] < target:
        prev += step
    for i in range(prev, min(prev + step, n)):
        if arr[i] == target:
            return i
    return -1