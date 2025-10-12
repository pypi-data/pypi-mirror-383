"""Command-line interface for MergeGuard."""

import sys
import time
from typing import List

import click
from rich.console import Console

from merge_guard import __version__
from merge_guard.detector import detect_issues
from merge_guard.formatters import format_issues, print_summary
from merge_guard.git_utils import (
    get_all_staged_diffs,
    get_file_language,
    is_git_repo,
    GitError,
)
from merge_guard.models import Issue


@click.group()
@click.version_option(version=__version__)
def cli():
    """MergeGuard - Detect AI-generated code patterns in Git commits."""
    pass


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def check(verbose: bool):
    """
    Check staged files for code quality issues.
    
    This command analyzes all staged files and detects common issues
    like unused imports, debug statements, and overly complex code.
    """
    console = Console()
    start_time = time.time()
    
    # Check if we're in a git repository
    if not is_git_repo():
        console.print("[bold red]Error:[/bold red] Not a git repository")
        console.print("Run this command from within a git repository.")
        sys.exit(1)
    
    # Get all staged files and their diffs
    try:
        staged_diffs = get_all_staged_diffs()
    except GitError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    
    if not staged_diffs:
        console.print("[yellow]No staged files to check.[/yellow]")
        console.print("Use 'git add' to stage files for commit.")
        sys.exit(0)
    
    # Analyze each file
    all_issues: List[Issue] = []
    
    if verbose:
        console.print(f"[dim]Analyzing {len(staged_diffs)} file(s)...[/dim]\n")
    
    for filepath, (diff, content, changed_lines) in staged_diffs.items():
        language = get_file_language(filepath)
        
        if language == 'unknown':
            continue
        
        if verbose:
            console.print(f"[dim]  Checking {filepath}...[/dim]")
        
        # Run detection
        issues = detect_issues(filepath, content, changed_lines, language)
        all_issues.extend(issues)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Print results
    if verbose:
        console.print()
    
    format_issues(all_issues, verbose=verbose)
    
    if verbose:
        print_summary(len(staged_diffs), len(all_issues), duration)
    
    # Exit with appropriate code
    if all_issues:
        sys.exit(1)  # Issues found - block commit
    else:
        sys.exit(0)  # No issues - allow commit


@cli.command()
def install():
    """
    Install MergeGuard as a git pre-commit hook.
    
    This will create a pre-commit hook that runs 'merge-guard check'
    automatically before each commit.
    """
    console = Console()
    console.print("[yellow]Hook installation not yet implemented.[/yellow]")
    console.print("Coming in Stage 3!")
    console.print("\nFor now, run manually: [bold]merge-guard check[/bold]")


@cli.command()
def uninstall():
    """
    Remove MergeGuard pre-commit hook.
    """
    console = Console()
    console.print("[yellow]Hook uninstallation not yet implemented.[/yellow]")
    console.print("Coming in Stage 3!")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()

