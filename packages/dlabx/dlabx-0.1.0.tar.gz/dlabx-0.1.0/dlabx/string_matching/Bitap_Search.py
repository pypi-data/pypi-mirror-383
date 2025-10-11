# ----------- Bitap (Shift-Or) String Search -----------

def Bitap_Search(text, pattern):
  
    if not pattern or not text:
        return []

    m = len(pattern)
    if m > 63:  # Bitmask limit for 64-bit style operations
        raise ValueError("Pattern too long for Bitap algorithm (max 63 characters).")

    # Step 1: Build bitmasks for each character in the pattern
    alphabet = {}
    for char in set(text):
        alphabet[char] = ~0  # All bits set to 1 (no match yet)

    for i, char in enumerate(pattern):
        alphabet[char] = alphabet.get(char, ~0) & ~(1 << i)

    # Step 2: Initialize R (represents match progress)
    R = ~1  # All bits 1 except the rightmost bit 0
    matches = []

    # Step 3: Scan the text
    for i, char in enumerate(text):
        R = ((R << 1) | 1) & alphabet.get(char, ~0)
        if (R & (1 << (m - 1))) == 0:
            # Match found ending at position i
            matches.append(i - m + 1)

    return matches
