"""Regex-based parser for Java source files."""

import re
from typing import List

from .base_parser import BaseParser, FunctionInfo, ParseResult


class JavaParser(BaseParser):

    @property
    def language(self) -> str:
        return "java"

    @property
    def extensions(self) -> List[str]:
        return [".java"]

    _METHOD_PATTERN = re.compile(
        r'^[ \t]*'
        r'(?:(?:public|private|protected|static|final|abstract|synchronized|native)\s+)*'
        r'[\w<>\[\]]+\s+'           # return type
        r'(\w+)\s*'                 # method name
        r'\(([^)]*)\)\s*'           # parameters
        r'(?:throws\s+[\w,\s]+\s*)?'
        r'\{',
        re.MULTILINE,
    )

    _IMPORT_PATTERN = re.compile(r'^\s*import\s+([\w.*]+)\s*;', re.MULTILINE)
    _CLASS_PATTERN = re.compile(
        r'^\s*(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)',
        re.MULTILINE,
    )

    def parse(self, code: str) -> ParseResult:
        result = ParseResult()
        lines = code.split("\n")

        # --- Imports ---
        for m in self._IMPORT_PATTERN.finditer(code):
            result.imports.append(m.group(1))

        # --- Classes ---
        for m in self._CLASS_PATTERN.finditer(code):
            result.classes.append(m.group(1))

        # --- Methods ---
        for m in self._METHOD_PATTERN.finditer(code):
            name = m.group(1)
            params_str = m.group(2).strip()
            start_pos = m.start()
            start_line = code[:start_pos].count("\n") + 1

            end_line = self._find_closing_brace(lines, start_line - 1)
            func_code = "\n".join(lines[start_line - 1: end_line])

            params_count = 0
            if params_str:
                params_count = params_str.count(",") + 1

            has_return = bool(re.search(r'\breturn\b', func_code))

            info = FunctionInfo(
                name=name,
                start_line=start_line,
                end_line=end_line,
                code=func_code,
                language="java",
                params_count=params_count,
                has_return=has_return,
            )
            result.functions.append(info)

        # --- Basic syntax check ---
        open_b = code.count("{")
        close_b = code.count("}")
        if open_b != close_b:
            result.syntax_errors.append({
                "line": len(lines),
                "message": f"Unmatched braces: {open_b} '{{' vs {close_b} '}}'"
            })

        return result

    @staticmethod
    def _find_closing_brace(lines, start_idx):
        depth = 0
        for i in range(start_idx, len(lines)):
            for ch in lines[i]:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return i + 1
        return len(lines)
