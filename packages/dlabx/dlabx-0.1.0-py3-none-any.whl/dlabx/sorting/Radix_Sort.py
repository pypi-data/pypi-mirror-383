
def Radix_Sort(arr):
    if not arr:
        return []
    max_num = max(arr)
    exp = 1
    result = arr.copy()
    while max_num // exp > 0:
        result = counting_sort_by_digit(result, exp)
        exp *= 10
    return result

def counting_sort_by_digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in reversed(range(n)):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1

    return output
