def Interpolation_Search(arr, target):
    """Interpolation Search: O(log log n) - assumes uniformly distributed sorted data"""
    low, high = 0, len(arr) - 1
    while low <= high and target >= arr[low] and target <= arr[high]:
        if arr[high] == arr[low]:
            if arr[low] == target:
                return low
            else:
                return -1
        pos = low + int(((float(high - low)) / (arr[high] - arr[low])) * (target - arr[low]))
        if pos >= len(arr):
            return -1
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    return -1