def Counting_Sort_By_Digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    # Count occurrences of each digit at current exp
    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1

    # Update count[i] to contain the actual position
    for i in range(1, 10):
        count[i] += count[i - 1]

    # Build output array (stable order)
    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1

    # Copy output to arr
    for i in range(n):
        arr[i] = output[i]

    return arr


def Radix_Sort(arr):
    if not arr:
        return arr

    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = Counting_Sort_By_Digit(arr, exp)  # ✅ pass both arr and exp
        exp *= 10
    return arr
