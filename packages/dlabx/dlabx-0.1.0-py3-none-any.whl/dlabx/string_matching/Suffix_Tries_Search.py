class SuffixTrieNode:
    def __init__(self):
        self.children = {}

class SuffixTrie:
    def __init__(self, s):
        self.root = SuffixTrieNode()
        self.build_suffix_trie(s)

    def build_suffix_trie(self, s):
        # Insert all suffixes into the trie
        for i in range(len(s)):
            current = self.root
            for c in s[i:]:
                if c not in current.children:
                    current.children[c] = SuffixTrieNode()
                current = current.children[c]

    def search(self, pattern):
        current = self.root
        for c in pattern:
            if c not in current.children:
                return False
            current = current.children[c]
        return True

    def print_trie(self, node=None, prefix=''):
        if node is None:
            node = self.root
        for c, child in node.children.items():
            print(prefix + c)
            self.print_trie(child, prefix + c)