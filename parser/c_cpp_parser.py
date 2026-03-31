"""Regex-based parser for C and C++ source files."""

import re
from typing import List

from .base_parser import BaseParser, FunctionInfo, ParseResult


class CCppParser(BaseParser):

    @property
    def language(self) -> str:
        return "c_cpp"

    @property
    def extensions(self) -> List[str]:
        return [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"]

    # Matches:  returnType functionName(params) {
    _FUNC_PATTERN = re.compile(
        r'^[ \t]*'
        r'(?:(?:static|inline|virtual|extern|const|unsigned|signed|volatile)\s+)*'
        r'[\w:*&<>]+\s+'            # return type
        r'([\w:~]+)\s*'             # function name (captured)
        r'\(([^)]*)\)\s*'           # parameters
        r'(?:const\s*)?'
        r'\{',
        re.MULTILINE,
    )

    _INCLUDE_PATTERN = re.compile(r'^\s*#\s*include\s+[<"]([^>"]+)[>"]', re.MULTILINE)
    _CLASS_PATTERN = re.compile(r'^\s*(?:class|struct)\s+(\w+)', re.MULTILINE)

    def parse(self, code: str) -> ParseResult:
        result = ParseResult()
        lines = code.split("\n")

        # --- Imports ---
        for m in self._INCLUDE_PATTERN.finditer(code):
            result.imports.append(f"#include {m.group(1)}")

        # --- Classes ---
        for m in self._CLASS_PATTERN.finditer(code):
            result.classes.append(m.group(1))

        # --- Functions ---
        for m in self._FUNC_PATTERN.finditer(code):
            func_name = m.group(1)
            params_str = m.group(2).strip()
            start_pos = m.start()
            start_line = code[:start_pos].count("\n") + 1

            # Find matching closing brace
            end_line = self._find_closing_brace(lines, start_line - 1)
            func_code = "\n".join(lines[start_line - 1: end_line])

            params_count = 0
            if params_str and params_str != "void":
                params_count = params_str.count(",") + 1

            has_return = bool(re.search(r'\breturn\b', func_code))

            info = FunctionInfo(
                name=func_name,
                start_line=start_line,
                end_line=end_line,
                code=func_code,
                language="c_cpp",
                params_count=params_count,
                has_return=has_return,
            )
            result.functions.append(info)

        # --- Basic syntax errors (unmatched braces) ---
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
                        return i + 1  # 1-indexed
        return len(lines)
