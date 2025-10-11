def Ternary_Search(arr, target, left=0, right=None):
    
    if right is None:
        right = len(arr) - 1
    if left > right:
        return -1

    third = (right - left) // 3
    mid1 = left + third
    mid2 = right - third

    if arr[mid1] == target:
        return mid1
    if arr[mid2] == target:
        return mid2

    if target < arr[mid1]:
        return Ternary_Search(arr, target, left, mid1 - 1)  
    elif target > arr[mid2]:
        return Ternary_Search(arr, target, mid2 + 1, right) 
    else:
        return Ternary_Search(arr, target, mid1 + 1, mid2 - 1)  
