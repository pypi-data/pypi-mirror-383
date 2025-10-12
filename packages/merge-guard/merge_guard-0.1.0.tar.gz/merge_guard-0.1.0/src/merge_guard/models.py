"""Data models for MergeGuard."""

from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    """Types of issues that can be detected in code."""
    
    DEAD_CODE = "DEAD_CODE"
    UNUSED_DEBUG = "UNUSED_DEBUG"
    COMMENTED_CODE = "COMMENTED_CODE"
    COMPLEXITY = "COMPLEXITY"
    EMPTY_HANDLERS = "EMPTY_HANDLERS"
    MEANINGLESS_COMMENT = "MEANINGLESS_COMMENT"
    UNNECESSARY_ELSE = "UNNECESSARY_ELSE"
    TODO_SPAM = "TODO_SPAM"


@dataclass
class Issue:
    """Represents a single code quality issue."""
    
    file: str
    line: int
    type: IssueType
    description: str
    suggestion: str | None = None
    
    def __str__(self) -> str:
        """Format issue for display."""
        result = f"{self.file}:{self.line} [{self.type.value}]\n"
        result += f"  {self.description}"
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
        return result

