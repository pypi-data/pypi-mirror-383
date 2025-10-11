def Exponential_Search(arr, target):
    """Exponential Search: O(log n)"""
    if len(arr) == 0:
        return -1
    if arr[0] == target:
        return 0
    size = len(arr)
    bound = 1
    while bound < size and arr[bound] < target:
        bound *= 2
    low = bound // 2
    high = min(bound, size - 1)
    return binary_search_range(arr, target, low, high)

def binary_search_range(arr, target, low, high):
    """Helper for exponential search"""
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1