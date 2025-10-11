# ----------- Partition Problem (Return Actual Subsets) -----------

def Partition_Array(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False, [], []  # Cannot partition if sum is odd

    target = total // 2
    n = len(nums)
    subset = []

    def backtrack(i, current_sum):
        if current_sum == target:
            return True
        if current_sum > target or i >= n:
            return False
        # Include nums[i]
        subset.append(nums[i])
        if backtrack(i + 1, current_sum + nums[i]):
            return True
        subset.pop()
        # Exclude nums[i]
        return backtrack(i + 1, current_sum)

    if backtrack(0, 0):
        # Build the other subset
        remaining = nums.copy()
        for x in subset:
            remaining.remove(x)
        return True, subset, remaining

    return False, [], []