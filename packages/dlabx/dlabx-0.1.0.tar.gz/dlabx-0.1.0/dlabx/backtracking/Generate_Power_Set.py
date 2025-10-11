# ----------- Generating All Subsets (Power Set) -----------

def Generate_Power_Set(nums):
    result = []

    def backtrack(start, subset):
        result.append(subset[:])
        for i in range(start, len(nums)):
            subset.append(nums[i])
            backtrack(i+1, subset)
            subset.pop()

    backtrack(0, [])
    return result