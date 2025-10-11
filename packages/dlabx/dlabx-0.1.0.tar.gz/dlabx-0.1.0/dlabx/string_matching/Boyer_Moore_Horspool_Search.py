def Boyer_Moore_Horspool_Search(text, pattern):
    m = len(pattern)
    n = len(text)

    # Build the shift table
    shift_table = {c: m for c in set(text)}
    for i in range(m - 1):
        shift_table[pattern[i]] = m - i - 1

    i = 0
    result = []

    while i <= n - m:
        j = m - 1
        # Compare from end of pattern
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1
        if j < 0:
            result.append(i)
            i += shift_table.get(text[i + m - 1], m)
        else:
            i += shift_table.get(text[i + j], m)
    return result
