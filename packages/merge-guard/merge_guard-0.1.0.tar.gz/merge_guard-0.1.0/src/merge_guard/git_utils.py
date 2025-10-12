"""Git operations for extracting diffs and staged files."""

import os
from pathlib import Path
from typing import Dict, List, Tuple

import git
import git.exc


class GitError(Exception):
    """Exception raised for Git-related errors."""
    pass


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    try:
        git.Repo(search_parent_directories=True)
        return True
    except git.InvalidGitRepositoryError:
        return False


def get_repo() -> git.Repo:
    """Get the Git repository object."""
    try:
        return git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        raise GitError("Not a git repository")


def get_staged_files() -> List[str]:
    """
    Get list of staged files with supported extensions.
    
    Returns:
        List of file paths relative to repo root
    """
    repo = get_repo()
    
    # Try to get staged files - handle initial commit case
    try:
        # Get all staged files
        staged = repo.index.diff("HEAD", cached=True)
    except (git.GitCommandError, git.exc.BadName):
        # No HEAD yet (initial commit), get all files in index
        staged_files = [item[0] for item in repo.index.entries.keys()]
        return [f for f in staged_files if is_supported_file(f)]
    
    # Filter for supported file types
    supported_files = []
    for item in staged:
        if item.a_path and is_supported_file(item.a_path):
            supported_files.append(item.a_path)
    
    return supported_files


def is_supported_file(filepath: str) -> bool:
    """Check if file type is supported for analysis."""
    supported_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx'}
    ext = Path(filepath).suffix
    return ext in supported_extensions


def get_file_language(filepath: str) -> str:
    """Determine the language of a file based on extension."""
    ext = Path(filepath).suffix
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
    }
    return language_map.get(ext, 'unknown')


def get_staged_diff(filepath: str) -> str:
    """
    Get the diff for a specific staged file.
    
    Args:
        filepath: Path to the file relative to repo root
        
    Returns:
        Git diff as string
    """
    repo = get_repo()
    
    try:
        # Try to get diff against HEAD
        diff = repo.git.diff('HEAD', filepath, cached=True)
    except git.GitCommandError:
        # No HEAD yet (initial commit), get diff against empty tree
        try:
            diff = repo.git.diff(repo.tree(), filepath, cached=True)
        except (git.GitCommandError, ValueError):
            # Fallback: just return the full file as "new"
            full_path = Path(repo.working_dir) / filepath
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return f"+++ {filepath}\n" + "\n".join(f"+{line}" for line in content.splitlines())
            return ""
    
    return diff


def get_file_content(filepath: str) -> str:
    """
    Get the full content of a staged file.
    
    Args:
        filepath: Path to the file relative to repo root
        
    Returns:
        File content as string
    """
    repo = get_repo()
    full_path = Path(repo.working_dir) / filepath
    
    if not full_path.exists():
        raise GitError(f"File not found: {filepath}")
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        raise GitError(f"Cannot read file (binary or encoding issue): {filepath}")


def parse_changed_lines(diff: str) -> List[int]:
    """
    Parse diff to extract line numbers of changed lines.
    
    Args:
        diff: Git diff string
        
    Returns:
        List of line numbers that were changed (added or modified)
    """
    changed_lines = []
    current_line = 0
    
    for line in diff.splitlines():
        # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
        if line.startswith('@@'):
            # Extract new file line number
            try:
                parts = line.split('+')[1].split('@@')[0].strip()
                if ',' in parts:
                    current_line = int(parts.split(',')[0])
                else:
                    current_line = int(parts)
            except (IndexError, ValueError):
                continue
        # Lines starting with + are additions (but not +++)
        elif line.startswith('+') and not line.startswith('+++'):
            changed_lines.append(current_line)
            current_line += 1
        # Lines starting with space are context (not changed)
        elif line.startswith(' '):
            current_line += 1
        # Lines starting with - are deletions (don't increment line number)
    
    return changed_lines


def get_all_staged_diffs() -> Dict[str, Tuple[str, str, List[int]]]:
    """
    Get diffs and content for all staged files.
    
    Returns:
        Dictionary mapping filepath to (diff, content, changed_lines)
    """
    result = {}
    
    for filepath in get_staged_files():
        try:
            diff = get_staged_diff(filepath)
            content = get_file_content(filepath)
            changed_lines = parse_changed_lines(diff)
            result[filepath] = (diff, content, changed_lines)
        except GitError as e:
            # Skip files we can't read
            continue
    
    return result

