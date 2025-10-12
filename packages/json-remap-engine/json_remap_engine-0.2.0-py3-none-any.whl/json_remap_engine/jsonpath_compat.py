"""
JSONPath compatibility layer to support JavaScript jsonpath-plus syntax.

This module translates JavaScript-style JSONPath expressions to be compatible
with the Python jsonpath-ng library while maintaining the same semantics.
"""

import re
from typing import Any

from jsonpath_ng.ext import parse as jsonpath_parse

from .path_utils import encode_pointer_token
from .safe_filter import (
    _evaluate_filter_condition,
    extract_filter_condition,
    has_complex_filter,
)


def _build_pointer_from_match(match: Any) -> str:
    """Build a JSON Pointer from a JSONPath match object."""
    # Use full_path to get the complete path from root
    current = match.full_path if hasattr(match, "full_path") else match.path
    pointer_parts = []

    # Collect all path elements by traversing left
    elements = []
    while current is not None:
        elements.append(current)
        if hasattr(current, "left"):
            current = current.left
        else:
            break

    # Reverse to get root-to-leaf order
    elements.reverse()

    # Extract field names and indices from each element
    for element in elements:
        if hasattr(element, "fields"):
            # Fields object - add all field names
            for field in element.fields:
                pointer_parts.append(str(field))
        elif hasattr(element, "field"):
            # Single field
            pointer_parts.append(str(element.field))
        elif hasattr(element, "index"):
            # Array index
            pointer_parts.append(str(element.index))
        elif hasattr(element, "right"):
            # Child object - process the right side
            right = element.right
            if hasattr(right, "fields"):
                for field in right.fields:
                    pointer_parts.append(str(field))
            elif hasattr(right, "field"):
                pointer_parts.append(str(right.field))
            elif hasattr(right, "index"):
                pointer_parts.append(str(right.index))

    # Encode each part properly
    encoded_parts = [encode_pointer_token(part) for part in pointer_parts]
    return "/" + "/".join(encoded_parts) if encoded_parts else ""


def _translate_logical_operators(jsonpath: str) -> str:
    """
    Translate JavaScript-style logical operators to Python equivalents.

    JavaScript jsonpath-plus uses: && and ||
    Python jsonpath-ng uses: & and |

    Args:
        jsonpath: JSONPath expression with potential JS-style operators

    Returns:
        JSONPath expression with Python-style operators
    """
    # Replace && with & (but not already-single &)
    # Use negative lookbehind and lookahead to avoid replacing single &
    result = re.sub(r"&&", "&", jsonpath)

    # Replace || with |
    result = re.sub(r"\|\|", "|", result)

    return result


def _translate_comma_indices(jsonpath: str) -> list[str]:
    """
    Translate comma-separated array indices to multiple JSONPath expressions.

    JavaScript jsonpath-plus supports: $.arr[1,3,5]
    Python jsonpath-ng doesn't, so we split into: [$.arr[1], $.arr[3], $.arr[5]]

    Args:
        jsonpath: JSONPath expression that may contain comma-separated indices

    Returns:
        List of JSONPath expressions (single item if no translation needed)
    """
    # Pattern to match array index lists like [1,3,5] or [1, 3, 5]
    comma_pattern = re.compile(r"\[(\d+(?:\s*,\s*\d+)+)\]")

    match = comma_pattern.search(jsonpath)
    if not match:
        # No comma-separated indices found
        return [jsonpath]

    # Extract the comma-separated indices
    indices_str = match.group(1)
    indices = [idx.strip() for idx in indices_str.split(",")]

    # Generate separate JSONPath expressions for each index
    base_before = jsonpath[: match.start()]
    base_after = jsonpath[match.end() :]

    result = []
    for idx in indices:
        translated = f"{base_before}[{idx}]{base_after}"
        result.append(translated)

    return result


def evaluate_jsonpath(
    jsonpath: str, document: Any, result_type: str = "pointer"
) -> list[Any]:
    """
    Evaluate a JSONPath expression with JS compatibility.

    Handles JavaScript-style syntax like comma-separated indices and returns
    results in the requested format.

    Args:
        jsonpath: JSONPath expression (supports JS syntax)
        document: The document to query
        result_type: "pointer" or "value"

    Returns:
        List of results (pointers or values)
    """
    # Check if this has a complex filter with && that needs safe evaluation
    if has_complex_filter(jsonpath):
        return _evaluate_complex_filter(jsonpath, document, result_type)

    # First, translate logical operators (&&, ||) to Python equivalents (&, |)
    translated_jsonpath = _translate_logical_operators(jsonpath)

    # Then translate comma-separated indices to multiple expressions
    expressions = _translate_comma_indices(translated_jsonpath)

    all_results = []
    for expr_str in expressions:
        expr = jsonpath_parse(expr_str)
        matches = expr.find(document)

        if result_type == "pointer":
            # Build pointers from matches
            for match in matches:
                pointer = _build_pointer_from_match(match)
                all_results.append(pointer)
        else:  # value
            for match in matches:
                all_results.append(match.value)

    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for item in all_results:
        # For pointers (strings), we can use them directly
        # For values, we need to be careful with unhashable types
        try:
            key = (
                item
                if isinstance(item, (str, int, float, bool, type(None)))
                else id(item)
            )
            if key not in seen:
                seen.add(key)
                unique_results.append(item)
        except TypeError:
            # Unhashable type, include it anyway
            unique_results.append(item)

    return unique_results


def _evaluate_complex_filter(
    jsonpath: str, document: Any, result_type: str = "pointer"
) -> list[Any]:
    """
    Evaluate a JSONPath with complex filter using safe Python evaluation.

    This handles expressions like:
    $.items[?(@.a && @.a.b && @.a.b.c == 'value')].property

    Args:
        jsonpath: JSONPath with complex filter
        document: The document to query
        result_type: "pointer" or "value"

    Returns:
        List of results
    """
    # Extract the filter condition, base path, and suffix
    filter_condition, base_path, suffix = extract_filter_condition(jsonpath)

    if not filter_condition:
        # No filter, use normal evaluation
        return evaluate_jsonpath(jsonpath, document, result_type)

    # Evaluate the base path without filter to get candidates
    try:
        base_expr = jsonpath_parse(base_path)
        base_matches = base_expr.find(document)
    except Exception:
        return []

    results = []

    for base_match in base_matches:
        # Get the array/collection
        collection = base_match.value
        if not isinstance(collection, list):
            continue

        # Manually filter items using safe evaluation
        for idx, item in enumerate(collection):
            if _evaluate_filter_condition(item, filter_condition):
                # This item matches the filter
                if suffix:
                    # Navigate to the suffix property
                    suffix_path = suffix.lstrip(".")
                    current = item
                    for part in suffix_path.split("."):
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            current = None
                            break

                    if current is not None:
                        if result_type == "pointer":
                            # Build pointer: base_path/index/suffix
                            base_pointer = _build_pointer_from_match(base_match)
                            full_pointer = f"{base_pointer}/{idx}"
                            if suffix_path:
                                suffix_encoded = "/".join(
                                    encode_pointer_token(p)
                                    for p in suffix_path.split(".")
                                )
                                full_pointer = f"{full_pointer}/{suffix_encoded}"
                            results.append(full_pointer)
                        else:
                            results.append(current)
                else:
                    # No suffix, return the item itself
                    if result_type == "pointer":
                        base_pointer = _build_pointer_from_match(base_match)
                        full_pointer = f"{base_pointer}/{idx}"
                        results.append(full_pointer)
                    else:
                        results.append(item)

    return results


__all__ = [
    "evaluate_jsonpath",
]
