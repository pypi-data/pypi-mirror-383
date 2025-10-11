# ----------- Permutation Generation (Heap's Algorithm) -----------

def Generate_Permutations(nums):

    result = []
    arr = list(nums)  # Convert to list if input is a string

    def heap_permute(n):
        if n == 1:
            result.append(arr[:])
            return
        for i in range(n):
            heap_permute(n - 1)
            # Perform swap depending on n being even or odd
            if n % 2 == 0:
                arr[i], arr[n - 1] = arr[n - 1], arr[i]
            else:
                arr[0], arr[n - 1] = arr[n - 1], arr[0]

    heap_permute(len(arr))
    return result
