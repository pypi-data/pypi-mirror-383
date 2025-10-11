def Naive_Search(text, pattern):
    """
    Search for all occurrences of 'pattern' in 'text' using the naive approach.

    Parameters:
    text (str): The text in which to search.
    pattern (str): The pattern to find.

    Returns:
    list: A list of starting indices where pattern is found in text.
    """
    n = len(text)
    m = len(pattern)
    occurrences = []

    for i in range(n - m + 1):
        match_found = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match_found = False
                break
        if match_found:
            occurrences.append(i)

    return occurrences