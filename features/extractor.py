"""Orchestrates all feature extractors into a unified feature vector."""

from typing import Dict, List

from parser.base_parser import FunctionInfo
from .complexity import cyclomatic_complexity
from .structure import (
    lines_of_code,
    max_nesting_depth,
    loop_count,
    function_call_count,
    function_length,
)
from .patterns import (
    variable_reuse_count,
    exception_handling_count,
    code_duplication_score,
    import_count,
)

# Canonical order of features — must match ML model training
FEATURE_NAMES = [
    "lines_of_code",
    "function_length",
    "nesting_depth",
    "cyclomatic_complexity",
    "loop_count",
    "function_call_count",
    "variable_reuse",
    "exception_handling",
    "code_duplication",
    "import_count",
]


def extract_features(func: FunctionInfo, imports: list = None) -> Dict[str, float]:
    """Extract all metrics for a single function."""
    code = func.code
    lang = func.language

    return {
        "lines_of_code": lines_of_code(code),
        "function_length": function_length(code),
        "nesting_depth": max_nesting_depth(code, lang),
        "cyclomatic_complexity": cyclomatic_complexity(code, lang),
        "loop_count": loop_count(code),
        "function_call_count": function_call_count(code),
        "variable_reuse": variable_reuse_count(code, lang),
        "exception_handling": exception_handling_count(code, lang),
        "code_duplication": code_duplication_score(code),
        "import_count": import_count(imports or []),
    }


def features_to_vector(features: Dict[str, float]) -> List[float]:
    """Convert feature dict to ordered list matching FEATURE_NAMES."""
    return [features[name] for name in FEATURE_NAMES]
