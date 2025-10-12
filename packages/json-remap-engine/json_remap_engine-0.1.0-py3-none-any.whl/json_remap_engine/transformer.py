"""Core transformation engine for applying JSON remapping rules."""

import copy
import json
from collections.abc import Sequence
from typing import Any, Literal, TypedDict


from .jsonpath_compat import evaluate_jsonpath
from .path_utils import (
    decode_pointer_token,
    encode_pointer_token,
    simple_json_path_to_pointer,
)
from .rules import MoveRule, RemoveRule, ReplaceRule, Rule


Op = Literal["remove", "replace", "move"]


class JsonPatchRemove(TypedDict):
    """JSON Patch remove operation."""

    op: Literal["remove"]
    path: str


class JsonPatchReplace(TypedDict):
    """JSON Patch replace operation."""

    op: Literal["replace"]
    path: str
    value: Any


class JsonPatchMove(TypedDict):
    """JSON Patch move operation."""

    op: Literal["move"]
    path: str
    from_: str  # Note: Python dict key can't be 'from', so we use 'from_' internally


# For external API, we'll use 'from' as the key
JsonPatchOperation = JsonPatchRemove | JsonPatchReplace | JsonPatchMove


class RuleOperationDiagnostic(TypedDict):
    """Diagnostic information for a single operation within a rule."""

    matchIndex: int
    pointer: str
    op: Op
    summary: dict[str, Any]  # The JSON Patch operation
    status: Literal["applied", "skipped"]
    message: str | None


class RuleDiagnostic(TypedDict):
    """Diagnostic information for a rule execution."""

    ruleId: str
    matcher: str
    op: Op
    matchCount: int
    operations: list[RuleOperationDiagnostic]
    errors: list[str]
    warnings: list[str]


class TransformerResult(TypedDict):
    """Result of running the transformer."""

    ok: bool
    document: Any
    operations: list[dict[str, Any]]  # JSON Patch operations
    diagnostics: list[RuleDiagnostic]
    errors: list[str]
    warnings: list[str]


# Unsafe keys that should never be used in JSON Pointer operations
UNSAFE_KEYS = {"__proto__", "prototype", "constructor"}


def _clone_value(value: Any) -> Any:
    """Deep clone a value."""
    return copy.deepcopy(value)


def _normalize_pointer(pointer: str) -> str:
    """Normalize a JSON Pointer to ensure it starts with '/'."""
    if pointer == "":
        return ""
    if not pointer.startswith("/"):
        return "/" + pointer.lstrip("/")
    return pointer


def _split_pointer(pointer: str) -> list[str]:
    """Split a JSON Pointer into decoded tokens."""
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ValueError(f"Invalid JSON pointer: {pointer}")
    parts = pointer[1:].split("/")
    return [decode_pointer_token(p) for p in parts]


def _ensure_pointer_safety(pointer: str) -> None:
    """Ensure a pointer doesn't contain unsafe segments."""
    if pointer == "":
        return
    tokens = _split_pointer(pointer)
    for token in tokens:
        if token in UNSAFE_KEYS:
            raise ValueError(f"Unsafe pointer segment '{token}' is not allowed")


def _join_pointer(tokens: list[str]) -> str:
    """Join tokens into a JSON Pointer."""
    if not tokens:
        return ""
    return "/" + "/".join(encode_pointer_token(t) for t in tokens)


def _get_value_at_pointer(document: Any, pointer: str) -> Any:
    """Get value at a JSON Pointer location."""
    tokens = _split_pointer(pointer)
    current = document

    for token in tokens:
        if isinstance(current, list):
            if token == "-":
                raise ValueError("Cannot resolve '-' within JSON pointer")
            try:
                index = int(token)
                if index < 0 or index >= len(current):
                    raise ValueError(f"Array index {token} is out of bounds")
                current = current[index]
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid array index: {token}")
                raise
        elif isinstance(current, dict):
            if token not in current:
                raise ValueError(f"Property '{token}' does not exist")
            current = current[token]
        else:
            raise ValueError(
                f"Cannot traverse pointer segment '{token}' on non-container value"
            )

    return current


def _get_parent_context(document: Any, pointer: str) -> tuple[Any, str | None]:
    """Get the parent container and key for a pointer."""
    tokens = _split_pointer(pointer)
    if not tokens:
        return None, None

    parent_tokens = tokens[:-1]
    key = tokens[-1]
    parent = (
        document
        if not parent_tokens
        else _get_value_at_pointer(document, _join_pointer(parent_tokens))
    )

    return parent, key


