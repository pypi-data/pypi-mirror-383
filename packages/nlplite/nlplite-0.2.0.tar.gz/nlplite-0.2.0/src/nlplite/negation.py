import re


class AdvancedSentencizer(object):
    def __init__(self):
        self.abbrevs = set(
            [
                "dr",
                "mr",
                "mrs",
                "ms",
                "vs",
                "etc",
                "inc",
                "corp",
                "pt",
                "pts",
                "no",
                "fig",
                "est",
                "approx",
                "jan",
                "feb",
                "mar",
                "apr",
                "jun",
                "jul",
                "aug",
                "sep",
                "sept",
                "oct",
                "nov",
                "dec",
                "hr",
                "min",
            ]
        )
        self._abbrev_re = re.compile(
            r"\b(" + "|".join(re.escape(a) for a in self.abbrevs) + r")\.$",
            re.IGNORECASE,
        )

    def span_tokenize(self, text):
        spans = []
        start = 0
        i = 0
        n = len(text)

        while i < n:
            ch = text[i]

            if ch in ".!?;":
                window = text[max(0, i - 12) : i + 1]
                if not self._abbrev_re.search(window):
                    j = i + 1
                    while j < n and text[j].isspace():
                        j += 1
                    if start < i + 1:
                        spans.append((start, i + 1))
                    start = j
                    i = j
                    continue

            elif ch == "\n":
                j = i + 1
                while j < n and text[j].isspace():
                    j += 1
                if start < i + 1:
                    spans.append((start, i + 1))
                start = j
                i = j
                continue

            i += 1

        if start < n:
            spans.append((start, n))

        return [(s, e) for s, e in spans if s < e]


