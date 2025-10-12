"""MergeGuard - Detect AI-generated code patterns in Git commits."""

__version__ = "0.1.0"

from merge_guard.models import Issue, IssueType

__all__ = ["Issue", "IssueType", "__version__"]
