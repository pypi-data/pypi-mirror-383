def Counting_Sort(arr, max_value=None):
    if not arr:
        return []
    if max_value is None:
        max_value = max(arr)
    count = [0] * (max_value + 1)
    for num in arr:
        count[num] += 1
    result = []
    for num, freq in enumerate(count):
        result.extend([num] * freq)
    return result