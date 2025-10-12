import string

BOUNDARY_CHARS = frozenset(" \t\n\r" + string.punctuation)


def span_overlaps_any(span, span_list):
    start_a, end_a = span
    for start_b, end_b in span_list:
        if start_a < end_b and start_b < end_a:
            return True
    return False
