"""Rule-based detection engine for code quality issues."""

import ast
import re
from typing import List, Set

from merge_guard.models import Issue, IssueType


def detect_issues(filepath: str, file_content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """
    Run all detection rules on a file.
    
    Args:
        filepath: Path to the file
        file_content: Full content of the file
        changed_lines: List of line numbers that were changed
        language: Programming language (python, javascript, typescript)
        
    Returns:
        List of detected issues
    """
    issues = []
    
    # Run all detectors
    issues.extend(detect_unused_imports(filepath, file_content, changed_lines, language))
    issues.extend(detect_unused_debug(filepath, file_content, changed_lines, language))
    issues.extend(detect_commented_code(filepath, file_content, changed_lines, language))
    issues.extend(detect_complexity(filepath, file_content, changed_lines, language))
    issues.extend(detect_empty_handlers(filepath, file_content, changed_lines, language))
    issues.extend(detect_meaningless_comments(filepath, file_content, changed_lines, language))
    issues.extend(detect_unnecessary_else(filepath, file_content, changed_lines, language))
    issues.extend(detect_todo_spam(filepath, file_content, changed_lines, language))
    
    return issues


# ============================================================================
# Rule 1: DEAD_CODE - Unused Imports
# ============================================================================

def detect_unused_imports(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect unused imports."""
    issues = []
    
    if language == "python":
        issues.extend(_detect_unused_imports_python(filepath, content, changed_lines))
    elif language in ("javascript", "typescript"):
        issues.extend(_detect_unused_imports_js(filepath, content, changed_lines))
    
    return issues


def _detect_unused_imports_python(filepath: str, content: str, changed_lines: List[int]) -> List[Issue]:
    """Detect unused imports in Python files."""
    issues = []
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return issues  # Skip files with syntax errors
    
    # Find all imports
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name.split('.')[0]
                imports[name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != '*':
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = node.lineno
    
    # Check if each import is used
    for import_name, line_num in imports.items():
        # Only check imports in changed lines
        if line_num not in changed_lines:
            continue
        
        # Check if import is used anywhere else in the file
        is_used = False
        for node in ast.walk(tree):
            # Check Name nodes
            if isinstance(node, ast.Name) and node.id == import_name:
                if node.lineno != line_num:  # Don't count the import itself
                    is_used = True
                    break
            # Check Attribute nodes (for module.attribute)
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == import_name:
                    is_used = True
                    break
        
        if not is_used:
            issues.append(Issue(
                file=filepath,
                line=line_num,
                type=IssueType.DEAD_CODE,
                description=f"Unused import '{import_name}'",
                suggestion=f"Remove this import if not needed"
            ))
    
    return issues


def _detect_unused_imports_js(filepath: str, content: str, changed_lines: List[int]) -> List[Issue]:
    """Detect unused imports in JavaScript/TypeScript files."""
    issues = []
    lines = content.splitlines()
    
    # Regex patterns for imports
    import_patterns = [
        r'import\s+(\w+)\s+from',  # import X from 'module'
        r'import\s+\{([^}]+)\}\s+from',  # import { X, Y } from 'module'
        r'const\s+(\w+)\s*=\s*require\(',  # const X = require('module')
    ]
    
    for line_num, line in enumerate(lines, 1):
        if line_num not in changed_lines:
            continue
        
        line = line.strip()
        for pattern in import_patterns:
            match = re.search(pattern, line)
            if match:
                # Extract imported names
                imported = match.group(1)
                names = [name.strip() for name in imported.split(',')]
                
                for name in names:
                    # Clean up name (remove as clauses, etc.)
                    name = name.split()[0]
                    
                    # Check if used in rest of file
                    is_used = False
                    for other_line_num, other_line in enumerate(lines, 1):
                        if other_line_num != line_num:
                            # Simple check: is the name mentioned elsewhere?
                            if re.search(r'\b' + re.escape(name) + r'\b', other_line):
                                is_used = True
                                break
                    
                    if not is_used:
                        issues.append(Issue(
                            file=filepath,
                            line=line_num,
                            type=IssueType.DEAD_CODE,
                            description=f"Unused import '{name}'",
                            suggestion="Remove this import if not needed"
                        ))
    
    return issues


# ============================================================================
# Rule 2: UNUSED_DEBUG - Debug Statements
# ============================================================================

def detect_unused_debug(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect leftover debug statements."""
    issues = []
    lines = content.splitlines()
    
    debug_patterns = {
        "python": [
            (r'\bprint\s*\(', "print() statement"),
            (r'\bpprint\s*\(', "pprint() statement"),
            (r'\bpdb\.set_trace\s*\(', "pdb.set_trace() debugger"),
            (r'\bbreakpoint\s*\(', "breakpoint() debugger"),
        ],
        "javascript": [
            (r'\bconsole\.log\s*\(', "console.log() statement"),
            (r'\bconsole\.debug\s*\(', "console.debug() statement"),
            (r'\bconsole\.warn\s*\(', "console.warn() statement"),
            (r'\bdebugger\b', "debugger statement"),
        ],
        "typescript": [
            (r'\bconsole\.log\s*\(', "console.log() statement"),
            (r'\bconsole\.debug\s*\(', "console.debug() statement"),
            (r'\bconsole\.warn\s*\(', "console.warn() statement"),
            (r'\bdebugger\b', "debugger statement"),
        ],
    }
    
    patterns = debug_patterns.get(language, [])
    
    for line_num, line in enumerate(lines, 1):
        if line_num not in changed_lines:
            continue
        
        for pattern, description in patterns:
            if re.search(pattern, line):
                issues.append(Issue(
                    file=filepath,
                    line=line_num,
                    type=IssueType.UNUSED_DEBUG,
                    description=f"Debug statement: {description}",
                    suggestion="Remove debug statement before committing"
                ))
    
    return issues


# ============================================================================
# Rule 3: COMMENTED_CODE - Commented Out Code
# ============================================================================

def detect_commented_code(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect blocks of commented-out code."""
    issues = []
    lines = content.splitlines()
    
    comment_char = '#' if language == 'python' else '//'
    
    consecutive_comments = []
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped.startswith(comment_char):
            # Check if this looks like code (contains =, (), {}, etc.)
            comment_text = stripped.lstrip(comment_char).strip()
            if _looks_like_code(comment_text):
                consecutive_comments.append(line_num)
            else:
                # If it's a real comment, reset
                if len(consecutive_comments) >= 3:
                    # Check if any of these are in changed lines
                    if any(ln in changed_lines for ln in consecutive_comments):
                        start_line = consecutive_comments[0]
                        issues.append(Issue(
                            file=filepath,
                            line=start_line,
                            type=IssueType.COMMENTED_CODE,
                            description=f"Block of {len(consecutive_comments)} lines of commented-out code",
                            suggestion="Remove commented code or document why it's kept"
                        ))
                consecutive_comments = []
        else:
            # Not a comment, check if we had a block
            if len(consecutive_comments) >= 3:
                if any(ln in changed_lines for ln in consecutive_comments):
                    start_line = consecutive_comments[0]
                    issues.append(Issue(
                        file=filepath,
                        line=start_line,
                        type=IssueType.COMMENTED_CODE,
                        description=f"Block of {len(consecutive_comments)} lines of commented-out code",
                        suggestion="Remove commented code or document why it's kept"
                    ))
            consecutive_comments = []
    
    # Check last block
    if len(consecutive_comments) >= 3:
        if any(ln in changed_lines for ln in consecutive_comments):
            start_line = consecutive_comments[0]
            issues.append(Issue(
                file=filepath,
                line=start_line,
                type=IssueType.COMMENTED_CODE,
                description=f"Block of {len(consecutive_comments)} lines of commented-out code",
                suggestion="Remove commented code or document why it's kept"
            ))
    
    return issues


def _looks_like_code(text: str) -> bool:
    """Check if a string looks like code vs. documentation."""
    code_indicators = ['=', '(', ')', '{', '}', '[', ']', ';', 'def ', 'function ', 'const ', 'let ', 'var ', 'return ', 'if ', 'for ', 'while ']
    return any(indicator in text for indicator in code_indicators)


# ============================================================================
# Rule 4: COMPLEXITY - Nesting Depth
# ============================================================================

def detect_complexity(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect overly nested code."""
    issues = []
    lines = content.splitlines()
    
    max_depth = 4
    indent_size = 4 if language == 'python' else 2
    
    for line_num, line in enumerate(lines, 1):
        if line_num not in changed_lines:
            continue
        
        # Skip blank lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            continue
        
        # Count indentation
        indent = len(line) - len(line.lstrip())
        depth = indent // indent_size
        
        if depth > max_depth:
            issues.append(Issue(
                file=filepath,
                line=line_num,
                type=IssueType.COMPLEXITY,
                description=f"Nesting depth of {depth} exceeds limit of {max_depth}",
                suggestion="Consider extracting nested logic into separate functions"
            ))
    
    return issues


# ============================================================================
# Rule 5: EMPTY_HANDLERS - Empty Catch/Except Blocks
# ============================================================================

def detect_empty_handlers(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect empty exception handlers."""
    issues = []
    
    if language == "python":
        issues.extend(_detect_empty_handlers_python(filepath, content, changed_lines))
    elif language in ("javascript", "typescript"):
        issues.extend(_detect_empty_handlers_js(filepath, content, changed_lines))
    
    return issues


def _detect_empty_handlers_python(filepath: str, content: str, changed_lines: List[int]) -> List[Issue]:
    """Detect empty except blocks in Python."""
    issues = []
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return issues
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            # Check if handler only contains pass
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                if node.lineno in changed_lines:
                    issues.append(Issue(
                        file=filepath,
                        line=node.lineno,
                        type=IssueType.EMPTY_HANDLERS,
                        description="Empty except block with only 'pass'",
                        suggestion="Handle the exception or at least log it"
                    ))
    
    return issues


def _detect_empty_handlers_js(filepath: str, content: str, changed_lines: List[int]) -> List[Issue]:
    """Detect empty catch blocks in JavaScript/TypeScript."""
    issues = []
    lines = content.splitlines()
    
    # Simple pattern matching for catch () {}
    for line_num, line in enumerate(lines, 1):
        if line_num not in changed_lines:
            continue
        
        # Look for catch followed by empty block
        if re.search(r'catch\s*\([^)]*\)\s*\{\s*\}', line):
            issues.append(Issue(
                file=filepath,
                line=line_num,
                type=IssueType.EMPTY_HANDLERS,
                description="Empty catch block",
                suggestion="Handle the error or at least log it"
            ))
    
    return issues


# ============================================================================
# Rule 6: MEANINGLESS_COMMENT - Obvious Comments
# ============================================================================

def detect_meaningless_comments(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect comments that don't add value."""
    issues = []
    lines = content.splitlines()
    
    # Patterns of meaningless comments
    meaningless_patterns = [
        r'#\s*(initialize|init|create|set|get|return|import)\s+\w+',  # Python
        r'//\s*(initialize|init|create|set|get|return|import)\s+\w+',  # JS/TS
        r'#\s*TODO\s*$',  # Just "TODO" with nothing else
        r'//\s*TODO\s*$',
        r'#\s*FIXME\s*$',
        r'//\s*FIXME\s*$',
    ]
    
    for line_num, line in enumerate(lines, 1):
        if line_num not in changed_lines:
            continue
        
        for pattern in meaningless_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(Issue(
                    file=filepath,
                    line=line_num,
                    type=IssueType.MEANINGLESS_COMMENT,
                    description="Comment doesn't add value",
                    suggestion="Remove obvious comment or make it more descriptive"
                ))
                break  # Only report once per line
    
    return issues


# ============================================================================
# Rule 7: UNNECESSARY_ELSE - Else After Return
# ============================================================================

def detect_unnecessary_else(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect else clauses after return statements."""
    issues = []
    
    if language == "python":
        issues.extend(_detect_unnecessary_else_python(filepath, content, changed_lines))
    elif language in ("javascript", "typescript"):
        issues.extend(_detect_unnecessary_else_js(filepath, content, changed_lines))
    
    return issues


def _detect_unnecessary_else_python(filepath: str, content: str, changed_lines: List[int]) -> List[Issue]:
    """Detect unnecessary else in Python."""
    issues = []
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return issues
    
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Check if the if body ends with return/break/continue
            if node.body and node.orelse:
                last_stmt = node.body[-1]
                if isinstance(last_stmt, (ast.Return, ast.Break, ast.Continue)):
                    # The else line is typically one line before the first statement in orelse
                    # We'll check if the orelse statement line or the line before it is in changed lines
                    else_stmt_line = node.orelse[0].lineno
                    possible_else_lines = [else_stmt_line - 1, else_stmt_line]
                    
                    if any(line in changed_lines for line in possible_else_lines):
                        # Report on the first statement of else block
                        issues.append(Issue(
                            file=filepath,
                            line=else_stmt_line,
                            type=IssueType.UNNECESSARY_ELSE,
                            description="Unnecessary 'else' after return/break/continue",
                            suggestion="Remove 'else' and unindent the code"
                        ))
    
    return issues


def _detect_unnecessary_else_js(filepath: str, content: str, changed_lines: List[int]) -> List[Issue]:
    """Detect unnecessary else in JavaScript/TypeScript."""
    issues = []
    lines = content.splitlines()
    
    for i, line in enumerate(lines):
        line_num = i + 1
        if line_num not in changed_lines:
            continue
        
        # Simple pattern: look for "} else {" and check previous line for return
        if re.search(r'\}\s*else\s*\{', line):
            # Check if previous non-empty line has return/break/continue
            for j in range(i - 1, -1, -1):
                prev_line = lines[j].strip()
                if prev_line:
                    if re.search(r'\b(return|break|continue)\b', prev_line):
                        issues.append(Issue(
                            file=filepath,
                            line=line_num,
                            type=IssueType.UNNECESSARY_ELSE,
                            description="Unnecessary 'else' after return/break/continue",
                            suggestion="Remove 'else' and unindent the code"
                        ))
                    break
    
    return issues


# ============================================================================
# Rule 8: TODO_SPAM - Contextless TODOs
# ============================================================================

def detect_todo_spam(filepath: str, content: str, changed_lines: List[int], language: str) -> List[Issue]:
    """Detect TODO/FIXME comments without proper context."""
    issues = []
    lines = content.splitlines()
    
    # Good TODO patterns (we won't flag these):
    good_patterns = [
        r'TODO\s*\(\s*#\d+\s*\)',  # TODO(#123)
        r'TODO\s*\(\s*@\w+\s*\)',  # TODO(@username)
        r'FIXME\s*\(\s*#\d+\s*\)',
        r'FIXME\s*\(\s*@\w+\s*\)',
    ]
    
    # Bad TODO patterns (we will flag these):
    bad_patterns = [
        r'#\s*TODO\s*:?\s*$',  # Just "# TODO" with nothing else
        r'//\s*TODO\s*:?\s*$',
        r'#\s*FIXME\s*:?\s*$',
        r'//\s*FIXME\s*:?\s*$',
        r'#\s*TODO\s*:?\s*fix',  # "TODO: fix" (too vague)
        r'//\s*TODO\s*:?\s*fix',
    ]
    
    for line_num, line in enumerate(lines, 1):
        if line_num not in changed_lines:
            continue
        
        # Check if it matches a bad pattern
        is_bad = False
        for pattern in bad_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                is_bad = True
                break
        
        if is_bad:
            # Make sure it's not actually a good TODO
            is_good = False
            for pattern in good_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_good = True
                    break
            
            if not is_good:
                issues.append(Issue(
                    file=filepath,
                    line=line_num,
                    type=IssueType.TODO_SPAM,
                    description="TODO/FIXME without context or issue number",
                    suggestion="Add issue number: TODO(#123) or assignee: TODO(@username) or detailed description"
                ))
    
    return issues

