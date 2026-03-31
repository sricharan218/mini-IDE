"""Pygments-based syntax highlighter integrated with QSyntaxHighlighter."""

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont,
)

# ─── Dark-theme color palette ─────────────────────────────────────

COLORS = {
    "keyword":      QColor("#C678DD"),   # purple
    "builtin":      QColor("#E5C07B"),   # gold
    "string":       QColor("#98C379"),   # green
    "comment":      QColor("#5C6370"),   # grey
    "number":       QColor("#D19A66"),   # orange
    "function":     QColor("#61AFEF"),   # blue
    "class":        QColor("#E5C07B"),   # gold
    "decorator":    QColor("#C678DD"),   # purple
    "operator":     QColor("#56B6C2"),   # cyan
    "type":         QColor("#E5C07B"),   # gold
    "preprocessor": QColor("#C678DD"),   # purple
    "default":      QColor("#ABB2BF"),   # light grey
}


def _fmt(color_key, bold=False, italic=False):
    fmt = QTextCharFormat()
    fmt.setForeground(COLORS.get(color_key, COLORS["default"]))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


# ─── Language rule sets ───────────────────────────────────────────

PYTHON_RULES = [
    (r'\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|'
     r'except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|'
     r'or|pass|raise|return|try|while|with|yield)\b', "keyword", True),
    (r'\b(True|False|None|self|cls|print|len|range|int|float|str|list|dict|'
     r'tuple|set|type|isinstance|super|open|input|map|filter|zip|enumerate)\b', "builtin", False),
    (r'@\w+', "decorator", False),
    (r'\bdef\s+(\w+)', "function", False),
    (r'\bclass\s+(\w+)', "class", True),
    (r'\"\"\".*?\"\"\"', "string", False),
    (r"\'\'\'.*?\'\'\'", "string", False),
    (r'"[^"\\]*(\\.[^"\\]*)*"', "string", False),
    (r"'[^'\\]*(\\.[^'\\]*)*'", "string", False),
    (r'#[^\n]*', "comment", False),
    (r'\b\d+\.?\d*\b', "number", False),
]

C_CPP_RULES = [
    (r'\b(auto|break|case|char|const|continue|default|do|double|else|enum|'
     r'extern|float|for|goto|if|inline|int|long|register|restrict|return|'
     r'short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|'
     r'volatile|while|class|namespace|template|typename|virtual|public|'
     r'private|protected|try|catch|throw|new|delete|bool|true|false|nullptr|'
     r'using|override|final|constexpr|noexcept|decltype|nullptr_t|'
     r'static_cast|dynamic_cast|const_cast|reinterpret_cast)\b', "keyword", True),
    (r'#\s*(include|define|ifdef|ifndef|endif|pragma|if|else|elif|undef|error)', "preprocessor", False),
    (r'\b(printf|scanf|malloc|free|sizeof|strlen|strcpy|memcpy|assert|'
     r'cout|cin|endl|std|vector|string|map|set|pair|queue|stack)\b', "builtin", False),
    (r'"[^"\\]*(\\.[^"\\]*)*"', "string", False),
    (r"'[^'\\]*(\\.[^'\\]*)*'", "string", False),
    (r'//[^\n]*', "comment", False),
    (r'/\*.*?\*/', "comment", False),
    (r'\b\d+\.?\d*[fFlLuU]?\b', "number", False),
]

JAVA_RULES = [
    (r'\b(abstract|assert|boolean|break|byte|case|catch|char|class|const|'
     r'continue|default|do|double|else|enum|extends|final|finally|float|'
     r'for|goto|if|implements|import|instanceof|int|interface|long|native|'
     r'new|package|private|protected|public|return|short|static|strictfp|'
     r'super|switch|synchronized|this|throw|throws|transient|try|void|'
     r'volatile|while|var)\b', "keyword", True),
    (r'\b(true|false|null)\b', "builtin", False),
    (r'\b(System|String|Integer|Double|Float|Boolean|List|Map|Set|'
     r'ArrayList|HashMap|HashSet|IOException|Exception|Override|'
     r'Deprecated|SuppressWarnings)\b', "type", False),
    (r'"[^"\\]*(\\.[^"\\]*)*"', "string", False),
    (r"'[^'\\]*(\\.[^'\\]*)*'", "string", False),
    (r'//[^\n]*', "comment", False),
    (r'/\*.*?\*/', "comment", False),
    (r'\b\d+\.?\d*[fFdDlL]?\b', "number", False),
]

LANGUAGE_RULES = {
    ".py":   PYTHON_RULES,
    ".c":    C_CPP_RULES,
    ".cpp":  C_CPP_RULES,
    ".cc":   C_CPP_RULES,
    ".cxx":  C_CPP_RULES,
    ".h":    C_CPP_RULES,
    ".hpp":  C_CPP_RULES,
    ".java": JAVA_RULES,
}


class SyntaxHighlighter(QSyntaxHighlighter):
    """Applies syntax highlighting to the code editor."""

    def __init__(self, parent=None, extension=".py"):
        super().__init__(parent)
        self._rules = []
        self.set_language(extension)

    def set_language(self, extension: str):
        """Switch highlighting rules based on file extension."""
        rules_def = LANGUAGE_RULES.get(extension, PYTHON_RULES)
        self._rules = []
        for pattern, color_key, bold in rules_def:
            fmt = _fmt(color_key, bold=bold)
            regex = QRegularExpression(pattern)
            self._rules.append((regex, fmt))

    def highlightBlock(self, text):
        for regex, fmt in self._rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)
