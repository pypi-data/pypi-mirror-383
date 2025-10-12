"""
JSONPath compatibility layer to support JavaScript jsonpath-plus syntax.

This module translates JavaScript-style JSONPath expressions to be compatible
with the Python jsonpath-ng library while maintaining the same semantics.
"""

import re
from typing import Any

from jsonpath_ng.ext import parse as jsonpath_parse

from .path_utils import encode_pointer_token


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
    # Translate comma-separated indices to multiple expressions
    expressions = _translate_comma_indices(jsonpath)

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


__all__ = [
    "evaluate_jsonpath",
]
