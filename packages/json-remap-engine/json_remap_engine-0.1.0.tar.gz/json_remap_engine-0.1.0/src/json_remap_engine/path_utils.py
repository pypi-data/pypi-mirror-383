"""Utilities for converting between JSON Pointer, JSONPath, and analysis path formats."""

import re
from typing import Any


NORMAL_KEY_REGEX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def decode_pointer_token(token: str) -> str:
    """Decode a JSON Pointer token by unescaping special characters."""
    return token.replace("~1", "/").replace("~0", "~")


def encode_pointer_token(token: str) -> str:
    """Encode a JSON Pointer token by escaping special characters."""
    return token.replace("~", "~0").replace("/", "~1")


def _unescape_analysis_key(key: str) -> str:
    """Unescape quotes in analysis path keys."""
    return key.replace('\\"', '"')


def _escape_analysis_key(key: str) -> str:
    """Escape quotes in analysis path keys."""
    return key.replace('"', '\\"')


def analysis_path_to_json_path(path: str) -> str:
    """
    Convert an internal "analysis path" (root.foo.bar[0]) to a JSONPath expression.

    Args:
        path: Analysis path string (e.g., "root.foo.bar[0]")

    Returns:
        JSONPath expression (e.g., "$.foo.bar[0]")
    """
    if not path or path == "root":
        return "$"
    return path.replace("root", "$", 1)


def analysis_path_to_pointer(path: str) -> str:
    """
    Convert an internal "analysis path" (root.foo.bar[0]) to a JSON Pointer string.

    Args:
        path: Analysis path string (e.g., "root.foo.bar[0]")

    Returns:
        JSON Pointer (e.g., "/foo/bar/0")
    """
    if not path or path == "root":
        return ""

    tail = path.replace("root", "", 1)
    if not tail:
        return ""

    tokens: list[str] = []
    # Match: .identifier, ["quoted"], or [index]
    segment_pattern = re.compile(
        r'(?:\.([A-Za-z_][A-Za-z0-9_]*))|(?:\["((?:\\"|[^"])+)"\])|(?:\[(\d+)\])'
    )

    for match in segment_pattern.finditer(tail):
        dotted, quoted, index_token = match.groups()
        if dotted is not None:
            tokens.append(dotted)
        elif quoted is not None:
            tokens.append(_unescape_analysis_key(quoted))
        elif index_token is not None:
            tokens.append(index_token)

    if not tokens:
        return ""
    return "/" + "/".join(encode_pointer_token(t) for t in tokens)


def pointer_to_analysis_path(pointer: str) -> str:
    """
    Convert a JSON Pointer to the internal analysis path format.

    Args:
        pointer: JSON Pointer (e.g., "/foo/bar/0")

    Returns:
        Analysis path (e.g., "root.foo.bar[0]")
    """
    if not pointer or pointer == "" or pointer == "/":
        return "root"

    tokens = [decode_pointer_token(t) for t in pointer.split("/")[1:]]

    path = "root"
    for token in tokens:
        if re.match(r"^\d+$", token):
            path += f"[{token}]"
        elif NORMAL_KEY_REGEX.match(token):
            path += f".{token}"
        else:
            path += f'["{_escape_analysis_key(token)}"]'

    return path


def pointer_exists(document: Any, pointer: str) -> bool:
    """
    Return True when a JSON Pointer exists inside the provided document.

    Args:
        document: The document to check
        pointer: JSON Pointer path

    Returns:
        True if the pointer exists in the document
    """
    if pointer == "" or pointer == "/":
        return document is not None

    tokens = [decode_pointer_token(t) for t in pointer.split("/")[1:]]

    current = document
    for token in tokens:
        if isinstance(current, list):
            try:
                index = int(token)
                if index < 0 or index >= len(current):
                    return False
                current = current[index]
            except (ValueError, IndexError):
                return False
        elif isinstance(current, dict):
            if token not in current:
                return False
            current = current[token]
        else:
            return False

    return True


def get_value_at_pointer_safe(document: Any, pointer: str) -> Any:
    """
    Safely retrieve a value at the JSON Pointer location.

    Args:
        document: The document to traverse
        pointer: JSON Pointer path

    Returns:
        The value at the pointer location, or None if not found
    """
    if pointer == "" or pointer == "/":
        return document

    tokens = [decode_pointer_token(t) for t in pointer.split("/")[1:]]

    current = document
    for token in tokens:
        if isinstance(current, list):
            try:
                index = int(token)
                if index < 0 or index >= len(current):
                    return None
                current = current[index]
            except (ValueError, IndexError):
                return None
        elif isinstance(current, dict):
            if token not in current:
                return None
            current = current[token]
        else:
            return None

    return current


def simple_json_path_to_pointer(expression: str) -> str | None:
    """
    Convert a "simple" JSONPath expression to an equivalent JSON Pointer.

    Limited to property access and numeric indices. Returns None for unsupported syntax.

    Args:
        expression: JSONPath expression (e.g., "$.foo.bar[0]")

    Returns:
        JSON Pointer or None if conversion is not possible
    """
    trimmed = expression.strip()
    if not trimmed.startswith("$"):
        return None

    remainder = trimmed[1:]
    if not remainder:
        return ""

    tokens: list[str] = []
    # Match: .identifier, ['name'] or ["name"], or [index]
    pattern = re.compile(
        r"(?:\.([A-Za-z_][A-Za-z0-9_]*))|(?:\[['\"]([^'\"\\]+)['\"]\])|(?:\[(\d+)\])"
    )
    last_index = 0

    for match in pattern.finditer(remainder):
        if match.start() != last_index:
            return None

        dotted_name, quoted_name, index_token = match.groups()
        if dotted_name is not None:
            tokens.append(dotted_name)
        elif quoted_name is not None:
            tokens.append(quoted_name)
        elif index_token is not None:
            tokens.append(index_token)

        last_index = match.end()

    if last_index != len(remainder):
        return None

    if not tokens:
        return ""
    return "/" + "/".join(encode_pointer_token(t) for t in tokens)


__all__ = [
    "analysis_path_to_json_path",
    "analysis_path_to_pointer",
    "pointer_to_analysis_path",
    "pointer_exists",
    "get_value_at_pointer_safe",
    "simple_json_path_to_pointer",
    "decode_pointer_token",
    "encode_pointer_token",
]
