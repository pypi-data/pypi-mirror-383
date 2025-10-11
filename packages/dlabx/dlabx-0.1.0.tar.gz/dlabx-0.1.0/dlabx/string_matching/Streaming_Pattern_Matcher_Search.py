class Streaming_Pattern_Matcher_Search:
    def __init__(self, pattern):
        self.pattern = pattern
        self.lps = self.compute_lps(pattern)
        self.state = 0  # current match length

    def compute_lps(self, pattern):
        """
        Preprocesses pattern to create longest prefix-suffix (lps) array.
        """
        lps = [0] * len(pattern)
        length = 0  # length of the previous longest prefix suffix
        i = 1

        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    def process_char(self, ch):
        """
        Processes a new character from the stream.
        Returns True if pattern is matched at this point.
        """
        while self.state > 0 and ch != self.pattern[self.state]:
            self.state = self.lps[self.state - 1]
        if ch == self.pattern[self.state]:
            self.state += 1
        if self.state == len(self.pattern):
            # Pattern found; reset state to continue searching
            self.state = self.lps[self.state - 1]
            return True
        return False