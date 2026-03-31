"""Rule-based suggestion engine mapping code metrics → actionable recommendations."""

from typing import List, Dict

# Thresholds for triggering suggestions
THRESHOLDS = {
    "cyclomatic_complexity": 10,
    "nesting_depth": 4,
    "function_length": 50,
    "lines_of_code": 80,
    "loop_count": 4,
    "variable_reuse": 5,
    "code_duplication": 2,
    "function_call_count": 15,
}

# Suggestion messages
SUGGESTIONS = {
    "cyclomatic_complexity": {
        "title": "High Cyclomatic Complexity",
        "message": "Consider splitting this function into smaller, focused units. "
                   "Extract conditional branches into helper methods.",
        "severity": "warning",
    },
    "nesting_depth": {
        "title": "Deep Nesting Detected",
        "message": "Reduce nesting depth by using early returns, guard clauses, "
                   "or extracting inner blocks into separate functions.",
        "severity": "warning",
    },
    "function_length": {
        "title": "Long Function Body",
        "message": "This function exceeds the recommended length. "
                   "Break it into smaller, more manageable pieces.",
        "severity": "info",
    },
    "lines_of_code": {
        "title": "Too Many Lines",
        "message": "Consider refactoring to reduce the number of lines. "
                   "Look for opportunities to extract reusable components.",
        "severity": "info",
    },
    "loop_count": {
        "title": "Many Loops",
        "message": "Multiple loops increase complexity. Consider using "
                   "built-in functions, list comprehensions, or map/filter.",
        "severity": "info",
    },
    "variable_reuse": {
        "title": "Excessive Variable Reassignment",
        "message": "Variables are reassigned frequently. Use descriptive names "
                   "and consider immutable patterns where possible.",
        "severity": "info",
    },
    "code_duplication": {
        "title": "Code Duplication Detected",
        "message": "Extract repeated logic into a reusable function or utility.",
        "severity": "warning",
    },
    "function_call_count": {
        "title": "High Number of Function Calls",
        "message": "Many function calls may indicate this function is doing too much. "
                   "Consider the Single Responsibility Principle.",
        "severity": "info",
    },
}


def get_suggestions(features: Dict[str, float]) -> List[dict]:
    """Return a list of suggestions based on the features exceeding thresholds."""
    result = []
    for metric, threshold in THRESHOLDS.items():
        value = features.get(metric, 0)
        if value >= threshold:
            suggestion = SUGGESTIONS[metric].copy()
            suggestion["metric"] = metric
            suggestion["value"] = value
            suggestion["threshold"] = threshold
            result.append(suggestion)

    # Sort by severity (warnings first)
    result.sort(key=lambda s: 0 if s["severity"] == "warning" else 1)
    return result


def format_suggestions(suggestions: List[dict]) -> str:
    """Format suggestions as readable text."""
    if not suggestions:
        return "✅ No issues detected. Code quality looks good!"

    lines = ["💡 Suggestions for improvement:", ""]
    for s in suggestions:
        icon = "⚠️" if s["severity"] == "warning" else "ℹ️"
        lines.append(f"{icon} {s['title']} ({s['metric']}: {s['value']}, threshold: {s['threshold']})")
        lines.append(f"   {s['message']}")
        lines.append("")

    return "\n".join(lines)
