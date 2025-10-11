def Merge_Sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = Merge_Sort(arr[:mid])
    right = Merge_Sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
