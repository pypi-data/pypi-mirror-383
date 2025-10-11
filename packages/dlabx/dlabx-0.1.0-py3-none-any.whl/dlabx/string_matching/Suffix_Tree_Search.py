class SuffixTreeNode:
    def __init__(self):
        self.children = {}
        self.start = -1
        self.end = -1
        self.index = -1  # leaf index

class Suffix_Tree_Search:
    def __init__(self, text):
        self.text = text
        self.root = self.build_suffix_tree(text)  # keep root inside the object

    def build_suffix_tree(self, text):
        """Naive suffix tree construction (O(n^2))"""
        root = SuffixTreeNode()
        n = len(text)
        for i in range(n):
            current = root
            for j in range(i, n):
                c = text[j]
                if c not in current.children:
                    node = SuffixTreeNode()
                    node.start = j
                    node.end = n
                    node.index = i
                    current.children[c] = node
                current = current.children[c]
        return root

    def search(self, pattern):
        """Search pattern in the suffix tree."""
        current = self.root
        i = 0
        while i < len(pattern):
            c = pattern[i]
            if c not in current.children:
                return False
            child = current.children[c]
            label_len = child.end - child.start
            j = 0
            while j < label_len and i < len(pattern):
                if self.text[child.start + j] != pattern[i]:
                    return False
                i += 1
                j += 1
            current = child
        return True
