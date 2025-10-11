"""
Common typo mappings and valid operator/keyword lists.

This module contains dictionaries of common typos and their corrections,
as well as lists of valid DQL operators and keywords for fuzzy matching.
"""

from typing import Dict, List

# Common typo mappings: incorrect → correct
COMMON_TYPOS: Dict[str, str] = {
    # Missing "be"
    "to_not_null": "to_not_be_null",
    "to_null": "to_be_null",

    # Misspelled operators
    "to_be_betwen": "to_be_between",
    "to_be_betwee": "to_be_between",
    "to_be_beetween": "to_be_between",

    "to_match_patern": "to_match_pattern",
    "to_match_patter": "to_match_pattern",
    "to_match_pattrn": "to_match_pattern",

    "to_be_uniqu": "to_be_unique",
    "to_be_uniq": "to_be_unique",
    "to_be_unic": "to_be_unique",

    "to_referenc": "to_reference",
    "to_refrence": "to_reference",
    "to_referance": "to_reference",

    "to_have_lenght": "to_have_length",
    "to_have_lenth": "to_have_length",

    "to_be_greater_then": "to_be_greater_than",
    "to_be_grater_than": "to_be_greater_than",

    "to_be_less_then": "to_be_less_than",
    "to_be_les_than": "to_be_less_than",

    "to_satisf": "to_satisfy",
    "to_satsify": "to_satisfy",

    # Case variations (should be lowercase)
    "TO_BE_NULL": "to_be_null",
    "TO_NOT_BE_NULL": "to_not_be_null",
    "TO_MATCH_PATTERN": "to_match_pattern",
    "TO_BE_BETWEEN": "to_be_between",
    "TO_BE_IN": "to_be_in",
    "TO_BE_UNIQUE": "to_be_unique",
    "TO_REFERENCE": "to_reference",
    "TO_HAVE_LENGTH": "to_have_length",
    "TO_BE_GREATER_THAN": "to_be_greater_than",
    "TO_BE_LESS_THAN": "to_be_less_than",
    "TO_SATISFY": "to_satisfy",
}

# All valid DQL operators
VALID_OPERATORS: List[str] = [
    "to_be_null",
    "to_not_be_null",
    "to_match_pattern",
    "to_be_between",
    "to_be_in",
    "to_be_unique",
    "to_reference",
    "to_have_length",
    "to_be_greater_than",
    "to_be_less_than",
    "to_satisfy",
]

# All valid DQL keywords
VALID_KEYWORDS: List[str] = [
    "from",
    "expect",
    "column",
    "row",
    "where",
    "severity",
    "critical",
    "warning",
    "info",
    "on_failure",
    "clean_with",
    "null",
    "and",
    "or",
    "not",
]

# Valid string functions (must be UPPERCASE in DQL)
VALID_STRING_FUNCTIONS: List[str] = [
    "UPPER",
    "LOWER",
    "TRIM",
    "LENGTH",
    "CONCAT",
]

# Valid date functions (must be UPPERCASE in DQL)
VALID_DATE_FUNCTIONS: List[str] = [
    "YEAR",
    "MONTH",
    "DAY",
    "AGE",
]

# All valid functions combined
VALID_FUNCTIONS: List[str] = VALID_STRING_FUNCTIONS + VALID_DATE_FUNCTIONS


def get_typo_correction(typo: str) -> str:
    """
    Get the correction for a common typo.

    Args:
        typo: The typo string

    Returns:
        Corrected string if typo is known, otherwise the original string

    Example:
        >>> get_typo_correction("to_not_null")
        'to_not_be_null'
        >>> get_typo_correction("unknown_typo")
        'unknown_typo'
    """
    return COMMON_TYPOS.get(typo.lower(), typo)


def is_case_error(input_str: str, valid_list: List[str]) -> bool:
    """
    Check if input matches a valid item but with wrong case.

    Args:
        input_str: Input string to check
        valid_list: List of valid strings (correct case)

    Returns:
        True if input matches a valid item (case-insensitive) but not exact case

    Example:
        >>> is_case_error("TO_BE_NULL", VALID_OPERATORS)
        True
        >>> is_case_error("to_be_null", VALID_OPERATORS)
        False  # Correct case
        >>> is_case_error("to_be_invalid", VALID_OPERATORS)
        False  # Not in list at all
    """
    input_lower = input_str.lower()

    for valid_item in valid_list:
        if input_lower == valid_item.lower() and input_str != valid_item:
            return True

    return False


def get_correct_case(input_str: str, valid_list: List[str]) -> str:
    """
    Get the correct case version of an input string.

    Args:
        input_str: Input string (possibly wrong case)
        valid_list: List of valid strings (correct case)

    Returns:
        Correct case version if found, otherwise the original string

    Example:
        >>> get_correct_case("TO_BE_NULL", VALID_OPERATORS)
        'to_be_null'
        >>> get_correct_case("upper", VALID_STRING_FUNCTIONS)
        'UPPER'
    """
    input_lower = input_str.lower()

    for valid_item in valid_list:
        if input_lower == valid_item.lower():
            return valid_item

    return input_str
