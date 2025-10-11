def Kmp_Search(text, pattern):
    # Preprocess pattern to create lps array
    lps = [0] * len(pattern)
    j = 0  # length of the previous longest prefix suffix

    # Build the lps array
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j

    # Search pattern in text
    result = []
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = lps[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == len(pattern):
            result.append(i - len(pattern) + 1)
            j = lps[j - 1]

    return result