def _remove_at_pointer(document: Any, pointer: str) -> Any:
    """Remove value at a JSON Pointer location (mutates document)."""
    parent, key = _get_parent_context(document, pointer)

    if parent is None or key is None:
        raise ValueError("Cannot remove the root document")

    if isinstance(parent, list):
        if key == "-":
            raise ValueError("'-' is not allowed when removing array elements")
        try:
            index = int(key)
            if index < 0 or index >= len(parent):
                raise ValueError(f"Array index {key} is out of bounds")
            parent.pop(index)
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Invalid array index: {key}")
            raise
    elif isinstance(parent, dict):
        if key not in parent:
            raise ValueError(f"Property '{key}' does not exist")
        del parent[key]
    else:
        raise ValueError("Cannot remove from non-container value")

    return document


def _replace_at_pointer(document: Any, pointer: str, value: Any) -> Any:
    """Replace value at a JSON Pointer location (mutates document)."""
    parent, key = _get_parent_context(document, pointer)

    if parent is None or key is None:
        return value

    if isinstance(parent, list):
        if key == "-":
            raise ValueError("'-' is not allowed when replacing array elements")
        try:
            index = int(key)
            if index < 0 or index >= len(parent):
                raise ValueError(f"Array index {key} is out of bounds")
            parent[index] = value
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Invalid array index: {key}")
            raise
    elif isinstance(parent, dict):
        if key in UNSAFE_KEYS:
            raise ValueError(f"Unsafe pointer segment '{key}' is not allowed")
        if key not in parent:
            raise ValueError(f"Property '{key}' does not exist")
        parent[key] = value
    else:
        raise ValueError("Cannot replace within non-container value")

    return document


def _add_at_pointer(document: Any, pointer: str, value: Any) -> Any:
    """Add value at a JSON Pointer location (mutates document)."""
    parent, key = _get_parent_context(document, pointer)

    if parent is None or key is None:
        return value

    if isinstance(parent, list):
        if key == "-":
            parent.append(value)
        else:
            try:
                index = int(key)
                if index < 0 or index > len(parent):
                    raise ValueError(f"Array index {key} is out of bounds")
                parent.insert(index, value)
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid array index: {key}")
                raise
    elif isinstance(parent, dict):
        if key in UNSAFE_KEYS:
            raise ValueError(f"Unsafe pointer segment '{key}' is not allowed")
        parent[key] = value
    else:
        raise ValueError("Cannot add within non-container value")

    return document


def _reorder_remove_operations(
    operations: list[RuleOperationDiagnostic],
) -> list[RuleOperationDiagnostic]:
    """Reorder remove operations to process higher indices first."""
    result = operations.copy()
    groups: dict[str, list[RuleOperationDiagnostic]] = {}

    for operation in operations:
        if operation["summary"].get("op") != "remove":
            continue

        tokens = _split_pointer(operation["summary"]["path"])
        parent_pointer = _join_pointer(tokens[:-1])

        if parent_pointer not in groups:
            groups[parent_pointer] = []
        groups[parent_pointer].append(operation)

    for group in groups.values():
        # Sort by descending index - higher indices first
        def get_index(op: RuleOperationDiagnostic) -> int:
            tokens = _split_pointer(op["summary"]["path"])
            try:
                return int(tokens[-1])
            except (ValueError, IndexError):
                return -1

        sorted_group = sorted(group, key=get_index, reverse=True)
        positions = sorted([result.index(op) for op in group if op in result])

        for position, operation in zip(positions, sorted_group):
            result[position] = operation

    return result


def _evaluate_pointer_matches(document: Any, matcher: str) -> list[str]:
    """Evaluate a JSONPath matcher and return matching JSON Pointers."""
    normalized = matcher.strip()
    if not normalized:
        raise ValueError("Matcher JSONPath expression is empty")

    try:
        # Use compatibility layer to handle JS-style syntax
        pointers = evaluate_jsonpath(normalized, document, result_type="pointer")

        # Normalize and return
        normalized_pointers = [_normalize_pointer(p) for p in pointers]
        return normalized_pointers

    except Exception as e:
        error_msg = str(e)
        if (
            "Cannot read properties of undefined" in error_msg
            or "NoneType" in error_msg
            or "NoneType" in error_msg
        ):
            raise ValueError(
                f"{error_msg}. Ensure optional segments exist before comparing. "
                "JSONPath filters do not support optional chaining syntax (?.)."
            )
        raise ValueError(error_msg)


