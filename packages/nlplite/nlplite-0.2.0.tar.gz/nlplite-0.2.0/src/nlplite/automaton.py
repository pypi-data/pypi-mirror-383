try:
    import ahocorasick  # pyahocorasick

    _HAS_PYAC = True
except Exception:
    _HAS_PYAC = False
    ahocorasick = None  # sentinel


class _PyFallbackAutomaton(object):
    def __init__(self):
        self._patterns = []  # list of (term, index)

    def add_word(self, term, index):
        self._patterns.append((term, index))

    def make_automaton(self):
        # Prefer longest matches
        self._patterns.sort(key=lambda x: (-len(x[0]), x[0]))

    def iter(self, text):
        # Brute force scanning: O(num_patterns * text_length)
        for term, idx in self._patterns:
            start = 0
            term_len = len(term)
            while True:
                pos = text.find(term, start)
                if pos == -1:
                    break
                yield (pos + term_len - 1, idx)
                start = pos + 1


class AutomatonWrapper(object):
    def __init__(self):
        if _HAS_PYAC:
            self._impl = ahocorasick.Automaton()
            self._is_py = False
        else:
            self._impl = _PyFallbackAutomaton()
            self._is_py = True

    def add(self, term, index):
        self._impl.add_word(term, index)

    def finalize(self):
        self._impl.make_automaton()

    def finditer(self, text):
        # Yields (end_index, pattern_index)
        for end_idx, pat_idx in self._impl.iter(text):
            yield (end_idx, pat_idx)


def build_automaton(normalized_terms):
    auto = AutomatonWrapper()
    for idx, term in enumerate(normalized_terms):
        auto.add(term, idx)
    auto.finalize()
    return auto
