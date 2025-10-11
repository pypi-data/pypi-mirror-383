def Binary_Search_Range(arr, target):

    low, high = 0, len(arr) - 1

    def find_first():
        left, right = low, high
        first_occurrence = -1
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                first_occurrence = mid
                right = mid - 1  # Move left
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return first_occurrence

    def find_last():
        left, right = low, high
        last_occurrence = -1
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                last_occurrence = mid
                left = mid + 1  # Move right
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return last_occurrence

    start = find_first()
    end = find_last()

    if start == -1 or end == -1:
        return -1, -1
    return start, end
