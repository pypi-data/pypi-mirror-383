def Shell_Sort(arr):
    n = len(arr)
    result = arr.copy()
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = result[i]
            j = i
            while j >= gap and result[j - gap] > temp:
                result[j] = result[j - gap]
                j -= gap
            result[j] = temp
        gap //= 2
    return result