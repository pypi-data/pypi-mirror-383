# dlab/queue.py

class Queue:
    def __init__(self):
        self._items = []

    # Basic Operations
    def enqueue(self, item):
        """Add an item to the end of the queue."""
        self._items.append(item)

    def dequeue(self):
        """Remove and return the item from the front of the queue."""
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        return self._items.pop(0)

    def front(self):
        """Get the item at the front without removing it."""
        if self.is_empty():
            raise IndexError("Front from empty queue")
        return self._items[0]

    def is_empty(self):
        """Check if the queue is empty."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items in the queue."""
        return len(self._items)

    def display(self):
        """Return a copy of the queue's items."""
        return self._items.copy()

    # Advanced Operations
    def clear(self):
        """Remove all items from the queue."""
        self._items.clear()

    def reverse(self):
        """Reverse the order of items in the queue."""
        self._items.reverse()

    def count(self, item):
        """Count how many times an item appears in the queue."""
        return self._items.count(item)

    def contains(self, item):
        """Check if the item exists in the queue."""
        return item in self._items

    def get_at(self, index):
        """Get item at specific index (0-based)."""
        if index < 0 or index >= len(self._items):
            raise IndexError("Index out of bounds")
        return self._items[index]

    def insert_at(self, index, item):
        """Insert an item at a specific position."""
        if index < 0 or index > len(self._items):
            raise IndexError("Index out of bounds")
        self._items.insert(index, item)

    def __len__(self):
        """Make the object compatible with len()."""
        return len(self._items)