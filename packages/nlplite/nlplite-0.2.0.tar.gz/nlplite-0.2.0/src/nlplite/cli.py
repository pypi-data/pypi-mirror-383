import argparse
import csv
import json
import sys
from pathlib import Path

from nlplite import (
    convert_text_to_codes,
    extract_terms_with_window,
    flash_extractor,
    get_assertion_status,
    search_terms,
)


def _read_text_arg(text_arg):
    if text_arg == "-":
        return ("stdin", sys.stdin.read())
    p = Path(text_arg)
    if p.exists() and p.is_file():
        return (p.name, p.read_text(encoding="utf-8"))
    return ("inline", text_arg)


def _parse_terms_arg(terms):
    if not terms:
        return []
    parsed_terms = []
    for item in terms:
        parts = [p.strip() for p in item.split(",")]
        for term in parts:
            if term:
                parsed_terms.append(term)
    return parsed_terms


def _parse_window(val):
    """
    Accepts:
      - integer (string) -> returns int
      - 'sentence' or 'paragraph' (case-insensitive) -> returns lowercase str
      - None -> returns None
    """
    if val is None:
        return None
    sval = str(val).strip().lower()
    if sval in ("sentence", "paragraph"):
        return sval
    try:
        num = int(sval)
        if num < 0:
            raise ValueError
        return num
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Invalid --window. Use a positive integer or 'sentence'/'paragraph'."
        )


