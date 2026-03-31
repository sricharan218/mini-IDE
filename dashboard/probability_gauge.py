"""Bug probability gauge widget using matplotlib."""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class ProbabilityGauge(QWidget):
    """Semi-circular gauge showing bug probability."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel("Bug Risk Gauge")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("color: #ABB2BF; font-size: 13px; font-weight: bold;")
        layout.addWidget(self._title)

        self._figure = Figure(figsize=(3.5, 2), facecolor="#282C34")
        self._canvas = FigureCanvas(self._figure)
        layout.addWidget(self._canvas)

        self._probability = 0.0
        self._func_name = ""
        self._draw()

    def update_gauge(self, probability: float, func_name: str = ""):
        self._probability = probability
        self._func_name = func_name
        self._draw()

    def _draw(self):
        self._figure.clear()
        ax = self._figure.add_subplot(111, polar=True)

        # Configure as semi-circle gauge
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_ylim(0, 1)
        ax.set_facecolor("#282C34")

        # Background arc
        theta_bg = np.linspace(0, np.pi, 100)
        ax.fill_between(theta_bg, 0, 0.85, color="#3B4048", alpha=0.5)

        # Colored arcs: green → yellow → red
        segments = [
            (0, 0.4 * np.pi, "#4EC956"),
            (0.4 * np.pi, 0.7 * np.pi, "#E5C07B"),
            (0.7 * np.pi, np.pi, "#E06C75"),
        ]
        for start, end, color in segments:
            theta = np.linspace(start, end, 50)
            ax.fill_between(theta, 0.65, 0.85, color=color, alpha=0.6)

        # Needle
        angle = self._probability * np.pi
        ax.plot([angle, angle], [0, 0.7], color="#E5C07B", linewidth=2.5)
        ax.plot(angle, 0.7, "o", color="#E06C75" if self._probability > 0.7
                else "#E5C07B" if self._probability > 0.4 else "#4EC956",
                markersize=6)

        # Center label
        ax.text(np.pi / 2, 0.3, f"{self._probability:.0%}",
                ha="center", va="center", fontsize=16, fontweight="bold",
                color="#ABB2BF")

        if self._func_name:
            ax.text(np.pi / 2, 0.05, self._func_name,
                    ha="center", va="center", fontsize=9, color="#636D83")

        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["polar"].set_visible(False)

        self._canvas.draw()
