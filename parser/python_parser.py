"""Python parser using the built-in ast module."""

import ast
from typing import List

from .base_parser import BaseParser, FunctionInfo, ParseResult


class PythonParser(BaseParser):

    @property
    def language(self) -> str:
        return "python"

    @property
    def extensions(self) -> List[str]:
        return [".py"]

    def parse(self, code: str) -> ParseResult:
        result = ParseResult()
        lines = code.split("\n")

        # --- Collect imports ---
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                result.imports.append(stripped)

        # --- Try to build AST ---
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            result.syntax_errors.append({
                "line": e.lineno or 1,
                "message": f"SyntaxError: {e.msg}"
            })
            return result

        # --- Walk AST for classes and functions ---
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                result.classes.append(node.name)

        # --- Extract functions (top-level and methods) ---
        self._extract_functions(tree, code, lines, result, class_name=None)

        return result

    def _extract_functions(self, tree, code, lines, result: ParseResult, class_name):
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                # Extract methods within classes
                self._extract_functions(node, code, lines, result, class_name=node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno - 1
                end = node.end_lineno if node.end_lineno else node.lineno
                func_code = "\n".join(lines[start:end])

                # Count nested functions
                nested = sum(
                    1 for child in ast.walk(node)
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and child is not node
                )

                has_return = any(
                    isinstance(child, ast.Return) and child.value is not None
                    for child in ast.walk(node)
                )

                info = FunctionInfo(
                    name=node.name,
                    start_line=node.lineno,
                    end_line=end,
                    code=func_code,
                    language="python",
                    class_name=class_name,
                    params_count=len(node.args.args),
                    has_return=has_return,
                    nested_functions=nested,
                )
                result.functions.append(info)
