__version__ = "0.2.0"
__description__ = "Fast lightweight NLP library for concept and segment extraction with negation/uncertainty detection."
__author__ = "Vidul Panickan"
__email__ = "apvidul@gmail.com"
__license__ = "MIT"

from .extractor import (
    convert_text_to_codes,
    extract_terms_with_window,
    flash_extractor,
    get_assertion_status,
    search_terms,
)

# Public API (functional only)
__all__ = [
    "flash_extractor",
    "search_terms",
    "extract_terms_with_window",
    "convert_text_to_codes",
    "get_assertion_status",
]
