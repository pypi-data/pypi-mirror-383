import csv
import re
from pathlib import Path

from .automaton import build_automaton
from .negation import AdvancedSentencizer, NegEx
from .utils import BOUNDARY_CHARS, span_overlaps_any 


def _iterate_dictionary_items(dictionary_input, separator=None, header=True):
    if isinstance(dictionary_input, dict):
        for k, v in dictionary_input.items():
            if not isinstance(k, str):
                raise TypeError("All terms must be strings.")
            yield (k, v)
        return

    if isinstance(dictionary_input, list):
        if not dictionary_input:
            return
        first_item = dictionary_input[0]
        if isinstance(first_item, tuple) and len(first_item) == 2:
            for t, c in dictionary_input:
                if not isinstance(t, str):
                    raise TypeError("All terms must be strings.")
                yield (t, c)
        else:
            for t in dictionary_input:
                if not isinstance(t, str):
                    raise TypeError("All terms must be strings.")
                yield (t, None)
        return

    if isinstance(dictionary_input, str):
        p = Path(dictionary_input)
        if not p.exists():
            raise FileNotFoundError("Dictionary file not found: %s" % dictionary_input)
        with p.open("r", encoding="utf-8", newline="") as f:
            if separator is None or separator == "":
                if header:
                    next(f, None)
                for line in f:
                    term = line.strip()
                    if term:
                        yield (term, None)
            else:
                actual_sep = "\t" if str(separator).lower() == "tab" else separator
                reader = csv.reader(f, delimiter=actual_sep)
                _header_row = next(reader, None) if header else None
                for row in reader:
                    if not row:
                        continue
                    term = row[0]
                    code = row[1] if len(row) > 1 and row[1] != "" else None
                    if not isinstance(term, str):
                        raise TypeError("All terms must be strings.")
                    yield (term, code)
        return

    raise TypeError(
        "Unsupported dictionary type. Provide list[str], list[(str, code)], dict[str, code], or file path."
    )


def _make_code_adder(joiner):
    def _add(codes_list, codes_set, code_obj):
        if code_obj is None:
            return False
        added = False

        def _add_one(raw):
            nonlocal added
            if raw is None:
                return
            s = str(raw).strip()
            if not s or s in codes_set:
                return
            codes_set.add(s)
            codes_list.append(s)
            added = True

        if isinstance(code_obj, str):
            if joiner and joiner in code_obj:
                for part in code_obj.split(joiner):
                    _add_one(part)
            else:
                _add_one(code_obj)
        elif isinstance(code_obj, (list, tuple, set)):
            for item in code_obj:
                _add_one(item)
        else:
            _add_one(code_obj)
        return added

    return _add


def _prepare_patterns(dictionary_input, separator, header, joiner):
    term_map = {}  # key: lower(term) -> [original_term, list_of_codes, set_for_dupes]
    duplicates = 0
    add_codes = _make_code_adder(joiner)
    codes_available = False

    for term_original, code in _iterate_dictionary_items(
        dictionary_input, separator=separator, header=header
    ):
        term_raw = str(term_original).strip()
        if not term_raw:
            continue
        key = term_raw.lower()
        entry = term_map.get(key)
        if entry is None:
            entry = [term_raw, [], set()]
            term_map[key] = entry
        else:
            duplicates += 1
        if add_codes(entry[1], entry[2], code):
            codes_available = True

    patterns = (
        []
    )  # list of tuples: (original_term, code_str_or_None, normalized_term, term_length)
    for key, (term_orig, codes_list, _codes_set) in term_map.items():
        code_str = joiner.join(codes_list) if codes_list else None
        patterns.append((term_orig, code_str, key, len(key)))

    return patterns, codes_available, duplicates


def _determine_negation_scopes(text, negation_check, negation_window):
    if not negation_check:
        return [], []
    negex = NegEx()
    scopes = negex.scopes(text, window_words=negation_window)
    return scopes["negation"], scopes["uncertainty"]


