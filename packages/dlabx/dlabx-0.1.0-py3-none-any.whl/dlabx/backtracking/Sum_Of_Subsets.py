# ----------- Sum of Subsets -----------

def Sum_Of_Subsets(nums, target):
    result = []

    def backtrack(index, current_sum, subset):
        if current_sum == target:
            result.append(subset[:])
            return
        if current_sum > target or index >= len(nums):
            return
        # include nums[index]
        subset.append(nums[index])
        backtrack(index+1, current_sum + nums[index], subset)
        subset.pop()
        # exclude nums[index]
        backtrack(index+1, current_sum, subset)

    backtrack(0, 0, [])
    return result