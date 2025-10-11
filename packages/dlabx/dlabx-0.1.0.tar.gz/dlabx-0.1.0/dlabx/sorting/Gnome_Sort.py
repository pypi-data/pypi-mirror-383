def Gnome_Sort(arr):
    result = arr.copy()
    index = 0
    n = len(result)
    while index < n:
        if index == 0 or result[index] >= result[index - 1]:
            index += 1
        else:
            result[index], result[index - 1] = result[index - 1], result[index]
            index -= 1
    return result