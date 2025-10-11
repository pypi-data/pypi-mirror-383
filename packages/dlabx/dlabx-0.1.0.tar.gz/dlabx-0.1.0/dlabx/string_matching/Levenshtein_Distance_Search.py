# ----------- Levenshtein Distance Search (Approximate Matching) -----------

def Levenshtein_Distance_Search(text, pattern, max_distance):

    n, m = len(text), len(pattern)
    if m == 0 or n == 0:
        return []

    # Initialize the DP array (only one row for efficiency)
    prev_row = list(range(m + 1))
    matches = []

    for i in range(1, n + 1):
        curr_row = [i] + [0] * m
        for j in range(1, m + 1):
            cost = 0 if text[i - 1] == pattern[j - 1] else 1
            curr_row[j] = min(
                curr_row[j - 1] + 1,     # Insertion
                prev_row[j] + 1,         # Deletion
                prev_row[j - 1] + cost   # Substitution
            )

        # If edit distance ≤ max_distance, record a match
        if curr_row[m] <= max_distance:
            start_index = i - m
            matches.append((start_index, curr_row[m]))

        prev_row = curr_row

    return matches