def _paragraph_spans(text):
    """
    Return list of (start, end) paragraph spans, where paragraphs are separated by 2+ newlines.
    """
    spans = []
    n = len(text)
    last_end = 0
    for m in re.finditer(r"\n{2,}", text):
        spans.append((last_end, m.start()))
        last_end = m.end()
    if last_end < n:
        spans.append((last_end, n))
    return spans


def _match_terms_in_text(
    text,
    patterns,
    automaton,
    include_term_string,
    include_code_values,
    include_start_offset,
    include_end_offset,
    window_size,
    negation_check,
    neg_spans,
    unc_spans,
    joiner,
):
    n = len(text)
    if n == 0:
        return []

    # Determine context mode
    include_context = window_size is not None
    context_mode = None
    char_window = 0
    sentence_spans = []
    paragraph_spans = []

    if include_context:
        if isinstance(window_size, str):
            ws = window_size.strip().lower()
            if ws not in ("sentence", "paragraph"):
                raise ValueError(
                    "window_size must be an integer, 'sentence', or 'paragraph'."
                )
            context_mode = ws
            if context_mode == "sentence":
                sentencizer = AdvancedSentencizer()
                sentence_spans = sentencizer.span_tokenize(text)
            else:
                paragraph_spans = _paragraph_spans(text)
        else:
            context_mode = "char"
            char_window = int(window_size)
            if char_window < 0:
                char_window = 0

    text_norm = text.lower()
    best_for_start = {}

    for end_idx, pat_idx in automaton.finditer(text_norm):
        _, _, term_norm, term_len = patterns[pat_idx]
        start_idx = end_idx - term_len + 1
        if start_idx < 0:
            continue

        if text_norm[start_idx : end_idx + 1] != term_norm:
            continue

        if start_idx > 0 and (text[start_idx - 1] not in BOUNDARY_CHARS):
            continue
        if end_idx < n - 1 and (text[end_idx + 1] not in BOUNDARY_CHARS):
            continue

        prev = best_for_start.get(start_idx)
        if (prev is None) or (end_idx > prev[0]):
            best_for_start[start_idx] = (end_idx, pat_idx)

    results = []
    last_end = -1

    for s in sorted(best_for_start.keys()):
        e, pat_idx = best_for_start[s]
        if s <= last_end:
            continue
        term_original, code_str, _term_norm, _L = patterns[pat_idx]

        status_flag = None
        if negation_check:
            if span_overlaps_any((s, e + 1), neg_spans):
                status_flag = "N"
            elif span_overlaps_any((s, e + 1), unc_spans):
                status_flag = "U"
            else:
                status_flag = "Y"

        # Build context string according to mode
        context_str = None
        if include_context:
            if context_mode == "char":
                ctxL = max(0, s - char_window)
                ctxR = min(n, e + 1 + char_window)
                context_str = text[ctxL:ctxR]
            elif context_mode == "sentence":
                for ss, se in sentence_spans:
                    if ss <= s < se:
                        context_str = text[ss:se]
                        break
            elif context_mode == "paragraph":
                for ps, pe in paragraph_spans:
                    if ps <= s < pe:
                        context_str = text[ps:pe]
                        break

        row = []

        if include_term_string:
            out_str = text[s : e + 1]
            if negation_check and status_flag:
                out_str = "%s:%s" % (out_str, status_flag)
            row.append(out_str)

        if include_code_values:
            if code_str is None:
                row.append(None)
            else:
                if negation_check and status_flag:
                    parts = [p for p in code_str.split(joiner) if p]
                    row.append(joiner.join("%s:%s" % (p, status_flag) for p in parts))
                else:
                    row.append(code_str)

        if include_start_offset:
            row.append(s)
        if include_end_offset:
            row.append(e)
        if include_context:
            row.append("" if context_str is None else context_str)

        results.append(tuple(row))
        last_end = e

    return results


# -------------------- Public API (functional only) --------------------


