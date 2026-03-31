"""Applies colored background highlights to risky lines in the editor."""

from PyQt6.QtGui import QColor


# Risk → background color mapping
RISK_COLORS = {
    "High Risk":   QColor(255, 80, 80, 50),     # red tint
    "Medium Risk": QColor(255, 200, 50, 45),     # yellow tint
    "Low Risk":    QColor(80, 200, 120, 30),     # green tint
}


def get_risk_color(label: str) -> QColor:
    """Return the highlight color for a risk label."""
    return RISK_COLORS.get(label, QColor(0, 0, 0, 0))


def risk_to_icon(label: str) -> str:
    """Return an emoji / text icon for the gutter."""
    icons = {
        "High Risk": "🔴",
        "Medium Risk": "🟡",
        "Low Risk": "🟢",
    }
    return icons.get(label, "")
