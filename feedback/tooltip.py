"""Tooltip / status-bar message generation for hover explanations."""


def build_tooltip(prediction) -> str:
    """Build a rich tooltip string from a PredictionResult."""
    lines = [
        f"⚠ Bug Risk: {prediction.probability:.0%} — {prediction.label}",
        f"Function: {prediction.function_name}",
        f"Lines: {prediction.start_line}–{prediction.end_line}",
        "",
    ]

    if prediction.feature_importances:
        lines.append("Contributing factors:")
        sorted_fi = sorted(
            prediction.feature_importances.items(),
            key=lambda x: -x[1]
        )
        for name, imp in sorted_fi[:5]:
            pretty = name.replace("_", " ").title()
            val = prediction.features.get(name, "?")
            lines.append(f"  • {pretty}: {val}  (importance: {imp:.2f})")

    return "\n".join(lines)


def build_status_message(prediction) -> str:
    """Short one-line status bar message."""
    return (
        f"{prediction.label}: {prediction.function_name} "
        f"({prediction.probability:.0%} bug risk)"
    )