def _resolve_value_expression(document: Any, rule: ReplaceRule) -> Any:
    """Resolve the replacement value, potentially from a JSONPath expression."""
    value_mode = rule.get("valueMode", "auto")
    value = rule.get("value")

    if value_mode == "literal":
        return _clone_value(value)

    if isinstance(value, str) and value.strip().startswith("$"):
        try:
            # Use compatibility layer
            resolved = evaluate_jsonpath(value.strip(), document, result_type="value")

            if len(resolved) != 1:
                raise ValueError(
                    f"Expected exactly one value for JSONPath '{value}', received {len(resolved)}"
                )
            return resolved[0]
        except Exception as e:
            raise ValueError(str(e))

    return _clone_value(value)


def _resolve_target_pointer(document: Any, rule: MoveRule) -> str | None:
    """Resolve the target pointer for a move operation."""
    target = rule.get("target", "")
    target_mode = rule.get("targetMode", "auto")

    if not target.strip():
        raise ValueError("Move operations require a target pointer or JSONPath")

    trimmed = target.strip()

    if target_mode == "pointer":
        pointer = _normalize_pointer(trimmed)
        _ensure_pointer_safety(pointer)
        return pointer

    if target_mode == "jsonpath":
        try:
            # Use compatibility layer
            values = evaluate_jsonpath(trimmed, document, result_type="pointer")

            if len(values) == 1:
                pointer = _normalize_pointer(values[0])
                _ensure_pointer_safety(pointer)
                return pointer

            if len(values) == 0:
                if rule.get("allowEmptyValue"):
                    return None
                fallback_pointer = simple_json_path_to_pointer(trimmed)
                if fallback_pointer is not None:
                    pointer = _normalize_pointer(fallback_pointer)
                    _ensure_pointer_safety(pointer)
                    return pointer

            raise ValueError(
                f"Expected exactly one target pointer for JSONPath '{target}', received {len(values)}"
            )
        except Exception as e:
            raise ValueError(str(e))

    # Auto mode
    if trimmed.startswith("/"):
        pointer = _normalize_pointer(trimmed)
        _ensure_pointer_safety(pointer)
        return pointer

    if trimmed.startswith("$"):
        try:
            # Use compatibility layer
            values = evaluate_jsonpath(trimmed, document, result_type="pointer")

            if len(values) != 1:
                if len(values) == 0:
                    if rule.get("allowEmptyValue"):
                        return None
                    fallback_pointer = simple_json_path_to_pointer(trimmed)
                    if fallback_pointer:
                        pointer = _normalize_pointer(fallback_pointer)
                        _ensure_pointer_safety(pointer)
                        return pointer

                raise ValueError(
                    f"Expected exactly one target pointer for JSONPath '{target}', received {len(values)}"
                )

            pointer = _normalize_pointer(values[0])
            _ensure_pointer_safety(pointer)
            return pointer
        except Exception as e:
            raise ValueError(str(e))

    raise ValueError("Target must start with '/' for JSONPointer or '$' for JSONPath")


def _apply_operation(document: Any, operation: dict[str, Any]) -> Any:
    """Apply a JSON Patch operation to the document."""
    op = operation["op"]

    if op == "remove":
        return _remove_at_pointer(document, operation["path"])
    elif op == "replace":
        return _replace_at_pointer(document, operation["path"], operation["value"])
    elif op == "move":
        value = _clone_value(_get_value_at_pointer(document, operation["from"]))
        intermediate = _remove_at_pointer(document, operation["from"])
        intermediate = _add_at_pointer(intermediate, operation["path"], value)
        return intermediate

    return document


