"""
json-remap-engine: JSONPath-driven remapping engine that produces JSON Patch operations.

This package provides a rules-based transformation engine for JSON documents,
using JSONPath expressions to match elements and JSON Patch operations to describe changes.
"""

from .path_utils import (
    analysis_path_to_json_path,
    analysis_path_to_pointer,
    decode_pointer_token,
    encode_pointer_token,
    get_value_at_pointer_safe,
    pointer_exists,
    pointer_to_analysis_path,
    simple_json_path_to_pointer,
)
from .rules import (
    MoveRule,
    RemoveRule,
    ReplaceRule,
    Rule,
    create_move_rule,
    create_remove_rule,
    create_replace_rule,
    generate_rule_id,
)
from .transformer import (
    JsonPatchOperation,
    Op,
    RuleDiagnostic,
    RuleOperationDiagnostic,
    TransformerResult,
    format_patch,
    run_transformer,
)

__version__ = "0.1.0"

__all__ = [
    # Transformer
    "run_transformer",
    "format_patch",
    # Types - Transformer
    "Rule",
    "RemoveRule",
    "ReplaceRule",
    "MoveRule",
    "RuleDiagnostic",
    "RuleOperationDiagnostic",
    "TransformerResult",
    "JsonPatchOperation",
    "Op",
    # Rules
    "create_remove_rule",
    "create_replace_rule",
    "create_move_rule",
    "generate_rule_id",
    # Path utilities
    "analysis_path_to_json_path",
    "analysis_path_to_pointer",
    "pointer_to_analysis_path",
    "pointer_exists",
    "get_value_at_pointer_safe",
    "simple_json_path_to_pointer",
    "decode_pointer_token",
    "encode_pointer_token",
]
