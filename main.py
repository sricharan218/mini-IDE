"""ML-Powered IDE — Main Application Entry Point.

Wires together the code editor, parser, feature extractor, ML predictor,
feedback engine, and dashboard into a cohesive IDE window.
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QMenuBar,
    QToolBar,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon

from editor.file_manager import FileManager
from parser.parser_registry import ParserRegistry
from features.extractor import extract_features, FEATURE_NAMES
from ml.model_loader import load_model
from ml.predictor import Predictor, classify_risk
from feedback.highlighter import risk_to_icon
from feedback.tooltip import build_tooltip, build_status_message
from explanation.explainer import explain_all
from suggestions.suggest import get_suggestions, format_suggestions
from dashboard.dashboard_widget import DashboardWidget
from utils.debounce import Debouncer


class MLPoweredIDE(QMainWindow):
    """Main IDE window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 ML-Powered IDE — Bug Predictor")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 850)

        # ── Dark theme ──────────────────────────────────────────
        self.setStyleSheet("""
            QMainWindow { background-color: #21252B; }
            QMenuBar {
                background-color: #282C34;
                color: #ABB2BF;
                border-bottom: 1px solid #3B4048;
                font-size: 12px;
            }
            QMenuBar::item:selected { background-color: #3E4451; }
            QMenu {
                background-color: #282C34;
                color: #ABB2BF;
                border: 1px solid #3B4048;
            }
            QMenu::item:selected { background-color: #3E4451; }
            QToolBar {
                background-color: #282C34;
                border-bottom: 1px solid #3B4048;
                spacing: 6px;
                padding: 4px;
            }
            QStatusBar {
                background-color: #21252B;
                color: #636D83;
                border-top: 1px solid #3B4048;
                font-size: 11px;
            }
            QSplitter::handle {
                background-color: #3B4048;
                width: 2px;
            }
            QTabBar::tab {
                background-color: #21252B;
                color: #636D83;
                padding: 8px 16px;
                border: 1px solid #3B4048;
                border-bottom: none;
                margin-right: 2px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #282C34;
                color: #ABB2BF;
                border-bottom: 2px solid #61AFEF;
            }
            QTabBar::tab:hover {
                background-color: #2C313A;
            }
        """)

        # ── Core components ─────────────────────────────────────
        self._parser_registry = ParserRegistry()
        self._model = load_model()
        self._predictor = Predictor(self._model) if self._model else None
        self._latest_predictions = []

        # ── UI Layout ───────────────────────────────────────────
        # Main splitter: editor | dashboard
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # File manager (tabs + editors) — must be created before menu/toolbar
        self._file_manager = FileManager()
        splitter.addWidget(self._file_manager)

        # Dashboard
        self._dashboard = DashboardWidget()
        splitter.addWidget(self._dashboard)

        # Build menu and toolbar (they reference _file_manager)
        self._build_menu_bar()
        self._build_toolbar()

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)

        # Status bar
        self._status_bar = QStatusBar()
        self._lang_label = QLabel("Python")
        self._lang_label.setStyleSheet("color: #61AFEF; padding-right: 10px;")
        self._risk_label = QLabel("Ready")
        self._risk_label.setStyleSheet("padding-right: 10px;")
        self._status_bar.addPermanentWidget(self._risk_label)
        self._status_bar.addPermanentWidget(self._lang_label)
        self.setStatusBar(self._status_bar)

        # ── Debounced analysis ──────────────────────────────────
        self._debouncer = Debouncer(400, self._run_analysis)
        self._file_manager.content_changed.connect(self._debouncer.trigger)
        self._file_manager.active_editor_changed.connect(self._on_editor_changed)

        # Initial message
        if not self._model:
            self._dashboard.details_text.setPlainText(
                "⚠ ML model not found!\n\n"
                "Train the model first:\n"
                "  python -m train.train_model\n\n"
                "Then restart the IDE."
            )
            self._status_bar.showMessage("⚠ ML model not loaded — run train/train_model.py first")

    # ════════════════════════════════════════════════════════════
    # Menu Bar & Toolbar
    # ════════════════════════════════════════════════════════════

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self._action("New File", "Ctrl+N", self._file_manager.new_file))
        file_menu.addAction(self._action("Open File", "Ctrl+O", self._file_manager.open_file))
        file_menu.addSeparator()
        file_menu.addAction(self._action("Save", "Ctrl+S", self._file_manager.save_file))
        file_menu.addAction(self._action("Save As...", "Ctrl+Shift+S", self._file_manager.save_file_as))
        file_menu.addSeparator()
        file_menu.addAction(self._action("Exit", "Ctrl+Q", self.close))

        # Analysis menu
        analysis_menu = menu_bar.addMenu("&Analysis")
        analysis_menu.addAction(self._action("Run Analysis Now", "F5", self._run_analysis))
        analysis_menu.addAction(self._action("Clear Results", "", self._clear_results))

        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self._action("About", "", self._show_about))

    def _build_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self._action("📄 New", "", self._file_manager.new_file))
        toolbar.addAction(self._action("📂 Open", "", self._file_manager.open_file))
        toolbar.addAction(self._action("💾 Save", "", self._file_manager.save_file))
        toolbar.addSeparator()
        toolbar.addAction(self._action("▶ Analyze", "", self._run_analysis))
        toolbar.addAction(self._action("🗑 Clear", "", self._clear_results))

    def _action(self, text, shortcut, callback):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        return action

    # ════════════════════════════════════════════════════════════
    # Analysis Pipeline
    # ════════════════════════════════════════════════════════════

    def _on_editor_changed(self, editor):
        if editor:
            lang = self._file_manager.current_language()
            self._lang_label.setText(lang)
            self._debouncer.trigger()

    def _run_analysis(self):
        """Parse → extract features → predict → display results."""
        editor = self._file_manager.current_editor()
        if not editor:
            return

        code = editor.toPlainText()
        if not code.strip():
            editor.clear_risk_data()
            self._dashboard.update_dashboard([])
            return

        ext = self._file_manager.current_extension()
        parser = self._parser_registry.get_parser(ext)

        if not parser:
            self._status_bar.showMessage(f"No parser for {ext}")
            return

        # Parse
        parse_result = parser.parse(code)

        # Show syntax errors
        if parse_result.syntax_errors:
            first_err = parse_result.syntax_errors[0]
            self._status_bar.showMessage(
                f"Syntax Error (line {first_err['line']}): {first_err['message']}"
            )

        if not parse_result.functions:
            editor.clear_risk_data()
            self._dashboard.update_dashboard([])
            if not parse_result.syntax_errors:
                self._status_bar.showMessage("No functions detected")
            return

        # Extract features
        functions_with_features = []
        for func in parse_result.functions:
            features = extract_features(func, parse_result.imports)
            functions_with_features.append((func, features))

        # Predict
        if self._predictor:
            self._predictor.predict_async(
                functions_with_features,
                self._on_predictions_ready,
            )
        else:
            # No model — just show features in dashboard
            self._status_bar.showMessage("ML model not loaded — showing metrics only")

    def _on_predictions_ready(self, predictions):
        """Callback when ML predictions complete."""
        self._latest_predictions = predictions
        editor = self._file_manager.current_editor()
        if not editor:
            return

        # Build risk data for editor highlighting
        risk_data = {}
        for pred in predictions:
            tooltip = build_tooltip(pred)
            for line in range(pred.start_line, pred.end_line + 1):
                risk_data[line] = {
                    "label": pred.label,
                    "tooltip": tooltip,
                }

        editor.set_risk_data(risk_data)

        # Build explanations
        explanations_text = explain_all(predictions)

        # Build suggestions for all functions
        all_suggestions = []
        for pred in predictions:
            sug = get_suggestions(pred.features)
            if sug:
                all_suggestions.append(f"── {pred.function_name} ──")
                all_suggestions.append(format_suggestions(sug))

        suggestions_text = "\n".join(all_suggestions) if all_suggestions else ""

        # Update dashboard
        self._dashboard.update_dashboard(predictions, explanations_text, suggestions_text)

        # Status bar
        if predictions:
            highest = max(predictions, key=lambda p: p.probability)
            self._risk_label.setText(build_status_message(highest))
            self._risk_label.setStyleSheet(
                f"color: {'#E06C75' if highest.probability > 0.7 else '#E5C07B' if highest.probability > 0.4 else '#98C379'}; "
                f"padding-right: 10px; font-weight: bold;"
            )
            self._status_bar.showMessage(
                f"Analyzed {len(predictions)} function(s) — "
                f"Highest risk: {highest.function_name} ({highest.probability:.0%})"
            )

    def _clear_results(self):
        editor = self._file_manager.current_editor()
        if editor:
            editor.clear_risk_data()
        self._latest_predictions = []
        self._dashboard.update_dashboard([])
        self._risk_label.setText("Ready")
        self._risk_label.setStyleSheet("padding-right: 10px;")
        self._status_bar.showMessage("Results cleared")

    def _show_about(self):
        QMessageBox.about(
            self,
            "About ML-Powered IDE",
            "<h2>🧠 ML-Powered IDE</h2>"
            "<p>A lightweight multi-language IDE with machine learning–based "
            "software bug prediction and real-time developer assistance.</p>"
            "<p><b>Supported Languages:</b> Python, C, C++, Java</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Real-time code analysis</li>"
            "<li>ML bug prediction (Low / Medium / High risk)</li>"
            "<li>Feature importance explanations</li>"
            "<li>Code improvement suggestions</li>"
            "<li>Interactive visualization dashboard</li>"
            "</ul>"
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MLPoweredIDE()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
