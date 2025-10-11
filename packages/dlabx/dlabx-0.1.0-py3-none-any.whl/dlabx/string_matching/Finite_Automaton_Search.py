# ----------- Finite Automaton (KMP-based) Pattern Search -----------

def compute_lps_array(pattern):
    """Compute the Longest Prefix Suffix (LPS) array for the given pattern."""
    lps = [0] * len(pattern)
    length = 0  # Length of the previous longest prefix suffix
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def build_transition_table(pattern, alphabet):
    """Builds transition table for the Finite Automaton based on KMP preprocessing."""
    m = len(pattern)
    lps = compute_lps_array(pattern)
    transition_table = []

    for state in range(m + 1):
        transition = {}
        for ch in alphabet:
            k = state
            while k > 0 and (k == m or pattern[k] != ch):
                k = lps[k - 1]
            if k < m and pattern[k] == ch:
                transition[ch] = k + 1
            else:
                transition[ch] = k
        transition_table.append(transition)
    return transition_table


def Finite_Automaton_Search(text, pattern):
    """
    Search all occurrences of 'pattern' in 'text' using Finite Automaton method.
    Returns: List of starting indices.
    """
    if not pattern or not text or len(pattern) > len(text):
        return []

    alphabet = sorted(set(text + pattern))
    transition_table = build_transition_table(pattern, alphabet)

    state = 0
    result = []

    for i, ch in enumerate(text):
        state = transition_table[state].get(ch, 0)
        if state == len(pattern):
            result.append(i - len(pattern) + 1)
    return result
