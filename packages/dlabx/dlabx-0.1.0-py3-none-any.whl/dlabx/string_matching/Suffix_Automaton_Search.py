class Suffix_Automaton_Search:
    class State:
        def __init__(self):
            self.length = 0
            self.link = -1
            self.next = {}

    def __init__(self, s):
        self.states = [self.State()]
        self.size = 1
        self.last = 0
        for c in s:
            self._add_char(c)

    def _add_char(self, c):
        cur = self.size
        self.states.append(self.State())
        self.states[cur].length = self.states[self.last].length + 1
        p = self.last

        while p != -1 and c not in self.states[p].next:
            self.states[p].next[c] = cur
            p = self.states[p].link

        if p == -1:
            self.states[cur].link = 0
        else:
            q = self.states[p].next[c]
            if self.states[p].length + 1 == self.states[q].length:
                self.states[cur].link = q
            else:
                # Clone state
                clone = self.size
                self.states.append(self.State())
                self.states[clone].length = self.states[p].length + 1
                self.states[clone].next = self.states[q].next.copy()
                self.states[clone].link = self.states[q].link

                while p != -1 and self.states[p].next.get(c, -1) == q:
                    self.states[p].next[c] = clone
                    p = self.states[p].link

                self.states[q].link = clone
                self.states[cur].link = clone
                self.size += 1

        self.last = cur
        self.size += 1

    def count_distinct_substrings(self):
        """Number of distinct substrings = sum of lengths of all states - sum of lengths of their suffix links"""
        total = 0
        for state in self.states[1:]:
            total += state.length - self.states[state.link].length
        return total

    def search(self, pattern):
        """Returns True if pattern exists in the string."""
        current = 0
        for ch in pattern:
            if ch not in self.states[current].next:
                return False
            current = self.states[current].next[ch]
        return True
