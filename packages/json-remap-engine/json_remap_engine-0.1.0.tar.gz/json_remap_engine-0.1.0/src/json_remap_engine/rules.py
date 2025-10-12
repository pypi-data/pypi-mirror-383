"""Rule creation utilities for the JSON remapping engine."""

import secrets
from typing import Literal, TypedDict


class _RuleRequired(TypedDict):
    """Required fields for all rule types."""

    id: str
    matcher: str
    op: str  # Will be narrowed in subclasses


class _RuleOptional(TypedDict, total=False):
    """Optional fields for all rule types."""

    allowEmptyMatcher: bool
    allowEmptyValue: bool
    disabled: bool


class _RuleBase(_RuleRequired, _RuleOptional):
    """Base fields combining required and optional."""

    pass


class RemoveRule(_RuleBase):
    """A rule that removes matched values."""

    op: Literal["remove"]  # type: ignore[misc]


class _ReplaceRuleRequired(_RuleBase):
    """Replace rule with required value field."""

    value: object


class _ReplaceRuleOptional(TypedDict, total=False):
    """Replace rule optional fields."""

    valueMode: Literal["auto", "literal"]


class ReplaceRule(_ReplaceRuleRequired, _ReplaceRuleOptional):
    """A rule that replaces matched values."""

    op: Literal["replace"]  # type: ignore[misc]


class _MoveRuleRequired(_RuleBase):
    """Move rule with required target field."""

    target: str


class _MoveRuleOptional(TypedDict, total=False):
    """Move rule optional fields."""

    targetMode: Literal["auto", "pointer", "jsonpath"]


class MoveRule(_MoveRuleRequired, _MoveRuleOptional):
    """A rule that moves matched values to a target location."""

    op: Literal["move"]  # type: ignore[misc]


Rule = RemoveRule | ReplaceRule | MoveRule


def generate_rule_id() -> str:
    """
    Generate a unique rule identifier using cryptographically secure randomness.

    Returns:
        A rule ID string in the format "r-xxxxxxxx"
    """
    random_bytes = secrets.token_bytes(4)
    hex_string = random_bytes.hex()
    return f"r-{hex_string}"


def create_remove_rule(
    matcher: str,
    *,
    id: str | None = None,
    allow_empty_matcher: bool = False,
    disabled: bool = False,
) -> RemoveRule:
    """
    Create a JSON removal rule for a JSONPath matcher.

    Args:
        matcher: JSONPath expression to match values for removal
        id: Optional rule identifier (auto-generated if not provided)
        allow_empty_matcher: Allow matcher to resolve to zero paths without warning
        disabled: Start the rule disabled (returned in diagnostics but not executed)

    Returns:
        A RemoveRule dictionary
    """
    return RemoveRule(
        id=id or generate_rule_id(),
        matcher=matcher,
        op="remove",
        allowEmptyMatcher=allow_empty_matcher,
        allowEmptyValue=False,
        disabled=disabled,
    )


def create_replace_rule(
    matcher: str,
    value: object,
    *,
    id: str | None = None,
    allow_empty_matcher: bool = False,
    allow_empty_value: bool = False,
    disabled: bool = False,
    value_mode: Literal["auto", "literal"] = "auto",
) -> ReplaceRule:
    """
    Create a replacement rule that optionally reuses another value in the document via JSONPath.

    Args:
        matcher: JSONPath expression to match values for replacement
        value: The value to replace with (can be a JSONPath expression if value_mode is "auto")
        id: Optional rule identifier (auto-generated if not provided)
        allow_empty_matcher: Allow matcher to resolve to zero paths without warning
        allow_empty_value: Allow value to be empty/undefined without raising warnings
        disabled: Start the rule disabled (returned in diagnostics but not executed)
        value_mode: When "literal", treat value as-is even if it starts with "$"

    Returns:
        A ReplaceRule dictionary
    """
    return ReplaceRule(
        id=id or generate_rule_id(),
        matcher=matcher,
        op="replace",
        value=value,
        allowEmptyMatcher=allow_empty_matcher,
        allowEmptyValue=allow_empty_value,
        disabled=disabled,
        valueMode=value_mode,
    )


def create_move_rule(
    matcher: str,
    target: str,
    *,
    id: str | None = None,
    allow_empty_matcher: bool = False,
    allow_empty_value: bool = False,
    disabled: bool = False,
    target_mode: Literal["auto", "pointer", "jsonpath"] = "auto",
) -> MoveRule:
    """
    Create a move rule that copies the matched value to a target location and removes the source.

    Args:
        matcher: JSONPath expression to match values to move
        target: Target location (JSON Pointer or JSONPath)
        id: Optional rule identifier (auto-generated if not provided)
        allow_empty_matcher: Allow matcher to resolve to zero paths without warning
        allow_empty_value: Allow target to resolve to zero paths without raising warnings
        disabled: Start the rule disabled (returned in diagnostics but not executed)
        target_mode: Force interpretation of target ("auto" auto-detects Pointer vs JSONPath)

    Returns:
        A MoveRule dictionary
    """
    return MoveRule(
        id=id or generate_rule_id(),
        matcher=matcher,
        op="move",
        target=target,
        allowEmptyMatcher=allow_empty_matcher,
        allowEmptyValue=allow_empty_value,
        disabled=disabled,
        targetMode=target_mode,
    )


__all__ = [
    "Rule",
    "RemoveRule",
    "ReplaceRule",
    "MoveRule",
    "create_remove_rule",
    "create_replace_rule",
    "create_move_rule",
    "generate_rule_id",
]
