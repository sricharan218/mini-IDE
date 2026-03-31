"""Abstract base class for all language parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FunctionInfo:
    """Represents a parsed function/method with its metadata."""
    name: str
    start_line: int
    end_line: int
    code: str
    language: str
    class_name: Optional[str] = None
    # Pre-extracted raw counts (parsers fill what they can)
    params_count: int = 0
    has_return: bool = False
    nested_functions: int = 0


@dataclass
class ParseResult:
    """Result of parsing a source file."""
    functions: List[FunctionInfo] = field(default_factory=list)
    syntax_errors: List[dict] = field(default_factory=list)  # {line, message}
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)


class BaseParser(ABC):
    """Abstract parser interface. Implement for each supported language."""

    @property
    @abstractmethod
    def language(self) -> str:
        ...

    @property
    @abstractmethod
    def extensions(self) -> List[str]:
        ...

    @abstractmethod
    def parse(self, code: str) -> ParseResult:
        """Parse source code and return structured results."""
        ...
