def Cycle_Sort(arr):
    result = arr.copy()
    n = len(result)
    for cycle_start in range(0, n - 1):
        item = result[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            if result[i] < item:
                pos += 1
        if pos == cycle_start:
            continue
        while item == result[pos]:
            pos += 1
        result[pos], item = item, result[pos]
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                if result[i] < item:
                    pos += 1
            while item == result[pos]:
                pos += 1
            result[pos], item = item, result[pos]
    return result