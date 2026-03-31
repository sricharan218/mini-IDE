# 🧠 ML-Powered IDE — Bug Predictor

A lightweight, multi-language Integrated Development Environment with **machine learning–based software bug prediction** and **real-time developer assistance**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)
![ML](https://img.shields.io/badge/ML-scikit--learn-orange)

---

## Features

- **Multi-language editor** — Python, C, C++, Java with syntax highlighting
- **Real-time code parsing** — AST-based analysis as you type
- **ML bug prediction** — Low / Medium / High risk per function
- **Feature extraction** — 10 software metrics (complexity, nesting, LOC, etc.)
- **Interactive dashboard** — Bug probability gauge, feature importance chart, metrics table
- **Code suggestions** — Actionable recommendations to improve code quality
- **Explanation system** — See why a function is flagged as risky

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the ML Model

```bash
python -m train.train_model
```

This trains a RandomForest classifier on synthetic bug data and saves it to `ml/models/bug_predictor.pkl`.

### 3. Launch the IDE

```bash
python main.py
```

---

## Project Structure

```
ml-ide/
├── main.py                  # Entry point
├── editor/                  # Code editor (syntax highlight, tabs, line numbers)
├── parser/                  # Language parsers (Python, C/C++, Java)
├── features/                # Feature extraction (complexity, nesting, LOC…)
├── ml/                      # ML model loader, predictor, cache
│   └── models/              # Pre-trained .pkl models
├── feedback/                # Editor highlighting and gutter icons
├── explanation/             # Bug explanation generator
├── suggestions/             # Code improvement suggestions
├── dashboard/               # Visualization panel (gauge, charts, table)
├── train/                   # ML model training scripts
├── utils/                   # Utilities (debounce)
└── requirements.txt
```

---

## Supported Languages

| Language | Parser | Extensions |
|----------|--------|------------|
| Python | `ast` module | `.py` |
| C | Regex-based | `.c`, `.h` |
| C++ | Regex-based | `.cpp`, `.cc`, `.hpp` |
| Java | Regex-based | `.java` |

### Adding a New Language

1. Create a new parser in `parser/` implementing `BaseParser`
2. Register it in `parser/parser_registry.py`
3. Add syntax highlighting rules in `editor/syntax_highlighter.py`

---

## Software Metrics Extracted

| Metric | Description |
|--------|-------------|
| Lines of Code | Non-empty, non-comment lines |
| Function Length | Statement count in function |
| Nesting Depth | Maximum indentation/brace depth |
| Cyclomatic Complexity | Decision points (if, for, while, and, or...) |
| Loop Count | for/while loop occurrences |
| Function Call Count | Number of function invocations |
| Variable Reuse | Variables assigned more than once |
| Exception Handling | try/except or try/catch blocks |
| Code Duplication | Repeated line sequences |
| Import Count | Number of dependency imports |

---

## How Bug Prediction Works

1. **Parse** — Code is parsed into functions using language-specific parsers
2. **Extract** — 10 software metrics are computed per function
3. **Predict** — A trained RandomForest model estimates bug probability
4. **Classify** — Risk is categorized: 🟢 Low (0–40%) · 🟡 Medium (41–70%) · 🔴 High (71–100%)
5. **Display** — Risky lines are highlighted, gutter icons appear, dashboard updates

---

## License

MIT
