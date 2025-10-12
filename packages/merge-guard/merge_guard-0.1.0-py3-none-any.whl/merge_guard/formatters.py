"""Output formatting for issues."""

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from merge_guard.models import Issue


def format_issues(issues: List[Issue], verbose: bool = True) -> None:
    """
    Format and print issues to console.
    
    Args:
        issues: List of detected issues
        verbose: If True, show detailed output with colors
    """
    console = Console()
    
    if not issues:
        console.print("✓ [green]No issues detected![/green]")
        return
    
    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        if issue.file not in issues_by_file:
            issues_by_file[issue.file] = []
        issues_by_file[issue.file].append(issue)
    
    # Header
    total_issues = len(issues)
    total_files = len(issues_by_file)
    
    header = Text()
    header.append("✗ Merge Guard detected ", style="bold red")
    header.append(f"{total_issues}", style="bold yellow")
    header.append(" issue" if total_issues == 1 else " issues", style="bold red")
    header.append(f" in {total_files} file" + ("s" if total_files > 1 else "") + ":", style="bold red")
    
    console.print()
    console.print(header)
    console.print()
    
    # Print issues grouped by file
    for filepath, file_issues in sorted(issues_by_file.items()):
        # File header
        console.print(f"[bold cyan]{filepath}[/bold cyan]")
        
        # Sort issues by line number
        file_issues.sort(key=lambda x: x.line)
        
        for issue in file_issues:
            # Issue type and line number
            console.print(f"  Line {issue.line}: [bold yellow][{issue.type.value}][/bold yellow]")
            
            # Description
            console.print(f"    {issue.description}", style="dim")
            
            # Suggestion (if available)
            if issue.suggestion:
                console.print(f"    💡 {issue.suggestion}", style="italic green")
            
            console.print()
    
    # Summary
    console.print(f"[bold red]Fix these issues and try again.[/bold red]")
    console.print()


def format_issues_simple(issues: List[Issue]) -> str:
    """
    Format issues as plain text (no colors).
    
    Args:
        issues: List of detected issues
        
    Returns:
        Formatted string
    """
    if not issues:
        return "✓ No issues detected!"
    
    lines = []
    lines.append(f"✗ Merge Guard detected {len(issues)} issue(s):\n")
    
    # Group by file
    issues_by_file = {}
    for issue in issues:
        if issue.file not in issues_by_file:
            issues_by_file[issue.file] = []
        issues_by_file[issue.file].append(issue)
    
    for filepath, file_issues in sorted(issues_by_file.items()):
        lines.append(f"\n{filepath}")
        file_issues.sort(key=lambda x: x.line)
        
        for issue in file_issues:
            lines.append(f"  Line {issue.line}: [{issue.type.value}]")
            lines.append(f"    {issue.description}")
            if issue.suggestion:
                lines.append(f"    Suggestion: {issue.suggestion}")
    
    lines.append("\nFix these issues and try again.")
    return "\n".join(lines)


def print_summary(total_files: int, issues_count: int, duration: float) -> None:
    """
    Print analysis summary.
    
    Args:
        total_files: Number of files analyzed
        issues_count: Number of issues found
        duration: Time taken in seconds
    """
    console = Console()
    
    summary = Text()
    summary.append("Analyzed ", style="dim")
    summary.append(f"{total_files}", style="bold")
    summary.append(" file" + ("s" if total_files != 1 else ""), style="dim")
    summary.append(f" in {duration:.2f}s", style="dim")
    
    if issues_count == 0:
        summary.append(" - ", style="dim")
        summary.append("All clear! ✓", style="bold green")
    else:
        summary.append(" - ", style="dim")
        summary.append(f"Found {issues_count} issue" + ("s" if issues_count != 1 else ""), style="bold red")
    
    console.print(summary)

