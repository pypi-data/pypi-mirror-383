# ----------- Subset Sum Problem (Backtracking with subset) -----------

def Subset_Sum(nums, target):
    result = []

    def backtrack(start, current_sum, path):
        if current_sum == target:
            result.extend(path)  # store the subset
            return True
        if current_sum > target:
            return False
        for i in range(start, len(nums)):
            if backtrack(i+1, current_sum + nums[i], path + [nums[i]]):
                return True
        return False

    exists = backtrack(0, 0, [])
    return exists, result
