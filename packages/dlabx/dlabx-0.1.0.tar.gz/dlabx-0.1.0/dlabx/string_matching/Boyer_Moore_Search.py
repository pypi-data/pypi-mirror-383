def Boyer_Moore_Search(text, pattern):
    # Build the bad character shift table
    bad_char = {c: i for i, c in enumerate(pattern)}
    m = len(pattern)
    n = len(text)
    i = 0
    result = []

    while i <= n - m:
        j = m - 1
        # Compare pattern from end
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1
        if j < 0:
            result.append(i)
            i += (m - bad_char.get(text[i + m], -1)) if i + m < n else 1
        else:
            shift = max(1, j - bad_char.get(text[i + j], -1))
            i += shift
    return result