"""Pattern-based metrics: variable reuse, code duplication, exception handling."""

import re
from collections import Counter


def variable_reuse_count(code: str, language: str = "python") -> int:
    """Count variables that are assigned more than once."""
    if language == "python":
        assignments = re.findall(r'\b(\w+)\s*=\s*(?!=)', code)
    else:
        # C/C++/Java: type var = ...; or var = ...;
        assignments = re.findall(r'\b(\w+)\s*=\s*(?!=)', code)

    counts = Counter(assignments)
    return sum(1 for v, c in counts.items() if c > 1)


def exception_handling_count(code: str, language: str = "python") -> int:
    """Count try/except or try/catch blocks."""
    if language == "python":
        return len(re.findall(r'\btry\b', code))
    else:
        return len(re.findall(r'\btry\b', code))


def code_duplication_score(code: str, min_length: int = 3) -> int:
    """Estimate code duplication by finding repeated line sequences.

    Returns the number of duplicated line groups found.
    """
    lines = [line.strip() for line in code.split("\n") if line.strip()]
    if len(lines) < min_length * 2:
        return 0

    seen = set()
    duplicates = 0
    for i in range(len(lines) - min_length + 1):
        chunk = tuple(lines[i:i + min_length])
        if chunk in seen:
            duplicates += 1
        else:
            seen.add(chunk)

    return duplicates


def import_count(imports: list) -> int:
    """Count the number of dependency imports."""
    return len(imports)
