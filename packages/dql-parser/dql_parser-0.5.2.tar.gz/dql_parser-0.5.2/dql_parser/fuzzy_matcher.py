"""
Fuzzy matching utilities for error message suggestions.

Provides string similarity matching to suggest corrections for typos
and unknown operators.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import List, Tuple


def fuzzy_match(
    input_str: str,
    candidates: List[str],
    threshold: float = 0.7,
    max_results: int = 3,
) -> List[Tuple[str, float]]:
    """
    Find similar strings using sequence matching.

    Args:
        input_str: The input string to match against
        candidates: List of valid candidate strings
        threshold: Minimum similarity ratio (0.0-1.0), default 0.7 (70%)
        max_results: Maximum number of results to return, default 3

    Returns:
        List of (candidate, similarity_ratio) tuples, sorted by similarity (descending)

    Example:
        >>> candidates = ["to_not_be_null", "to_be_null", "to_match_pattern"]
        >>> fuzzy_match("to_not_null", candidates, threshold=0.7)
        [('to_not_be_null', 0.93), ('to_be_null', 0.76)]
    """
    matches: List[Tuple[str, float]] = []

    input_lower = input_str.lower()

    for candidate in candidates:
        candidate_lower = candidate.lower()

        # Calculate sequence similarity ratio
        ratio = SequenceMatcher(None, input_lower, candidate_lower).ratio()

        if ratio >= threshold:
            matches.append((candidate, ratio))

    # Sort by similarity (descending) and return top N
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:max_results]


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings.

    Args:
        str1: First string
        str2: Second string

    Returns:
        Similarity ratio between 0.0 and 1.0

    Example:
        >>> calculate_similarity("to_not_null", "to_not_be_null")
        0.93
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def levenshtein_distance(str1: str, str2: str) -> int:
    """
    Calculate Levenshtein edit distance between two strings.

    This is the minimum number of single-character edits (insertions,
    deletions, or substitutions) required to change one string into the other.

    Args:
        str1: First string
        str2: Second string

    Returns:
        Edit distance as integer

    Example:
        >>> levenshtein_distance("to_not_null", "to_not_be_null")
        3  # Need to insert 'b', 'e', '_'
    """
    len1, len2 = len(str1), len(str2)

    # Create distance matrix
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # Initialize first column and row
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j

    # Fill in the matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1].lower() == str2[j - 1].lower():
                # Characters match, no operation needed
                matrix[i][j] = matrix[i - 1][j - 1]
            else:
                # Take minimum of insert, delete, or substitute
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # deletion
                    matrix[i][j - 1] + 1,  # insertion
                    matrix[i - 1][j - 1] + 1,  # substitution
                )

    return matrix[len1][len2]


def fuzzy_match_by_edit_distance(
    input_str: str,
    candidates: List[str],
    max_distance: int = 2,
    max_results: int = 3,
) -> List[Tuple[str, int]]:
    """
    Find similar strings using Levenshtein edit distance.

    Args:
        input_str: The input string to match against
        candidates: List of valid candidate strings
        max_distance: Maximum edit distance to consider, default 2
        max_results: Maximum number of results to return, default 3

    Returns:
        List of (candidate, edit_distance) tuples, sorted by distance (ascending)

    Example:
        >>> candidates = ["to_not_be_null", "to_be_null", "to_match_pattern"]
        >>> fuzzy_match_by_edit_distance("to_not_null", candidates, max_distance=3)
        [('to_not_be_null', 3), ('to_be_null', 4)]
    """
    matches: List[Tuple[str, int]] = []

    for candidate in candidates:
        distance = levenshtein_distance(input_str, candidate)

        if distance <= max_distance:
            matches.append((candidate, distance))

    # Sort by edit distance (ascending) and return top N
    matches.sort(key=lambda x: x[1])
    return matches[:max_results]
