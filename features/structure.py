"""Structural metrics: LOC, nesting depth, loop count, function calls."""

import re


def lines_of_code(code: str) -> int:
    """Count non-empty, non-comment lines."""
    count = 0
    for line in code.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
            count += 1
    return count


def max_nesting_depth(code: str, language: str = "python") -> int:
    """Estimate maximum nesting depth."""
    if language == "python":
        return _nesting_by_indent(code)
    else:
        return _nesting_by_braces(code)


def _nesting_by_indent(code: str) -> int:
    max_depth = 0
    for line in code.split("\n"):
        if line.strip():
            indent = len(line) - len(line.lstrip())
            depth = indent // 4  # assume 4-space indentation
            max_depth = max(max_depth, depth)
    return max_depth


def _nesting_by_braces(code: str) -> int:
    max_depth = 0
    depth = 0
    for ch in code:
        if ch == "{":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == "}":
            depth -= 1
    return max_depth


def loop_count(code: str) -> int:
    """Count for/while loops."""
    return len(re.findall(r'\b(for|while)\b', code))


def function_call_count(code: str) -> int:
    """Count function/method calls (identifier followed by '(')."""
    # Exclude keywords that look like calls
    keywords = {"if", "for", "while", "switch", "catch", "elif", "except",
                "return", "print", "class", "def", "import", "from"}
    calls = re.findall(r'\b(\w+)\s*\(', code)
    return sum(1 for c in calls if c not in keywords)


def function_length(code: str) -> int:
    """Number of statements (non-blank lines) in a code block."""
    return lines_of_code(code)
