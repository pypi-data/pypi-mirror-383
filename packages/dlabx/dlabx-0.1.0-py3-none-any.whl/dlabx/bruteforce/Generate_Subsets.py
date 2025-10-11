# ----------- Subset Generation (Power Set) -----------

def Generate_Subsets(nums):
  
    result = []
    arr = list(nums)  # Convert to list if input is a string

    def backtrack(start, path):
        # Add current subset to the result
        result.append(path[:])
        # Try including each remaining element
        for i in range(start, len(arr)):
            path.append(arr[i])
            backtrack(i + 1, path)
            path.pop()  # Backtrack: remove last element

    backtrack(0, [])
    return result
