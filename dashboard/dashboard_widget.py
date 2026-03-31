"""Dashboard container combining gauge, chart, table, and explanation panel."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QScrollArea,
    QSplitter,
)
from PyQt6.QtCore import Qt

from .probability_gauge import ProbabilityGauge
from .importance_chart import ImportanceChart
from .complexity_table import ComplexityTable


class DashboardWidget(QWidget):
    """Side panel dashboard with bug prediction visualizations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(340)
        self.setMaximumWidth(500)

        self.setStyleSheet("background-color: #21252B;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("🧠 ML Bug Predictor")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            "color: #61AFEF; font-size: 16px; font-weight: bold; "
            "padding: 8px; background-color: #282C34; border-radius: 6px;"
        )
        layout.addWidget(header)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #21252B; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)

        # Gauge
        self.gauge = ProbabilityGauge()
        content_layout.addWidget(self.gauge)

        # Importance chart
        self.importance_chart = ImportanceChart()
        content_layout.addWidget(self.importance_chart)

        # Complexity table
        self.complexity_table = ComplexityTable()
        content_layout.addWidget(self.complexity_table)

        # Explanation / Suggestions text area
        explain_label = QLabel("📋 Analysis Details")
        explain_label.setStyleSheet(
            "color: #ABB2BF; font-size: 13px; font-weight: bold; padding-top: 6px;"
        )
        content_layout.addWidget(explain_label)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMinimumHeight(150)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #282C34;
                color: #ABB2BF;
                border: 1px solid #3B4048;
                border-radius: 4px;
                padding: 6px;
                font-family: Consolas, monospace;
                font-size: 11px;
            }
        """)
        content_layout.addWidget(self.details_text)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def update_dashboard(self, predictions, explanations_text="", suggestions_text=""):
        """Refresh all dashboard widgets with new prediction data."""
        if not predictions:
            self.gauge.update_gauge(0.0, "No functions")
            self.importance_chart.update_chart({})
            self.complexity_table.clear_table()
            self.details_text.setPlainText("Write some code to see analysis results.")
            return

        # Use highest-risk function for gauge
        highest = max(predictions, key=lambda p: p.probability)
        self.gauge.update_gauge(highest.probability, highest.function_name)

        # Feature importances from highest-risk function
        self.importance_chart.update_chart(highest.feature_importances)

        # Table
        self.complexity_table.update_table(predictions)

        # Details text
        details = []
        if explanations_text:
            details.append(explanations_text)
        if suggestions_text:
            details.append(suggestions_text)
        self.details_text.setPlainText("\n\n".join(details) if details else "Analysis complete.")
