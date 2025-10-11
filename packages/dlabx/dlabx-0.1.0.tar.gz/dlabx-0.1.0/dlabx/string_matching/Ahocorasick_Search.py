class TrieNode:
    def __init__(self):
        self.children = {}
        self.failure = None
        self.output = []

class Ahocorasick_Search:
  
    def __init__(self, patterns):
        self.root = TrieNode()
        self.build_trie(patterns)
        self.build_failure_links()

    def build_trie(self, patterns):
        """Builds the trie structure from the given patterns."""
        for pattern in patterns:
            if not pattern:  # Skip empty patterns
                continue
            node = self.root
            for char in pattern:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.output.append(pattern)

    def build_failure_links(self):
        """Builds failure links using a normal list as queue (no deque)."""
        queue = []

        # Root's children fail back to root
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)

        # BFS traversal
        while queue:
            current_node = queue.pop(0)  # FIFO queue behavior
            for char, child_node in current_node.children.items():
                failure_node = current_node.failure
                while failure_node and char not in failure_node.children:
                    failure_node = failure_node.failure
                if failure_node and char in failure_node.children:
                    child_node.failure = failure_node.children[char]
                else:
                    child_node.failure = self.root
                # Merge output lists
                child_node.output += child_node.failure.output
                queue.append(child_node)

    def search(self, text):
    
        node = self.root
        results = {}

        for index, char in enumerate(text):
            # Follow failure links if mismatch
            while node and char not in node.children:
                node = node.failure
            if not node:
                node = self.root
                continue

            node = node.children[char]

            for pattern in node.output:
                start_index = index - len(pattern) + 1
                results.setdefault(pattern, []).append(start_index)

        return results
