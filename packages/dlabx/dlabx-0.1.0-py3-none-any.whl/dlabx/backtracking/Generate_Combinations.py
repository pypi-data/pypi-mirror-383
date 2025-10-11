# ----------- Combinations Generation -----------

def Generate_Combinations(nums, k):
    def backtrack(start, path):
        if len(path) == k:
            combinations.append(path[:])
            return
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i+1, path)
            path.pop()

    combinations = []
    backtrack(0, [])
    return combinations