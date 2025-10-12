# MergeGuard

A Git pre-commit hook tool that detects AI-generated code patterns and prevents low-quality code from being committed.

## Overview

MergeGuard helps AI-first development teams maintain code quality by catching common issues that AI coding assistants generate before they reach code review. It analyzes staged Git files and blocks commits containing:

- 🔍 **Dead Code**: Unused imports and variables
- 🐛 **Debug Statements**: Leftover `print()` and `console.log()` calls
- 💬 **Commented Code**: Blocks of commented-out code
- 🌀 **Complexity**: Deep nesting (> 4 levels)
- 🚫 **Empty Handlers**: Empty `try/except` or `catch` blocks
- 📝 **Meaningless Comments**: Comments that don't add value
- ↩️ **Unnecessary Else**: `else` clauses after `return` statements
- ✏️ **TODO Spam**: TODOs without context or issue numbers

## Installation

### Prerequisites

- Python 3.9 or higher
- Git repository

### Install with pip

```bash
pip install merge-guard
```

### Install with pipx (recommended for CLI tools)

```bash
pipx install merge-guard
```

### Install from source

```bash
git clone https://github.com/yourusername/merge-guard.git
cd merge-guard
uv sync
uv pip install -e .
```

## Usage

### Basic Usage

MergeGuard runs as a manual check for now (Stage 1 MVP):

```bash
# Make your changes
git add .

# Check for issues before committing
merge-guard check
```

If issues are found, fix them and try again. If no issues are found, proceed with your commit:

```bash
git commit -m "Your commit message"
```

### Verbose Output

Get detailed information about the analysis:

```bash
merge-guard check --verbose
```

### Example Output

When issues are detected:

```
Analyzing 2 file(s)...

  Checking src/app.py...
  Checking src/utils.js...

✗ Merge Guard detected 3 issues in 2 files:

src/app.py
  Line 5: [DEAD_CODE]
    Unused import 'sys'
    💡 Remove this import if not needed

  Line 42: [UNUSED_DEBUG]
    Debug statement: print() statement
    💡 Remove debug statement before committing

src/utils.js
  Line 128: [COMPLEXITY]
    Nesting depth of 6 exceeds limit of 4
    💡 Consider extracting nested logic into separate functions

Fix these issues and try again.

Analyzed 2 files in 0.15s - Found 3 issues
```

When code is clean:

```
Analyzing 1 file(s)...

  Checking src/app.py...

✓ No issues detected!
Analyzed 1 file in 0.08s - All clear! ✓
```

## Supported File Types

MergeGuard currently supports:

- 🐍 **Python** (`.py`)
- 📜 **JavaScript** (`.js`, `.jsx`)
- 📘 **TypeScript** (`.ts`, `.tsx`)

## Detection Rules

### 1. DEAD_CODE - Unused Imports

Detects imports that are declared but never used:

```python
# ❌ Bad
import sys  # Unused
import os

print(os.getcwd())
```

```python
# ✅ Good
import os

print(os.getcwd())
```

### 2. UNUSED_DEBUG - Debug Statements

Catches leftover debug statements:

```python
# ❌ Bad
def calculate(x):
    print("Debug:", x)  # Should be removed
    return x * 2
```

```javascript
// ❌ Bad
function calculate(x) {
  console.log("Debug:", x); // Should be removed
  debugger;
  return x * 2;
}
```

### 3. COMMENTED_CODE - Commented Code Blocks

Flags 3+ consecutive lines of commented-out code:

```python
# ❌ Bad
def process():
    # old_value = x * 2
    # result = old_value + 10
    # return result
    return x
```

### 4. COMPLEXITY - Deep Nesting

Detects nesting depth exceeding 4 levels:

```python
# ❌ Bad
if a:
    if b:
        if c:
            if d:
                if e:  # Too deep!
                    return "nested"
```

### 5. EMPTY_HANDLERS - Empty Exception Blocks

Catches empty try/except or try/catch blocks:

```python
# ❌ Bad
try:
    risky_operation()
except:
    pass  # Should at least log
```

### 6. MEANINGLESS_COMMENT - Obvious Comments

Flags comments that just restate the code:

```python
# ❌ Bad
# Initialize variable x
x = 10
```

```python
# ✅ Good
# Default timeout in seconds for API requests
x = 10
```

### 7. UNNECESSARY_ELSE - Else After Return

Detects unnecessary else clauses:

```python
# ❌ Bad
if condition:
    return "yes"
else:  # Unnecessary
    return "no"
```

```python
# ✅ Good
if condition:
    return "yes"
return "no"
```

### 8. TODO_SPAM - Contextless TODOs

Flags TODOs without proper context:

```python
# ❌ Bad
# TODO: fix this
```

```python
# ✅ Good
# TODO(#123): Refactor to use new authentication API
# TODO(@username): Handle edge case for empty arrays
```

## Configuration

Currently, MergeGuard uses default rules (Stage 1 MVP). Configuration options will be added in future versions.

## Exit Codes

- `0` - No issues detected, commit can proceed
- `1` - Issues detected, commit should be blocked

## Coming Soon

### Stage 2: Local LLM Integration

- Replace rule-based detection with local LLM (DeepSeek/Llama)
- Smarter detection of AI-generated patterns
- Issue-by-issue streaming

### Stage 3: Pre-commit Hook Installation

- `merge-guard install` - Automatic hook installation
- Runs automatically on every commit
- `merge-guard uninstall` - Remove hook

### Stage 4: Override Mechanism

- Mark false positives
- Store overrides locally
- Skip known good patterns

### Stage 5: Full File Context

- Intelligent chunking for large files
- Better dead code detection with full context

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/merge-guard.git
cd merge-guard

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Run tests
uv run pytest tests/ -v
```

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=merge_guard tests/

# Specific test file
uv run pytest tests/test_detector.py -v
```

### Project Structure

```
merge-guard-cli/
├── src/merge_guard/
│   ├── __init__.py
│   ├── cli.py              # CLI commands
│   ├── detector.py         # Detection rules
│   ├── formatters.py       # Output formatting
│   ├── git_utils.py        # Git operations
│   └── models.py           # Data models
├── tests/
│   ├── fixtures/           # Sample files
│   ├── test_detector.py    # Detector tests
│   └── test_git_utils.py   # Git utility tests
├── pyproject.toml          # Project config
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

**Proprietary License** - This software is proprietary and confidential.

- **Personal/Evaluation Use**: Free for evaluation and personal projects
- **Commercial Use**: Requires a commercial license
- **Source Code**: Not open source - all rights reserved

For commercial licensing inquiries, contact: ashtilawat23@gmail.com

See LICENSE file for full terms and conditions.

## Credits

Built for AI-first development teams who embrace coding agents but want to maintain code quality.

---

**Current Version**: 0.1.0 (Stage 1 MVP)

**Status**: ✅ Rule-based detection working | 🚧 LLM integration coming in Stage 2
