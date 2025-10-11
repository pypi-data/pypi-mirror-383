def Sunday_Search(text, pattern):
    n = len(text)
    m = len(pattern)

    # Build shift table for pattern characters
    shift_table = {}
    for i, c in enumerate(pattern):
        shift_table[c] = m - i

    i = 0
    result = []

    while i <= n - m:
        # Check for match
        if text[i:i + m] == pattern:
            result.append(i)
        # Check the character after the current window
        next_char_index = i + m
        if next_char_index < n:
            next_char = text[next_char_index]
            shift = shift_table.get(next_char, m + 1)
        else:
            break  # No character after the window, end search
        i += shift
    return result