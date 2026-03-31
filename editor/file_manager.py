"""File manager — multi-tab file open/save/close with language detection."""

import os

from PyQt6.QtWidgets import QTabWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal

from .editor_widget import CodeEditor


EXTENSION_MAP = {
    ".py": "Python",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".java": "Java",
}


class FileManager(QTabWidget):
    """Manages multiple open files in tabs, each with its own CodeEditor."""

    # Emitted when the active tab or its content changes
    active_editor_changed = pyqtSignal(object)   # CodeEditor or None
    content_changed = pyqtSignal()                # any text change

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)

        self._file_paths = {}  # tab_index → file_path (None for unsaved)

        # Open an initial untitled tab
        self.new_file()

    # ── Public API ──────────────────────────────────────────────

    def new_file(self):
        editor = CodeEditor()
        editor.textChanged.connect(self.content_changed.emit)
        index = self.addTab(editor, "Untitled")
        self._file_paths[index] = None
        self.setCurrentIndex(index)
        return editor

    def open_file(self, path: str = None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "All Supported (*.py *.c *.cpp *.cc *.cxx *.h *.hpp *.java);;"
                "Python (*.py);;C/C++ (*.c *.cpp *.h *.hpp);;Java (*.java);;All (*)"
            )
        if not path:
            return

        # Check if already open
        for idx, fp in self._file_paths.items():
            if fp == path:
                self.setCurrentIndex(idx)
                return

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open file:\n{e}")
            return

        editor = CodeEditor()
        ext = os.path.splitext(path)[1].lower()
        editor.set_language(ext)
        editor.setPlainText(content)
        editor.textChanged.connect(self.content_changed.emit)

        name = os.path.basename(path)
        index = self.addTab(editor, name)
        self._file_paths[index] = path
        self.setCurrentIndex(index)

    def save_file(self):
        editor = self.current_editor()
        if not editor:
            return
        idx = self.currentIndex()
        path = self._file_paths.get(idx)

        if not path:
            return self.save_file_as()

        self._write_file(path, editor.toPlainText())
        self.setTabText(idx, os.path.basename(path))

    def save_file_as(self):
        editor = self.current_editor()
        if not editor:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "",
            "Python (*.py);;C (*.c);;C++ (*.cpp);;Java (*.java);;All (*)"
        )
        if path:
            idx = self.currentIndex()
            self._file_paths[idx] = path
            ext = os.path.splitext(path)[1].lower()
            editor.set_language(ext)
            self._write_file(path, editor.toPlainText())
            self.setTabText(idx, os.path.basename(path))

    def close_tab(self, index):
        if self.count() <= 1:
            return  # Keep at least one tab
        self._file_paths.pop(index, None)
        self.removeTab(index)
        # Re-index file paths
        new_paths = {}
        for i in range(self.count()):
            widget = self.widget(i)
            for old_idx, fp in list(self._file_paths.items()):
                if self.widget(old_idx) is widget:
                    new_paths[i] = fp
        self._file_paths = new_paths

    def current_editor(self) -> CodeEditor:
        return self.currentWidget()

    def current_file_path(self):
        return self._file_paths.get(self.currentIndex())

    def current_extension(self):
        path = self.current_file_path()
        if path:
            return os.path.splitext(path)[1].lower()
        return ".py"

    def current_language(self):
        ext = self.current_extension()
        return EXTENSION_MAP.get(ext, "Unknown")

    # ── Private ─────────────────────────────────────────────────

    def _write_file(self, path, content):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot save file:\n{e}")

    def _on_tab_changed(self, index):
        editor = self.widget(index)
        self.active_editor_changed.emit(editor)
