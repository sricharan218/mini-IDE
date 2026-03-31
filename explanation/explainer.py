"""Feature importance → human-readable bug explanation."""


def explain_prediction(prediction) -> str:
    """Generate a multi-line explanation for a prediction result."""
    lines = [
        f"{'═' * 50}",
        f"  Bug Risk Analysis: {prediction.function_name}",
        f"{'═' * 50}",
        f"",
        f"  Risk Level : {prediction.label}",
        f"  Bug Probability : {prediction.probability:.0%}",
        f"",
    ]

    if prediction.feature_importances:
        lines.append("  Main Contributing Factors:")
        lines.append("  " + "─" * 40)

        sorted_fi = sorted(
            prediction.feature_importances.items(),
            key=lambda x: -x[1],
        )
        total = sum(v for _, v in sorted_fi) or 1

        for name, importance in sorted_fi[:5]:
            pretty = name.replace("_", " ").title()
            value = prediction.features.get(name, "N/A")
            pct = importance / total * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            lines.append(f"  • {pretty:30s} = {value}")
            lines.append(f"    Contribution: {bar} {pct:.0f}%")

    lines.append("")
    lines.append(f"{'═' * 50}")
    return "\n".join(lines)


def explain_all(predictions) -> str:
    """Explain all predictions for a file."""
    if not predictions:
        return "No functions analyzed yet."
    return "\n\n".join(explain_prediction(p) for p in predictions)
