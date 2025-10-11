def Comb_Sort(arr):
    result = arr.copy()
    n = len(result)
    gap = n
    shrink = 1.3
    swapped = True
    while gap > 1 or swapped:
        gap = int(gap / shrink)
        if gap < 1:
            gap = 1
        swapped = False
        for i in range(0, n - gap):
            if result[i] > result[i + gap]:
                result[i], result[i + gap] = result[i + gap], result[i]
                swapped = True
    return result