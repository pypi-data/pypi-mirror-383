def Z_Array_Search(text, pattern):
    """
    Searches for all occurrences of `pattern` in `text` using the Z-array.
    Returns list of starting indices.
    """
    concat = pattern + "$" + text  # $ is a delimiter not in pattern/text
    n = len(concat)
    z = [0] * n
    left, right = 0, 0
    matches = []

    for i in range(1, n):
        if i <= right:
            z[i] = min(right - i + 1, z[i - left])
        while i + z[i] < n and concat[z[i]] == concat[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > right:
            left = i
            right = i + z[i] - 1
        if z[i] == len(pattern):
            matches.append(i - len(pattern) - 1)  # adjust to original text index

    return matches
