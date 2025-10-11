# ----------- Huffman Coding -----------
from collections import Counter

def Huffman_Coding(text):
    """
    Huffman Coding algorithm to encode a string.

    Parameters:
        text: str, input string to encode

    Returns:
        codes: dict {char: code}
        encoded_str: str, encoded binary string
    """
    if not text:
        return {}, ""

    # Count frequency of each character
    frequencies = Counter(text)

    # Implement a simple heap with list and helper functions
    heap = []

    def heap_push(item):
        heap.append(item)
        _heapify_up(len(heap) - 1)

    def heap_pop():
        if not heap:
            return None
        _swap(0, len(heap) - 1)
        min_item = heap.pop()
        _heapify_down(0)
        return min_item

    def _heapify_up(i):
        parent = (i - 1) // 2
        while i > 0 and heap[parent][0] > heap[i][0]:
            _swap(parent, i)
            i = parent
            parent = (i - 1) // 2

    def _heapify_down(i):
        smallest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < len(heap) and heap[left][0] < heap[smallest][0]:
            smallest = left
        if right < len(heap) and heap[right][0] < heap[smallest][0]:
            smallest = right
        if smallest != i:
            _swap(i, smallest)
            _heapify_down(smallest)

    def _swap(i, j):
        heap[i], heap[j] = heap[j], heap[i]

    # Initialize heap with characters and their frequencies
    for symbol, weight in frequencies.items():
        heap_push([weight, [symbol, ""]])

    # Build Huffman Tree
    while len(heap) > 1:
        lo = heap_pop()
        hi = heap_pop()
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heap_push([lo[0] + hi[0]] + lo[1:] + hi[1:])

    # Extract Huffman codes
    code_dict = {}
    if heap:
        for symbol, code in heap[0][1:]:
            code_dict[symbol] = code

    # Encode the string
    encoded_str = "".join(code_dict[c] for c in text)

    return code_dict, encoded_str
