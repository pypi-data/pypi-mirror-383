def Linear_Search(arr, target):
    """Linear Search: O(n)"""
    for index, element in enumerate(arr):
        if element == target:
            return index
    return -1