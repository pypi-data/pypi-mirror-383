# ----------- Permutations Generation -----------

def Generate_Permutations(nums):
    def backtrack(path, used):
        if len(path) == len(nums):
            permutations.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used[i] = False

    permutations = []
    used = [False] * len(nums)
    backtrack([], used)
    return permutations
