def Wumanber_Search(text, patterns):
    """
    Wu-Manber algorithm for multi-pattern exact string matching.
    Returns a dictionary: {pattern: [positions]}
    """
    if not patterns:
        return {}

    # Minimum pattern length
    m = min(len(p) for p in patterns)
    if m == 0:
        return {}

    # Build shift table based on last characters of blocks
    shift = {}
    for pat in patterns:
        for i in range(len(pat) - m + 1):
            block = pat[i:i+m]
            shift[block] = len(pat) - i - m + 1

    results = {pat: [] for pat in patterns}
    n = len(text)
    i = 0

    while i <= n - m:
        # Extract the last block of length m in current window
        window_block = text[i:i+m]
        if window_block in shift:
            # Check all patterns for exact match at this position
            for pat in patterns:
                if i + len(pat) <= n and text[i:i+len(pat)] == pat:
                    results[pat].append(i)
            i += 1
        else:
            # Shift by block length if block not found
            i += m

    return results