class NegEx(object):
    def __init__(self):
        self.PRE_NEG = list(
            dict.fromkeys(
                [
                    "no",
                    "none",
                    "never",
                    "without",
                    "without any",
                    "absence of",
                    "absent of",
                    "lack of",
                    "lacking",
                    "lacks",
                    "no evidence of",
                    "no evidence for",
                    "no evidence to suggest",
                    "no sign of",
                    "no signs of",
                    "no clinical signs of",
                    "no indication of",
                    "no indications of",
                    "no clinical indication of",
                    "no suggestion of",
                    "not suggestive of",
                    "no history of",
                    "no prior history of",
                    "no past history of",
                    "no previous history of",
                    "no known history of",
                    "negative history of",
                    "negative hx of",
                    "no documented",
                    "no documentation of",
                    "no report of",
                    "no reported",
                    "denies",
                    "denied",
                    "denying",
                    "negative for",
                    "neg for",
                    "fails to reveal",
                    "fail to reveal",
                    "failed to reveal",
                    "failure to reveal",
                    "did not show",
                    "didn't show",
                    "does not show",
                    "doesn't show",
                    "do not show",
                    "don't show",
                    "did not demonstrate",
                    "didn't demonstrate",
                    "does not demonstrate",
                    "doesn't demonstrate",
                    "did not reveal",
                    "didn't reveal",
                    "does not reveal",
                    "doesn't reveal",
                    "did not find",
                    "didn't find",
                    "does not find",
                    "doesn't find",
                    "found no",
                    "did not identify",
                    "didn't identify",
                    "does not identify",
                    "doesn't identify",
                    "did not detect",
                    "didn't detect",
                    "does not detect",
                    "doesn't detect",
                    "not detected",
                    "undetected",
                    "not visualized",
                    "not appreciated",
                    "no abnormality",
                    "no abnormalities",
                    "unremarkable for",
                    "no acute",
                    "no new acute",
                    "no focal",
                    "no gross",
                    "no obvious",
                    "no significant",
                    "no clinically significant",
                    "no appreciable",
                    "not appreciable",
                    "free of",
                    "free from",
                    "cleared of",
                    "no longer",
                    "no more",
                    "rules out",
                    "effectively rules out",
                    "not",
                    "the same is true for",
                    "no complaints of",
                    "not associated with",
                    "does not have",
                    "do not have",
                    "did not have",
                    "doesn't have",
                    "don't have",
                    "didn't have",
                    "did not complain of",
                    "does not complain of",
                    "didn't complain of",
                    "doesn't complain of",
                    "did not experience",
                    "does not experience",
                    "didn't experience",
                    "doesn't experience",
                    "never had",
                    "never developed",
                    "did not develop",
                    "does not develop",
                    "didn't develop",
                    "doesn't develop",
                    "did not exhibit",
                    "does not exhibit",
                    "didn't exhibit",
                    "doesn't exhibit",
                    "did not display",
                    "does not display",
                    "didn't display",
                    "doesn't display",
                    "did not manifest",
                    "does not manifest",
                    "didn't manifest",
                    "doesn't manifest",
                    "failed to identify",
                    "fails to identify",
                    "failure to identify",
                    "failed to detect",
                    "fails to detect",
                    "failure to detect",
                    "failed to demonstrate",
                    "fails to demonstrate",
                    "failure to demonstrate",
                    "failed to appreciate",
                    "fails to appreciate",
                    "failure to appreciate",
                    "unable to identify",
                    "unable to detect",
                    "unable to visualize",
                    "unable to demonstrate",
                    "unable to find",
                    "unable to see",
                    "unable to appreciate",
                    "unable to locate",
                    "unable to elicit",
                    "clear of",
                    "asymptomatic",
                    "asymptomatic for",
                ]
            )
        )

        self.POST_NEG = list(
            dict.fromkeys(
                [
                    "absent",
                    "is absent",
                    "was absent",
                    "are absent",
                    "were absent",
                    "not present",
                    "is not present",
                    "was not present",
                    "not seen",
                    "is not seen",
                    "was not seen",
                    "were not seen",
                    "not found",
                    "is not found",
                    "was not found",
                    "not identified",
                    "is not identified",
                    "was not identified",
                    "not demonstrated",
                    "is not demonstrated",
                    "was not demonstrated",
                    "not evident",
                    "is not evident",
                    "was not evident",
                    "not observed",
                    "is not observed",
                    "was not observed",
                    "not visualized",
                    "is not visualized",
                    "was not visualized",
                    "not appreciated",
                    "is not appreciated",
                    "was not appreciated",
                    "not noted",
                    "is not noted",
                    "was not noted",
                    "not detected",
                    "is not detected",
                    "was not detected",
                    "was ruled out",
                    "were ruled out",
                    "is ruled out",
                    "are ruled out",
                    "has been ruled out",
                    "have been ruled out",
                    "had been ruled out",
                    "was excluded",
                    "were excluded",
                    "is excluded",
                    "are excluded",
                    "has been excluded",
                    "have been excluded",
                    "had been excluded",
                    "ruled out by",
                    "effectively ruled out",
                    "resolved",
                    "has resolved",
                    "have resolved",
                    "had resolved",
                    "cleared",
                    "has cleared",
                    "have cleared",
                    "subsided",
                    "has subsided",
                    "is negative",
                    "was negative",
                    "are negative",
                    "were negative",
                    "came back negative",
                    "returned negative",
                    "resulted negative",
                    "tested negative",
                    "screens negative",
                    "negative",
                    "unlikely",
                    "highly unlikely",
                    "very unlikely",
                    "doubtful",
                    "improbable",
                    "isn't present",
                    "wasn't present",
                    "aren't present",
                    "weren't present",
                    "isn't seen",
                    "wasn't seen",
                    "aren't seen",
                    "weren't seen",
                    "isn't found",
                    "wasn't found",
                    "aren't found",
                    "weren't found",
                    "isn't identified",
                    "wasn't identified",
                    "isn't demonstrated",
                    "wasn't demonstrated",
                    "isn't evident",
                    "wasn't evident",
                    "isn't observed",
                    "wasn't observed",
                    "isn't visualized",
                    "wasn't visualized",
                    "isn't appreciated",
                    "wasn't appreciated",
                    "isn't noted",
                    "wasn't noted",
                    "isn't detected",
                    "wasn't detected",
                    "free",
                    "afebrile",
                    "gone",
                    "has gone",
                    "have gone",
                    "had gone",
                    "disappeared",
                    "has disappeared",
                    "have disappeared",
                    "had disappeared",
                    "ceased",
                    "has ceased",
                    "have ceased",
                    "had ceased",
                ]
            )
        )

        self.PRE_UNC = list(
            dict.fromkeys(
                [
                    "rule out",
                    "r/o",
                    "ro",
                    "to rule out",
                    "to r/o",
                    "evaluate for",
                    "eval for",
                    "work up for",
                    "workup for",
                    "monitor for",
                    "monitoring for",
                    "observe for",
                    "observation for",
                    "watch for",
                    "follow for",
                    "follow-up for",
                    "following for",
                    "correlate clinically",
                    "clinical correlation advised",
                    "clinical correlation recommended",
                    "possible",
                    "possibly",
                    "probable",
                    "probably",
                    "potential",
                    "potentially",
                    "perhaps",
                    "may be",
                    "might be",
                    "could be",
                    "can be",
                    "may have",
                    "might have",
                    "could have",
                    "may represent",
                    "might represent",
                    "could represent",
                    "suspect",
                    "suspicion for",
                    "suspicion of",
                    "suspicious for",
                    "worry for",
                    "worrisome for",
                    "consider",
                    "consideration for",
                    "under consideration",
                    "differential includes",
                    "ddx includes",
                    "question of",
                    "questionable",
                    "raises question of",
                    "raises concern for",
                    "compatible with",
                    "consistent with",
                    "equivocal",
                    "indeterminate",
                    "unclear",
                    "uncertain",
                    "impression of",
                    "appears to be",
                    "seems to be",
                    "thought to be",
                    "favors",
                    "more likely",
                    "most likely",
                    "less likely",
                    "hold",
                    "suspected",
                    "presumed",
                    "presumptive",
                    "maybe",
                    "concern for",
                    "likely",
                ]
            )
        )

        self.POST_UNC = list(
            dict.fromkeys(
                [
                    "cannot be ruled out",
                    "can not be ruled out",
                    "can't be ruled out",
                    "cannot be entirely ruled out",
                    "cannot be completely ruled out",
                    "could not be ruled out",
                    "may not be ruled out",
                    "might not be ruled out",
                    "remains to be ruled out",
                    "cannot be excluded",
                    "can not be excluded",
                    "can't be excluded",
                    "could not be excluded",
                    "may not be excluded",
                    "might not be excluded",
                    "not excluded",
                    "not be excluded",
                    "is possible",
                    "was possible",
                    "remains possible",
                    "is likely",
                    "was likely",
                    "remains likely",
                    "is probable",
                    "was probable",
                    "under investigation",
                    "being investigated",
                    "under evaluation",
                    "being evaluated",
                    "being worked up",
                    "undergoing workup",
                    "is suspected",
                    "was suspected",
                    "remains suspected",
                    "is unclear",
                    "was unclear",
                    "remains unclear",
                ]
            )
        )

        self.PSEUDO = list(
            dict.fromkeys(
                [
                    "not rule out",
                    "not be ruled out",
                    "cannot rule out",
                    "can not rule out",
                    "can't rule out",
                    "could not rule out",
                    "may not rule out",
                    "might not rule out",
                    "cannot completely rule out",
                    "cannot entirely rule out",
                    "cannot be completely ruled out",
                    "cannot be entirely ruled out",
                    "cannot exclude",
                    "can not exclude",
                    "can't exclude",
                    "could not exclude",
                    "may not exclude",
                    "might not exclude",
                    "cannot be excluded",
                    "can not be excluded",
                    "can't be excluded",
                    "could not be excluded",
                    "may not be excluded",
                    "might not be excluded",
                    "not excluded",
                    "not be excluded",
                    "no doubt that",
                    "no doubt about",
                    "no question that",
                    "without doubt",
                    "definitely has",
                    "certainly has",
                    "clearly has",
                    "obviously has",
                    "undoubtedly has",
                    "not only",
                    "not necessarily",
                    "not certain if",
                    "not certain whether",
                    "not sure if",
                    "not sure whether",
                    "not known if",
                    "not clear if",
                    "no change in",
                    "no significant change",
                    "no interval change",
                    "no increase in",
                    "no decrease in",
                    "no improvement in",
                    "no worsening in",
                    "no worsening of",
                    "gram-negative",
                    "gram negative",
                    "not to pursue",
                    "no denying",
                    "no denying that",
                    "cannot deny",
                    "can't deny",
                    "not out of the question",
                    "unable to rule out",
                    "unable to exclude",
                ]
            )
        )

        self.TERMINATORS = list(
            dict.fromkeys(
                [
                    "but",
                    "however",
                    "except",
                    "other than",
                    "rather than",
                    "aside from",
                    "apart from",
                    "although",
                    "though",
                    "yet",
                    "nevertheless",
                    "whereas",
                ]
            )
        )

        self.TEMPORAL_TERMINATORS = list(
            dict.fromkeys(
                [
                    "now",
                    "currently",
                    "presently",
                    "today",
                    "tonight",
                    "this morning",
                    "this afternoon",
                    "this evening",
                    "at present",
                    "right now",
                    "at this time",
                    "presenting with",
                    "presents with",
                    "presented with",
                    "on presentation",
                    "developed",
                    "subsequently",
                    "later",
                    "since",
                    "since then",
                    "post-op",
                    "postoperative",
                    "postoperatively",
                    "post op",
                ]
            )
        )

        self.REENTRY_AFTER_COMMA = list(
            dict.fromkeys(
                [
                    "reports",
                    "reporting",
                    "reported",
                    "states",
                    "stated",
                    "notes",
                    "noted",
                    "noting",
                    "describes",
                    "described",
                    "describing",
                    "complains of",
                    "complaining of",
                    "endorses",
                    "admits to",
                    "admitting to",
                    "admitted to",
                    "presents with",
                    "presenting with",
                    "presented with",
                    "developed",
                    "now",
                    "currently",
                    "today",
                    "at present",
                ]
            )
        )

        self.RELATIVE_PRONOUNS = ["which", "that", "who", "whom", "whose"]

        self._coord_re = re.compile(r"(,|/|\band\b|\bor\b|\bnor\b)", re.IGNORECASE)
        self._relpron_re = self._compile_phrase_list(self.RELATIVE_PRONOUNS)
        self._reentry_re = self._compile_phrase_list(self.REENTRY_AFTER_COMMA)
        self._pre_neg_re = self._compile_phrase_list(self.PRE_NEG)
        self._post_neg_re = self._compile_post_with_hyphen_safe_negative(self.POST_NEG)
        self._pre_unc_re = self._compile_phrase_list(self.PRE_UNC)
        self._post_unc_re = self._compile_phrase_list(self.POST_UNC)
        self._term_re = self._compile_phrase_list(
            self.TERMINATORS + self.TEMPORAL_TERMINATORS
        )
        self._pseudo_re = self._compile_phrase_list(self.PSEUDO)
        self._qmark_unc_re = re.compile(r"(?<!\w)\?(?=\s*\w)", re.IGNORECASE)
        self._pre_neg_abbrev_re = re.compile(
            r"(?<!\w)(?:neg(?:ative)?\s+for|-\s*ve\s+for|\(-\)\s*for)\b", re.IGNORECASE
        )
        self._word_re = re.compile(r"\w+")
        self._sentencizer = AdvancedSentencizer()

    def _compile_phrase_list(self, phrases):
        parts = []
        for p in phrases:
            esc = re.escape(p.lower()).replace(r"\ ", r"\s+")
            parts.append("(?:%s)" % esc)
        if parts:
            return re.compile(r"\b(?:%s)\b" % "|".join(parts), re.IGNORECASE)
        return re.compile(r"$^")

    def _compile_post_with_hyphen_safe_negative(self, phrases):
        parts = []
        for p in phrases:
            if p == "negative":
                parts.append(r"(?<!-)\bnegative\b")
            else:
                esc = re.escape(p.lower()).replace(r"\ ", r"\s+")
                parts.append("(?:%s)" % esc)
        if parts:
            return re.compile(r"\b(?:%s)\b" % "|".join(parts), re.IGNORECASE)
        return re.compile(r"$^")

    def scopes(self, text, window_words):
        neg_all = []
        unc_all = []
        for s0, s1 in self._sentencizer.span_tokenize(text):
            sent = text[s0:s1]
            n_sp, u_sp = self._scopes_in_sentence(sent, s0, window_words)
            neg_all.extend(n_sp)
            unc_all.extend(u_sp)
        return {
            "negation": self._merge_spans(neg_all),
            "uncertainty": self._merge_spans(unc_all),
        }

    def _scopes_in_sentence(self, sent, base, window_words):
        neg_spans = []
        unc_spans = []
        length = len(sent)
        pseudo_ranges = [(m.start(), m.end()) for m in self._pseudo_re.finditer(sent)]

        def overlapped(a, b, c, d):
            return not (b <= c or a >= d)

        def in_pseudo(a, b):
            for ps, pe in pseudo_ranges:
                if overlapped(a, b, ps, pe):
                    return True
            return False

        term_spans = [(m.start(), m.end()) for m in self._term_re.finditer(sent)]
        for m in self._reentry_re.finditer(sent):
            i = m.start() - 1
            while i >= 0 and sent[i].isspace():
                i -= 1
            if i >= 0 and sent[i] == ",":
                term_spans.append((m.start(), m.end()))
        term_spans.sort()
        term_starts = [s for s, _ in term_spans]
        term_ends = [e for _, e in term_spans]

        rel_starts = [m.start() for m in self._relpron_re.finditer(sent)]
        coord_ends = [m.end() for m in self._coord_re.finditer(sent)]

        def next_term_after(idx):
            for st in term_starts:
                if st > idx:
                    return st
            return length

        def prev_term_before(idx):
            prev = 0
            for en in term_ends:
                if en < idx:
                    prev = en
                else:
                    break
            return prev

        def last_relpron_before(idx):
            last = None
            for st in rel_starts:
                if st < idx:
                    last = st
                else:
                    break
            return last

        def last_coord_end_before(idx):
            prev = 0
            for en in coord_ends:
                if en <= idx:
                    prev = en
                else:
                    break
            return prev

        words = list(re.finditer(r"\w+", sent))

        def right_window_limit(idx, N):
            if not N:
                return length
            count = 0
            endpos = length
            for m in words:
                if m.end() <= idx:
                    continue
                count += 1
                endpos = m.end()
                if count >= N:
                    break
            return endpos

        def left_window_limit(idx, N):
            if not N:
                return 0
            left_words = [m for m in words if m.end() <= idx]
            if not left_words:
                return 0
            i = max(0, len(left_words) - N)
            return left_words[i].start()

        for m in self._pre_neg_re.finditer(sent):
            a, b = m.start(), m.end()
            if not in_pseudo(a, b):
                scope_start = b
                scope_end = next_term_after(b)
                if window_words:
                    scope_end = min(scope_end, right_window_limit(b, window_words))
                if scope_start < scope_end:
                    neg_spans.append((base + scope_start, base + scope_end))

        for m in self._pre_neg_abbrev_re.finditer(sent):
            a, b = m.start(), m.end()
            if not in_pseudo(a, b):
                scope_start = b
                scope_end = min(next_term_after(b), right_window_limit(b, 6))
                if scope_start < scope_end:
                    neg_spans.append((base + scope_start, base + scope_end))

        for m in self._post_neg_re.finditer(sent):
            a, b = m.start(), m.end()
            if in_pseudo(a, b):
                continue
            scope_end = a
            scope_start = prev_term_before(a)
            rp = last_relpron_before(a)
            if rp is not None:
                cut = last_coord_end_before(rp)
                if cut > scope_start:
                    scope_start = cut
            if window_words:
                scope_start = max(scope_start, left_window_limit(a, window_words))
            if scope_start < scope_end:
                neg_spans.append((base + scope_start, base + scope_end))

        for m in self._pre_unc_re.finditer(sent):
            a, b = m.start(), m.end()
            scope_start = b
            scope_end = next_term_after(b)
            if window_words:
                scope_end = min(scope_end, right_window_limit(b, window_words))
            if scope_start < scope_end:
                unc_spans.append((base + scope_start, base + scope_end))

        for m in self._qmark_unc_re.finditer(sent):
            a, b = m.start(), m.end()
            scope_start = b
            scope_end = min(next_term_after(b), right_window_limit(b, 2))
            if scope_start < scope_end:
                unc_spans.append((base + scope_start, base + scope_end))

        for m in self._post_unc_re.finditer(sent):
            a, b = m.start(), m.end()
            scope_end = a
            scope_start = prev_term_before(a)
            rp = last_relpron_before(a)
            if rp is not None:
                cut = last_coord_end_before(rp)
                if cut > scope_start:
                    scope_start = cut
            if window_words:
                scope_start = max(scope_start, left_window_limit(a, window_words))
            if scope_start < scope_end:
                unc_spans.append((base + scope_start, base + scope_end))

        NEITHER = re.compile(r"\bneither\b", re.IGNORECASE)
        NOR = re.compile(r"\bnor\b", re.IGNORECASE)
        for m_nei in NEITHER.finditer(sent):
            nei_end = m_nei.end()
            m_nor = NOR.search(sent, nei_end)
            if not m_nor:
                scope_start = nei_end
                scope_end = next_term_after(nei_end)
                if window_words:
                    scope_end = min(
                        scope_end, right_window_limit(nei_end, window_words)
                    )
                if scope_start < scope_end:
                    neg_spans.append((base + scope_start, base + scope_end))
            else:
                nor_start = m_nor.start()
                nor_end = m_nor.end()
                if nei_end < nor_start:
                    neg_spans.append((base + nei_end, base + nor_start))
                right_end = next_term_after(nor_end)
                if window_words:
                    right_end = min(
                        right_end, right_window_limit(nor_end, window_words)
                    )
                if nor_end < right_end:
                    neg_spans.append((base + nor_end, base + right_end))

        return neg_spans, unc_spans

    def _merge_spans(self, spans):
        if not spans:
            return []
        spans.sort()
        merged = [spans[0]]
        for s, e in spans[1:]:
            ls, le = merged[-1]
            if s <= le:
                merged[-1] = (ls, max(le, e))
            else:
                merged.append((s, e))
        return merged
