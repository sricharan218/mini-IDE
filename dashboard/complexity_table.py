"""Per-function complexity metrics table."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class ComplexityTable(QWidget):
    """Table showing per-function metrics: LOC, depth, complexity, risk."""

    COLUMNS = ["Function", "LOC", "Depth", "Complexity", "Loops", "Risk", "Prob"]

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel("Function Metrics")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("color: #ABB2BF; font-size: 13px; font-weight: bold;")
        layout.addWidget(self._title)

        self._table = QTableWidget(0, len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels(self.COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)

        # Style
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: #282C34;
                color: #ABB2BF;
                gridline-color: #3B4048;
                border: none;
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #3E4451;
            }
            QHeaderView::section {
                background-color: #21252B;
                color: #ABB2BF;
                border: 1px solid #3B4048;
                padding: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item:alternate {
                background-color: #2C313A;
            }
        """)
        layout.addWidget(self._table)

    def update_table(self, predictions):
        """Update table with list of PredictionResult objects."""
        self._table.setRowCount(0)

        for pred in predictions:
            row = self._table.rowCount()
            self._table.insertRow(row)

            features = pred.features

            items = [
                pred.function_name,
                str(int(features.get("lines_of_code", 0))),
                str(int(features.get("nesting_depth", 0))),
                str(int(features.get("cyclomatic_complexity", 0))),
                str(int(features.get("loop_count", 0))),
                pred.label,
                f"{pred.probability:.0%}",
            ]

            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Color-code risk column
                if col == 5:
                    if "High" in text:
                        item.setForeground(QColor("#E06C75"))
                    elif "Medium" in text:
                        item.setForeground(QColor("#E5C07B"))
                    else:
                        item.setForeground(QColor("#98C379"))

                self._table.setItem(row, col, item)

    def clear_table(self):
        self._table.setRowCount(0)
