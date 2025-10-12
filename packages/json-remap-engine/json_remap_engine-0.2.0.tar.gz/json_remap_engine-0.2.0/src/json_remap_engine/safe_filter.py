"""
Safe filter evaluation for JSONPath expressions with existence checking.

This module implements JavaScript-style safe navigation for filter expressions
by parsing and evaluating them in Python instead of relying on jsonpath-ng.
"""

import re
from typing import Any


def _safe_get_nested(obj: Any, path: str) -> tuple[bool, Any]:
    """
    Safely get a nested property from an object.

    Args:
        obj: The object to traverse
        path: Dot-separated path (e.g., "inspection.meta.status")

    Returns:
        Tuple of (exists, value). If exists is False, value is None.
    """
    if not isinstance(obj, dict):
        return False, None

    parts = path.split(".")
    current = obj

    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]

    return True, current


def _evaluate_filter_condition(item: Any, condition: str) -> bool:
    """
    Evaluate a filter condition with safe navigation.

    Supports expressions like:
    - @.inspection && @.inspection.meta && @.inspection.meta.status == 'OK'
    - @.field == value
    - @.field > value

    Args:
        item: The current item being filtered
        condition: The filter condition without [?( and )]

    Returns:
        True if condition matches, False otherwise
    """
    # Replace @ with empty string to get property paths
    condition = condition.strip()

    # Split by && or & to get individual checks
    and_parts = re.split(r"\s*&&\s*|\s*&\s*", condition)

    for part in and_parts:
        part = part.strip()

        # Check for comparison operators
        if "==" in part:
            left, right = part.split("==", 1)
            left = left.strip().lstrip("@").lstrip(".")
            right = right.strip().strip('"').strip("'")

            exists, value = _safe_get_nested(item, left)
            if not exists:
                return False
            if str(value) != right:
                return False

        elif "!=" in part:
            left, right = part.split("!=", 1)
            left = left.strip().lstrip("@").lstrip(".")
            right = right.strip().strip('"').strip("'")

            exists, value = _safe_get_nested(item, left)
            if not exists:
                return False
            if str(value) == right:
                return False

        elif ">=" in part:
            left, right = part.split(">=", 1)
            left = left.strip().lstrip("@").lstrip(".")
            right = right.strip()

            exists, value = _safe_get_nested(item, left)
            if not exists:
                return False
            try:
                if not (float(value) >= float(right)):
                    return False
            except (ValueError, TypeError):
                return False

        elif "<=" in part:
            left, right = part.split("<=", 1)
            left = left.strip().lstrip("@").lstrip(".")
            right = right.strip()

            exists, value = _safe_get_nested(item, left)
            if not exists:
                return False
            try:
                if not (float(value) <= float(right)):
                    return False
            except (ValueError, TypeError):
                return False

        elif ">" in part:
            left, right = part.split(">", 1)
            left = left.strip().lstrip("@").lstrip(".")
            right = right.strip()

            exists, value = _safe_get_nested(item, left)
            if not exists:
                return False
            try:
                if not (float(value) > float(right)):
                    return False
            except (ValueError, TypeError):
                return False

        elif "<" in part:
            left, right = part.split("<", 1)
            left = left.strip().lstrip("@").lstrip(".")
            right = right.strip()

            exists, value = _safe_get_nested(item, left)
            if not exists:
                return False
            try:
                if not (float(value) < float(right)):
                    return False
            except (ValueError, TypeError):
                return False

        else:
            # Just existence check
            path = part.lstrip("@").lstrip(".")
            if path:
                exists, _ = _safe_get_nested(item, path)
                if not exists:
                    return False

    return True


def extract_filter_condition(jsonpath: str) -> tuple[str | None, str, str]:
    """
    Extract filter condition from JSONPath if present.

    Args:
        jsonpath: JSONPath expression

    Returns:
        Tuple of (filter_condition, base_path_before_filter, suffix_after_filter)
        If no filter, filter_condition is None.
    """
    # Match patterns like [?(...)]
    filter_pattern = re.compile(r"\[\?\(([^)]+)\)\]")
    match = filter_pattern.search(jsonpath)

    if not match:
        return None, jsonpath, ""

    condition = match.group(1)
    # Base path is everything before the filter
    base_path = jsonpath[: match.start()]
    # Suffix is everything after the filter
    suffix = jsonpath[match.end() :]

    return condition, base_path, suffix


def has_complex_filter(jsonpath: str) -> bool:
    """
    Check if JSONPath has a complex filter with && or nested property access.

    Args:
        jsonpath: JSONPath expression

    Returns:
        True if it has complex filter that needs safe evaluation
    """
    filter_pattern = re.compile(r"\[\?\(([^)]+)\)\]")
    match = filter_pattern.search(jsonpath)

    if not match:
        return False

    condition = match.group(1)

    # Check for && or multiple property accesses
    if "&&" in condition or condition.count("@.") > 1:
        return True

    # Check for nested property access (more than one dot)
    at_props = re.findall(r"@\.[\w.]+", condition)
    for prop in at_props:
        if prop.count(".") > 1:  # @.a.b.c
            return True

    return False


__all__ = [
    "extract_filter_condition",
    "has_complex_filter",
    "_evaluate_filter_condition",
]
