def Suffix_Array_Search(text, pattern):

    n = len(text)
    # Step 1: Build the suffix array
    suffixes = list(range(n))
    rank = [ord(c) for c in text]
    tmp = [0] * n
    k = 1

    while k < n:
        suffixes.sort(key=lambda x: (rank[x], rank[x + k] if x + k < n else -1))
        tmp[suffixes[0]] = 0
        for i in range(1, n):
            prev, curr = suffixes[i - 1], suffixes[i]
            tmp[curr] = tmp[prev]
            if (rank[curr], rank[curr + k] if curr + k < n else -1) != \
               (rank[prev], rank[prev + k] if prev + k < n else -1):
                tmp[curr] += 1
        rank, tmp = tmp, rank
        k <<= 1
        if rank[suffixes[-1]] == n - 1:
            break

    # Step 2: Binary search the pattern in suffix array
    def pattern_search():
        l, r = 0, n - 1
        result = []
        m = len(pattern)
        while l <= r:
            mid = (l + r) // 2
            substr = text[suffixes[mid]:suffixes[mid]+m]
            if substr == pattern:
                # Find all occurrences
                # Search left
                i = mid
                while i >= 0 and text[suffixes[i]:suffixes[i]+m] == pattern:
                    result.append(suffixes[i])
                    i -= 1
                # Search right
                i = mid + 1
                while i < n and text[suffixes[i]:suffixes[i]+m] == pattern:
                    result.append(suffixes[i])
                    i += 1
                break
            elif substr < pattern:
                l = mid + 1
            else:
                r = mid - 1
        return sorted(result)

    return pattern_search()
