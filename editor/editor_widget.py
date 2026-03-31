"""Code editor widget with line numbers, bracket completion, and gutter icons."""

from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget, QToolTip
from PyQt6.QtCore import Qt, QRect, QSize, QPoint
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QTextFormat,
    QTextCursor,
    QPen,
    QFontMetrics,
)

from .syntax_highlighter import SyntaxHighlighter
from feedback.highlighter import get_risk_color, risk_to_icon


# ─── Bracket auto-completion map ──────────────────────────────────

BRACKET_PAIRS = {
    "(": ")",
    "[": "]",
    "{": "}",
    '"': '"',
    "'": "'",
}


class LineNumberArea(QWidget):
    """Draws line numbers and gutter icons alongside the editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Rich code editor with line numbers, highlighting, and gutter annotations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._extension = ".py"
        self._gutter_data = {}  # line -> annotation dict
        self._risk_lines = {}   # line -> risk_label

        # Font
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Colors
        self._bg_color = QColor("#282C34")
        self._fg_color = QColor("#ABB2BF")
        self._line_highlight = QColor("#2C313A")
        self._gutter_bg = QColor("#21252B")
        self._gutter_fg = QColor("#636D83")

        palette = self.palette()
        palette.setColor(palette.ColorRole.Base, self._bg_color)
        palette.setColor(palette.ColorRole.Text, self._fg_color)
        self.setPalette(palette)

        # Tab / indentation
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(" ") * 4)

        # Syntax highlighter
        self._highlighter = SyntaxHighlighter(self.document(), self._extension)

        # Line number area
        self._line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self._update_line_number_area_width(0)
        self._highlight_current_line()

    # ── Public API ──────────────────────────────────────────────

    def set_language(self, extension: str):
        self._extension = extension
        self._highlighter.set_language(extension)
        self._highlighter.rehighlight()

    def set_risk_data(self, risk_data: dict):
        """Set risk data: {line_number: {'label': str, 'tooltip': str}}."""
        self._risk_lines = {}
        self._gutter_data = {}
        for line, info in risk_data.items():
            self._risk_lines[line] = info.get("label", "")
            self._gutter_data[line] = info
        self._highlight_current_line()
        self._line_number_area.update()

    def clear_risk_data(self):
        self._risk_lines.clear()
        self._gutter_data.clear()
        self._highlight_current_line()
        self._line_number_area.update()

    # ── Line numbers ────────────────────────────────────────────

    def line_number_area_width(self):
        digits = max(1, len(str(self.blockCount())))
        gutter_icon_space = 22
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits + gutter_icon_space

    def _update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(),
                                          self._line_number_area.width(),
                                          rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(),
                  self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), self._gutter_bg)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number + 1
                number = str(line_num)

                # Draw gutter icon
                if line_num in self._gutter_data:
                    info = self._gutter_data[line_num]
                    label = info.get("label", "")
                    icon = risk_to_icon(label)
                    if icon:
                        painter.setPen(QPen(QColor("#ABB2BF")))
                        painter.drawText(
                            0, top,
                            20, self.fontMetrics().height(),
                            Qt.AlignmentFlag.AlignCenter, icon,
                        )

                # Draw line number
                painter.setPen(QPen(self._gutter_fg))
                painter.drawText(
                    0, top,
                    self._line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    # ── Current-line and risk highlighting ───────────────────────

    def _highlight_current_line(self):
        extra = []

        # Current line highlight
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(self._line_highlight)
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extra.append(selection)

        # Risk line highlights
        block = self.document().begin()
        while block.isValid():
            line_num = block.blockNumber() + 1
            if line_num in self._risk_lines:
                label = self._risk_lines[line_num]
                color = get_risk_color(label)
                sel = QTextEdit.ExtraSelection()
                sel.format.setBackground(color)
                sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                cursor = QTextCursor(block)
                sel.cursor = cursor
                extra.append(sel)
            block = block.next()

        self.setExtraSelections(extra)

    # ── Bracket completion ──────────────────────────────────────

    def keyPressEvent(self, event):
        text = event.text()
        if text in BRACKET_PAIRS:
            closing = BRACKET_PAIRS[text]
            cursor = self.textCursor()
            cursor.insertText(text + closing)
            cursor.movePosition(QTextCursor.MoveOperation.Left)
            self.setTextCursor(cursor)
            return

        # Auto-indent after colon (Python) or brace
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            line = cursor.block().text()
            indent = len(line) - len(line.lstrip())
            extra_indent = ""
            stripped = line.rstrip()
            if stripped.endswith(":") or stripped.endswith("{"):
                extra_indent = "    "
            super().keyPressEvent(event)
            if indent or extra_indent:
                self.insertPlainText(" " * indent + extra_indent)
            return

        super().keyPressEvent(event)

    # ── Tooltip on hover ────────────────────────────────────────

    def mouseMoveEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        line_num = cursor.blockNumber() + 1
        if line_num in self._gutter_data:
            tooltip = self._gutter_data[line_num].get("tooltip", "")
            if tooltip:
                QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
        else:
            QToolTip.hideText()
        super().mouseMoveEvent(event)
