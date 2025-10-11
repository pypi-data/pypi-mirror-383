# Custom heap sort implementation without import
def heapify(arr, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and arr[l] > arr[largest]:
        largest = l
    if r < n and arr[r] > arr[largest]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def Heap_Sort(arr):
    result = arr.copy()
    n = len(result)

    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(result, n, i)

    # Extract elements from heap
    for i in range(n - 1, 0, -1):
        result[0], result[i] = result[i], result[0]
        heapify(result, i, 0)

    return result