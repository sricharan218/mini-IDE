"""Feature importance horizontal bar chart."""

import matplotlib
matplotlib.use("Agg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class ImportanceChart(QWidget):
    """Horizontal bar chart showing top feature importances."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel("Feature Importance")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("color: #ABB2BF; font-size: 13px; font-weight: bold;")
        layout.addWidget(self._title)

        self._figure = Figure(figsize=(3.5, 2.5), facecolor="#282C34")
        self._canvas = FigureCanvas(self._figure)
        layout.addWidget(self._canvas)

        self._draw({})

    def update_chart(self, importances: dict):
        """importances: {feature_name: importance_value}"""
        self._draw(importances)

    def _draw(self, importances: dict):
        self._figure.clear()
        ax = self._figure.add_subplot(111)
        ax.set_facecolor("#282C34")

        if not importances:
            ax.text(0.5, 0.5, "No data yet",
                    ha="center", va="center", color="#636D83", fontsize=11)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            self._canvas.draw()
            return

        # Top 6 features
        sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:6]
        names = [n.replace("_", " ").title() for n, _ in reversed(sorted_items)]
        values = [v for _, v in reversed(sorted_items)]

        colors = ["#E06C75" if v > 0.15 else "#E5C07B" if v > 0.08 else "#61AFEF"
                  for v in values]

        bars = ax.barh(names, values, color=colors, height=0.6, edgecolor="#3B4048")
        ax.set_xlim(0, max(values) * 1.2 if values else 1)

        # Style
        ax.tick_params(colors="#ABB2BF", labelsize=8)
        ax.xaxis.label.set_color("#ABB2BF")
        for spine in ax.spines.values():
            spine.set_color("#3B4048")

        self._figure.tight_layout()
        self._canvas.draw()
