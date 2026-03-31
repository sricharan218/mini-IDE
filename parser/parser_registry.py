"""Registry mapping file extensions to language parsers."""

from typing import Dict, Optional

from .base_parser import BaseParser
from .python_parser import PythonParser
from .c_cpp_parser import CCppParser
from .java_parser import JavaParser


class ParserRegistry:
    """Maps file extensions → parser instances."""

    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        # Register built-in parsers
        for parser_cls in (PythonParser, CCppParser, JavaParser):
            self.register(parser_cls())

    def register(self, parser: BaseParser):
        for ext in parser.extensions:
            self._parsers[ext] = parser

    def get_parser(self, extension: str) -> Optional[BaseParser]:
        return self._parsers.get(extension)

    def get_parser_for_file(self, filename: str) -> Optional[BaseParser]:
        import os
        _, ext = os.path.splitext(filename)
        return self.get_parser(ext.lower())

    @property
    def supported_extensions(self):
        return list(self._parsers.keys())