def flash_extractor(
    text,
    dictionary,
    sep=None,
    header=True,
    include_term_string=True,
    include_code_values=None,  # None = include if codes exist; True = force; False = omit
    include_start_offset=True,
    include_end_offset=True,
    window_size=None,  # int, 'sentence', or 'paragraph'
    negation_check=False,
    negation_window=None,
    code_joiner=";",
):
    patterns, codes_available, _dupes = _prepare_patterns(
        dictionary, sep, header, code_joiner
    )

    if include_code_values is None:
        include_code_values = bool(codes_available)
    elif include_code_values and not codes_available:
        raise ValueError(
            "include_code_values=True requested but dictionary contains no code mappings."
        )

    normalized_terms = [p[2] for p in patterns]
    automaton = build_automaton(normalized_terms)

    neg_spans, unc_spans = _determine_negation_scopes(
        text, negation_check, negation_window
    )

    results = _match_terms_in_text(
        text=text,
        patterns=patterns,
        automaton=automaton,
        include_term_string=bool(include_term_string),
        include_code_values=bool(include_code_values),
        include_start_offset=bool(include_start_offset),
        include_end_offset=bool(include_end_offset),
        window_size=window_size,
        negation_check=bool(negation_check),
        neg_spans=neg_spans,
        unc_spans=unc_spans,
        joiner=code_joiner,
    )
    return results


def search_terms(text, terms, window_size=None, include_offsets=True):
    """
    window_size can be:
      - int N: include ±N characters of context
      - 'sentence': include full sentence
      - 'paragraph': include full paragraph (split by 2+ newlines)
    """
    term_list = [t.strip() for t in terms if str(t).strip()]
    if not term_list:
        return []
    return flash_extractor(
        text=text,
        dictionary=term_list,
        sep=None,
        header=True,
        include_term_string=True,
        include_code_values=False,
        include_start_offset=bool(include_offsets),
        include_end_offset=bool(include_offsets),
        window_size=window_size,
        negation_check=False,
        negation_window=None,
        code_joiner=";",
    )


def extract_terms_with_window(
    text,
    dictionary,
    sep=None,
    header=True,
    window_size=None,  # int, 'sentence', or 'paragraph'
    include_code=None,
    include_offsets=True,
    negation_check=False,
    negation_window=None,
):
    """
    window_size can be:
      - int N: include ±N characters of context
      - 'sentence': include full sentence
      - 'paragraph': include full paragraph (split by 2+ newlines)
    """
    return flash_extractor(
        text=text,
        dictionary=dictionary,
        sep=sep,
        header=header,
        include_term_string=True,
        include_code_values=include_code,
        include_start_offset=bool(include_offsets),
        include_end_offset=bool(include_offsets),
        window_size=window_size,
        negation_check=bool(negation_check),
        negation_window=negation_window,
        code_joiner=";",
    )


def convert_text_to_codes(
    text,
    dictionary,
    sep=None,
    header=True,
    include_offsets=True,
    negation_check=False,
    negation_window=None,
    unique=False,
):
    rows = flash_extractor(
        text=text,
        dictionary=dictionary,
        sep=sep,
        header=header,
        include_term_string=False,
        include_code_values=True,  # require codes
        include_start_offset=bool(include_offsets),
        include_end_offset=bool(include_offsets),
        window_size=None,  # context not applicable here
        negation_check=bool(negation_check),
        negation_window=negation_window,
        code_joiner=";",
    )
    if not unique:
        return rows

    seen = set()
    unique_codes = []
    for r in rows:
        code_value = r[0]  # when term_string=False, first element is code
        if code_value not in seen:
            seen.add(code_value)
            unique_codes.append(code_value)
    return unique_codes


def get_assertion_status(
    text,
    terms,
    include_offsets=True,
    negation_window=None,
    window_size=None,  # NEW: support context here too (optional)
):
    """
    Returns assertion for each occurrence of provided terms.
    If window_size is provided (int/'sentence'/'paragraph'), include context at the end.
    """
    term_list = [t.strip() for t in terms if str(t).strip()]
    if not term_list:
        return []
    return flash_extractor(
        text=text,
        dictionary=term_list,
        sep=None,
        header=True,
        include_term_string=True,
        include_code_values=False,
        include_start_offset=bool(include_offsets),
        include_end_offset=bool(include_offsets),
        window_size=window_size,  # allow sentence/paragraph/char context
        negation_check=True,
        negation_window=negation_window,
        code_joiner=";",
    )
