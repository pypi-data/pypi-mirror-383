# ----------- Simple Heap Implementation ----------- #

class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def extract_min(self):
        if not self.heap:
            return None
        self._swap(0, len(self.heap) - 1)
        min_item = self.heap.pop()
        self._heapify_down(0)
        return min_item

    def _heapify_up(self, index):
        parent = (index - 1) // 2
        if parent >= 0 and self.heap[parent][0] > self.heap[index][0]:
            self._swap(parent, index)
            self._heapify_up(parent)

    def _heapify_down(self, index):
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right
        if smallest != index:
            self._swap(index, smallest)
            self._heapify_down(smallest)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def __len__(self):
        return len(self.heap)



# ----------- Prim's Algorithm -----------

def Prim_Mst(graph, start=0):
    visited = set()
    min_heap = MinHeap()
    mst_edges = []
    total_cost = 0  # add this

    def add_edges(node):
        visited.add(node)
        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                min_heap.insert((weight, node, neighbor))

    add_edges(start)

    while len(min_heap) > 0:
        weight, u, v = min_heap.extract_min()
        if v not in visited:
            mst_edges.append((u, v, weight))
            total_cost += weight  # track cost
            add_edges(v)

    return mst_edges, total_cost 
