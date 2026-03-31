"""Cyclomatic complexity calculator for source code."""

import re


def cyclomatic_complexity(code: str, language: str = "python") -> int:
    """Calculate McCabe cyclomatic complexity from source code text.

    Counts decision points: if, elif, else, for, while, and, or,
    except/catch, case, ternary operator, assert.
    """
    # Strip comments (simplified)
    if language in ("c_cpp", "java"):
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    elif language == "python":
        code = re.sub(r'#.*', '', code)

    complexity = 1  # Base path

    # Common decision keywords
    keywords = [
        r'\bif\b', r'\belif\b', r'\belse\s+if\b',
        r'\bfor\b', r'\bwhile\b',
        r'\band\b', r'\bor\b',
        r'\b&&\b', r'\b\|\|\b',
        r'\bcase\b',
    ]

    if language == "python":
        keywords += [r'\bexcept\b', r'\bassert\b']
    else:
        keywords += [r'\bcatch\b', r'\bassert\b']

    for pattern in keywords:
        complexity += len(re.findall(pattern, code))

    # Ternary operators
    if language == "python":
        complexity += len(re.findall(r'\bif\b.*\belse\b', code))  # inline if-else
    else:
        complexity += code.count("?")  # C-style ternary

    return max(1, complexity)