def run_transformer(input_data: Any, rules: Sequence[Rule]) -> TransformerResult:
    """
    Run the JSON remapping transformer with the given rules.

    Args:
        input_data: The input document to transform
        rules: List of transformation rules to apply

    Returns:
        TransformerResult with the transformed document and diagnostics
    """
    diagnostics: list[RuleDiagnostic] = []
    errors: list[str] = []
    warnings: list[str] = []
    applied_operations: list[dict[str, Any]] = []

    working_document = _clone_value(input_data)

    for rule_index, rule in enumerate(rules):
        if rule.get("disabled"):
            diagnostics.append(
                RuleDiagnostic(
                    ruleId=rule["id"],
                    matcher=rule["matcher"],
                    op=rule["op"],
                    matchCount=0,
                    operations=[],
                    errors=[],
                    warnings=[],
                )
            )
            continue

        rule_errors: list[str] = []
        rule_warnings: list[str] = []
        matches: list[str] = []
        suppress_no_op_warning = False

        trimmed_matcher = rule.get("matcher", "").strip()
        if not trimmed_matcher:
            matches = []
            suppress_no_op_warning = True
        else:
            try:
                matches = _evaluate_pointer_matches(working_document, rule["matcher"])
            except Exception as e:
                message = str(e)
                rule_errors.append(
                    f"Rule {rule_index + 1} ({rule['op']}) matcher error: {message}"
                )

            if len(matches) == 0 and rule.get("allowEmptyMatcher"):
                suppress_no_op_warning = True

        skip_due_to_empty_value = False
        if rule["op"] == "replace":
            value_is_empty = rule.get("value") is None
            if value_is_empty:
                skip_due_to_empty_value = True
                if rule.get("allowEmptyValue"):
                    suppress_no_op_warning = True
                else:
                    rule_errors.append(
                        f"Rule {rule_index + 1} replace value error: replacement value is required"
                    )

        if skip_due_to_empty_value:
            matches = []

        operations: list[RuleOperationDiagnostic] = []

        for match_index, pointer in enumerate(matches):
            if rule["op"] == "remove":
                operations.append(
                    RuleOperationDiagnostic(
                        matchIndex=match_index,
                        pointer=pointer,
                        op="remove",
                        summary={"op": "remove", "path": pointer},
                        status="skipped",
                        message=None,
                    )
                )
            elif rule["op"] == "replace":
                try:
                    resolved_value = _resolve_value_expression(working_document, rule)  # type: ignore
                    if resolved_value is None and rule.get("allowEmptyValue"):
                        suppress_no_op_warning = True
                        continue

                    operations.append(
                        RuleOperationDiagnostic(
                            matchIndex=match_index,
                            pointer=pointer,
                            op="replace",
                            summary={
                                "op": "replace",
                                "path": pointer,
                                "value": resolved_value,
                            },
                            status="skipped",
                            message=None,
                        )
                    )
                except Exception as e:
                    message = str(e)
                    if (
                        rule.get("allowEmptyValue")
                        and "Expected exactly one value" in message
                    ):
                        suppress_no_op_warning = True
                        continue
                    rule_errors.append(
                        f"Rule {rule_index + 1} replace value error: {message}"
                    )
            elif rule["op"] == "move":
                try:
                    target = _resolve_target_pointer(working_document, rule)  # type: ignore
                    if target is None:
                        suppress_no_op_warning = True
                        continue

                    operations.append(
                        RuleOperationDiagnostic(
                            matchIndex=match_index,
                            pointer=pointer,
                            op="move",
                            summary={"op": "move", "from": pointer, "path": target},
                            status="skipped",
                            message=None,
                        )
                    )
                except Exception as e:
                    message = str(e)
                    rule_errors.append(
                        f"Rule {rule_index + 1} move target error: {message}"
                    )

        if (
            not suppress_no_op_warning
            and len(operations) == 0
            and len(matches) == 0
            and len(rule_errors) == 0
        ):
            rule_warnings.append("No matches produced patch operations")

        ordered_operations = _reorder_remove_operations(operations)
        ordered_operations = [op.copy() for op in ordered_operations]

        for operation in ordered_operations:
            try:
                working_document = _apply_operation(
                    working_document, operation["summary"]
                )
                operation["status"] = "applied"
                applied_operations.append(operation["summary"])
            except Exception as e:
                message = str(e)
                operation["status"] = "skipped"
                operation["message"] = message
                op_type = operation["op"].capitalize()
                rule_errors.append(
                    f"{op_type} {operation['pointer']} failed: {message}"
                )

        diagnostics.append(
            RuleDiagnostic(
                ruleId=rule["id"],
                matcher=rule["matcher"],
                op=rule["op"],
                matchCount=len(matches),
                operations=ordered_operations,
                errors=rule_errors,
                warnings=rule_warnings,
            )
        )

        errors.extend(rule_errors)
        warnings.extend(rule_warnings)

    return TransformerResult(
        ok=len(errors) == 0,
        document=working_document,
        operations=applied_operations,
        diagnostics=diagnostics,
        errors=errors,
        warnings=warnings,
    )


def format_patch(operations: list[dict[str, Any]], pretty: bool = True) -> str:
    """
    Format JSON Patch operations as a JSON string.

    Args:
        operations: List of JSON Patch operations
        pretty: Whether to pretty-print the JSON

    Returns:
        JSON string representation of the operations
    """
    if pretty:
        return json.dumps(operations, indent=2)
    # Use compact separators to match JavaScript JSON.stringify output
    return json.dumps(operations, separators=(",", ":"))


__all__ = [
    "run_transformer",
    "format_patch",
    "Rule",
    "RemoveRule",
    "ReplaceRule",
    "MoveRule",
    "RuleDiagnostic",
    "RuleOperationDiagnostic",
    "TransformerResult",
    "JsonPatchOperation",
    "Op",
]
