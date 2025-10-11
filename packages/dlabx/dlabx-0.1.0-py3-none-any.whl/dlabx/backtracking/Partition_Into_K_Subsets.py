# ----------- Partitioning an Array into K Subsets (returns subsets) -----------

def Partition_Into_K_Subsets(nums, k):
    total = sum(nums)
    if total % k != 0:
        return False, []
    target = total // k
    nums.sort(reverse=True)  # Sorting helps with pruning
    subsets = [[] for _ in range(k)]
    subset_sums = [0] * k

    def backtrack(index):
        if index == len(nums):
            return all(s == target for s in subset_sums)
        for i in range(k):
            if subset_sums[i] + nums[index] <= target:
                subset_sums[i] += nums[index]
                subsets[i].append(nums[index])

                if backtrack(index + 1):
                    return True

                # Backtrack
                subset_sums[i] -= nums[index]
                subsets[i].pop()

            # Optimization: if current subset is empty, no need to try others
            if subset_sums[i] == 0:
                break
        return False

    if backtrack(0):
        return True, subsets
    else:
        return False, []