def main():
    parser = argparse.ArgumentParser(
        prog="nlplite",
        description="Fast lightweight NLP library for concept extraction with negation/uncertainty detection.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=r"""
Examples:
  Search terms in inline text with sentence context:
    nlplite --search --terms "heart","heart failure" --text "Patient has heart failure. He denies chest pain." --window sentence

  Extract using a mapping file (with codes), include paragraph context and negation flags, without offsets:
    nlplite --extract --dict terms.csv --sep "," --text notes.txt --window paragraph --negation --no-offsets

  Convert text to unique codes:
    nlplite --convert --dict terms.csv --sep "," --text notes.txt --unique

  Assertion status with sentence context:
    nlplite --assertion --terms "heart failure","chest pain" --text "Patient denies chest pain but ?heart failure." --window sentence
""",
    )

    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--search", action="store_true", help="Search for ad-hoc terms in text."
    )
    modes.add_argument(
        "--extract",
        action="store_true",
        help="Extract terms using a dictionary (with optional codes).",
    )
    modes.add_argument(
        "--convert",
        action="store_true",
        help="Convert text to codes using a dictionary.",
    )
    modes.add_argument(
        "--assertion",
        action="store_true",
        help="Check negation/uncertainty status for specific terms.",
    )

    parser.add_argument(
        "--terms",
        nargs="+",
        help="Terms for --search/--assertion modes. Comma-separated or repeated.",
    )
    parser.add_argument(
        "--dict",
        dest="dictionary",
        help="Path to dictionary file for --extract/--convert modes.",
    )
    parser.add_argument(
        "--sep",
        default=None,
        help="Field separator for dictionary file (e.g., ',' or 'tab').",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Dictionary file has no header row (use with --dict).",
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Path to a text file, '-' to read from stdin, or an inline text string.",
    )
    parser.add_argument(
        "--window",
        default=None,
        type=_parse_window,
        help="Context window: integer for ±N characters, or 'sentence'/'paragraph' for full context.",
    )
    parser.add_argument(
        "--negation",
        action="store_true",
        help="Enable negation/uncertainty tagging (adds :Y/:N/:U).",
    )
    parser.add_argument(
        "--neg-window",
        type=int,
        default=None,
        help="Limit negation/uncertainty scope to N words (optional).",
    )
    parser.add_argument(
        "--unique",
        action="store_true",
        help="For --convert: output only unique codes (order preserved).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "text"],
        default="json",
        help="Output format: json (default), csv, text.",
    )

    # --- NEW: include_offsets CLI control (Py3.8-compatible) ---
    offsets_group = parser.add_mutually_exclusive_group()
    offsets_group.add_argument(
        "--include-offsets",
        dest="include_offsets",
        action="store_true",
        help="Include start/end offsets in results (default).",
    )
    offsets_group.add_argument(
        "--no-offsets",
        dest="include_offsets",
        action="store_false",
        help="Omit start/end offsets from results.",
    )
    parser.set_defaults(include_offsets=True)
    # -----------------------------------------------------------

    args = parser.parse_args()

    if args.search:
        if args.terms is None:
            parser.error("--search requires --terms.")
        if args.dictionary or args.extract or args.convert:
            parser.error("--search mode: do not use --dict or other mode flags.")

    if args.assertion:
        if args.terms is None:
            parser.error("--assertion requires --terms.")
        if args.dictionary or args.extract or args.convert:
            parser.error("--assertion mode: do not use --dict or other mode flags.")
        # NOTE: window IS allowed for assertion now.

    if args.extract or args.convert:
        if not args.dictionary:
            parser.error("--extract/--convert mode requires --dict <dictionary_file>.")
    if args.convert and args.window is not None:
        parser.error("--window is not supported with --convert mode.")

    sep = args.sep
    if sep is not None and isinstance(sep, str) and sep.lower() == "tab":
        sep = "\t"
    if sep == "":
        sep = None

    _note_id, text = _read_text_arg(args.text)

    output_data = []
    try:
        if args.search:
            terms_list = _parse_terms_arg(args.terms)
            output_data = search_terms(
                text,
                terms_list,
                window_size=args.window,
                include_offsets=args.include_offsets,
            )

        elif args.assertion:
            terms_list = _parse_terms_arg(args.terms)
            output_data = get_assertion_status(
                text,
                terms_list,
                include_offsets=args.include_offsets,
                negation_window=args.neg_window,
                window_size=args.window,
            )

        elif args.extract:
            output_data = extract_terms_with_window(
                text=text,
                dictionary=args.dictionary,
                sep=sep,
                header=(not args.no_header),
                window_size=args.window,
                include_code=None,
                include_offsets=args.include_offsets,
                negation_check=args.negation,
                negation_window=args.neg_window,
            )

        elif args.convert:
            output_data = convert_text_to_codes(
                text=text,
                dictionary=args.dictionary,
                sep=sep,
                header=(not args.no_header),
                include_offsets=args.include_offsets,
                negation_check=args.negation,
                negation_window=args.neg_window,
                unique=args.unique,
            )

    except Exception as e:
        parser.error("Error: %s" % e)

    if args.format == "json":
        print(json.dumps(output_data, ensure_ascii=False))

    elif args.format == "csv":
        writer = csv.writer(sys.stdout)
        if (
            isinstance(output_data, list)
            and output_data
            and isinstance(output_data[0], str)
        ):
            for code in output_data:
                writer.writerow([code])
        else:
            for row in output_data:
                row_values = []
                for field in row:
                    if isinstance(field, str):
                        row_values.append(field.replace("\n", "\\n"))
                    else:
                        row_values.append(field)
                writer.writerow(row_values)

    elif args.format == "text":
        if (
            isinstance(output_data, list)
            and output_data
            and isinstance(output_data[0], str)
        ):
            # Unique-code list (from --convert --unique)
            for code in output_data:
                base_code = code
                flag = None
                if len(code) > 2 and code[-2] == ":" and code[-1] in ("Y", "N", "U"):
                    base_code = code[:-2]
                    flag = code[-1]
                if flag:
                    meaning = {"Y": "affirmed", "N": "negated", "U": "uncertain"}[flag]
                    print("Code: %s (%s)" % (base_code, meaning))
                else:
                    print("Code: %s" % base_code)
        else:
            # Robust pretty-printer that tolerates missing offsets/context
            for row in output_data:
                if not isinstance(row, (list, tuple)):
                    print(str(row))
                    continue

                term = None
                code_val = None
                start_idx = None
                end_idx = None
                context_str = None

                # Normalize to list for easier indexing
                r = list(row)
                if not r:
                    print("")
                    continue

                # First element is always the (possibly flagged) term string
                term = r[0]
                i = 1

                # Optional code column (string or None) may follow
                if i < len(r) and (isinstance(r[i], str) or r[i] is None):
                    code_val = r[i]
                    i += 1

                # Optional offsets: two consecutive integers
                if (
                    i + 1 < len(r)
                    and isinstance(r[i], int)
                    and isinstance(r[i + 1], int)
                ):
                    start_idx = r[i]
                    end_idx = r[i + 1]
                    i += 2

                # Optional context: whatever remains (usually a string)
                if i < len(r):
                    context_str = r[i]

                # Decode :Y/:N/:U suffix on term
                flag = None
                term_str = str(term)
                if (
                    term_str.endswith(":Y")
                    or term_str.endswith(":N")
                    or term_str.endswith(":U")
                ):
                    flag = term_str[-1]
                    term_base = term_str[:-2]
                else:
                    term_base = term_str

                # Decode possible :Y/:N/:U suffixes in codes (if present)
                code_base = None
                if code_val is not None:
                    code_str = str(code_val)
                    code_parts = code_str.split(";") if code_str else []
                    cleaned = []
                    for cp in code_parts:
                        if cp.endswith(":Y") or cp.endswith(":N") or cp.endswith(":U"):
                            cleaned.append(cp[:-2])
                        else:
                            cleaned.append(cp)
                    code_base = ";".join(cleaned)

                text_line = "Term: %s" % term_base
                if flag:
                    meaning = {"Y": "affirmed", "N": "negated", "U": "uncertain"}[flag]
                    text_line += " (%s)" % meaning
                if code_base is not None:
                    code_display = code_base.replace(";", ", ")
                    label = "Code" if ";" not in code_base else "Codes"
                    text_line += ", %s: %s" % (label, code_display)
                if start_idx is not None and end_idx is not None:
                    text_line += ", Location: %s-%s" % (start_idx, end_idx)
                if context_str is not None:
                    ctx_clean = str(context_str).replace("\n", "\\n").strip()
                    text_line += ', Context: "%s"' % ctx_clean
                print(text_line)


if __name__ == "__main__":
    main()
