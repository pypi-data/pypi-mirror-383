def rle_compress(text):
    """
    Compresses the text using Run-Length Encoding (RLE).
    Returns a list of (character, count) tuples.
    """
    if not text:
        return []

    compressed = []
    prev_char = text[0]
    count = 1

    for ch in text[1:]:
        if ch == prev_char:
            count += 1
        else:
            compressed.append((prev_char, count))
            prev_char = ch
            count = 1
    compressed.append((prev_char, count))
    return compressed

def rle_decompress(compressed):
    """
    Decompresses RLE data back into the original string.
    """
    return ''.join([ch * count for ch, count in compressed])

def pattern_match_in_rle(compressed_text, pattern):
    """
    Naively searches for pattern in RLE compressed text.
    Note: This is a simplified approach and may not handle all edge cases efficiently.
    """
    decompressed_text = rle_decompress(compressed_text)
    positions = []

    start = 0
    while True:
        idx = decompressed_text.find(pattern, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions
