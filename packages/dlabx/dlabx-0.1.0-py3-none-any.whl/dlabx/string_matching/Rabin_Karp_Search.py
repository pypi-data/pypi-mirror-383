def Rabin_Karp_Search(text, pattern):
    n, m = len(text), len(pattern)
    p, base, prime = 0, 256, 101
    high_order = pow(base, m-1, prime)
    pattern_hash = sum(ord(pattern[i]) * pow(base, m - i - 1, prime) for i in range(m)) % prime
    window_hash = sum(ord(text[i]) * pow(base, m - i - 1, prime) for i in range(m)) % prime
    
    positions = []
    for i in range(n - m + 1):
        if pattern_hash == window_hash and text[i:i+m] == pattern:
            positions.append(i)
        if i < n - m:
            window_hash = (window_hash - ord(text[i]) * high_order) * base + ord(text[i + m])
            window_hash %= prime
    return positions