# Contributing to Breadcrumb AI Tracer

Thank you for your interest in contributing to Breadcrumb! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Getting Help](#getting-help)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and constructive in discussions
- Accept constructive criticism gracefully
- Focus on what's best for the project and community
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Other conduct considered inappropriate

### Reporting

If you experience or witness unacceptable behavior, please report it by contacting the project maintainers.

---

## Getting Started

### Prerequisites

- **Python 3.12+** (recommended for PEP 669 support)
- **Python 3.8+** (minimum for sys.settrace backend)
- **uv** (recommended for dependency management)
- **Git** for version control

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/breadcrumb.git
cd breadcrumb

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd breadcrumb
uv pip install -e .
uv pip install -e ".[dev]"

# Run tests
pytest

# Verify installation
breadcrumb --version
```

---

## Development Setup

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/your-org/breadcrumb.git
cd breadcrumb/breadcrumb

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
uv pip install -e ".[dev]"
```

### 2. Verify Setup

```bash
# Run tests
pytest

# Check code style
ruff check .

# Run type checker
mypy src/breadcrumb

# Verify CLI works
breadcrumb --version
```

### 3. IDE Setup

**VS Code:**

Install recommended extensions:
- Python
- Pylance
- Ruff

Workspace settings (`.vscode/settings.json`):

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true
}
```

**PyCharm:**

- Enable type checking: Preferences → Editor → Inspections → Python → Type Checker
- Set Black as formatter: Preferences → Tools → Black
- Enable pytest: Preferences → Tools → Python Integrated Tools → Testing → pytest

---

## Project Architecture

Breadcrumb is built in phases, each building on the previous:

### Phase 0-1: Core Instrumentation

**Location:** `src/breadcrumb/instrumentation/`

**Purpose:** Capture execution events

**Components:**
- `pep669_backend.py`: Python 3.12+ low-overhead monitoring
- `settrace_backend.py`: Fallback for older Python versions

**Key concepts:**
- Event-driven architecture
- Minimal overhead (< 5%)
- Selective instrumentation via glob patterns

### Phase 2: Storage Layer

**Location:** `src/breadcrumb/storage/`

**Purpose:** Persist and query trace data

**Components:**
- `connection.py`: DuckDB connection management
- `async_writer.py`: Non-blocking writes
- `query.py`: Safe query API with SQL injection prevention
- `retention.py`: Data cleanup policies
- `migrations/`: Schema versioning

**Key concepts:**
- DuckDB columnar storage
- Async writes for performance
- Automatic schema migrations

### Phase 3: MCP Server

**Location:** `src/breadcrumb/mcp/`

**Purpose:** Expose traces to AI agents via Model Context Protocol

**Components:**
- `server.py`: FastMCP server with 4 tools

**Key concepts:**
- AI-native interface
- JSON responses
- Read-only access for safety

### Phase 4: CLI Tools

**Location:** `src/breadcrumb/cli/`

**Purpose:** Command-line interface for humans

**Components:**
- `main.py`: Typer-based CLI
- `commands/`: Individual command implementations
- `formatters.py`: JSON and table output

**Key concepts:**
- Human and AI friendly
- Consistent exit codes
- Rich error messages

### Phase 5: Security and Polish

**Location:** `src/breadcrumb/capture/`

**Purpose:** Secret redaction and data privacy

**Components:**
- `secret_redactor.py`: Automatic secret detection and redaction
- `value_truncation.py`: Size limits for database

**Key concepts:**
- Defense in depth
- Zero-config security
- Configurable policies

### Directory Structure

```
breadcrumb/
├── src/
│   └── breadcrumb/
│       ├── __init__.py           # Public API
│       ├── config.py             # Configuration system
│       ├── instrumentation/      # Phase 1: Tracing backends
│       ├── storage/              # Phase 2: Database layer
│       ├── mcp/                  # Phase 3: MCP server
│       ├── cli/                  # Phase 4: CLI tools
│       └── capture/              # Phase 5: Security
├── tests/                        # All tests
│   ├── instrumentation/
│   ├── storage/
│   ├── test_mcp/
│   ├── cli/
│   ├── capture/
│   └── performance/
├── examples/                     # Example scripts
├── docs/                         # Documentation
├── pyproject.toml               # Package configuration
└── README.md                    # Main documentation
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Create feature branch from main
git checkout -b feature/your-feature-name

# Or bugfix branch
git checkout -b fix/bug-description
```

**Branch naming:**
- `feature/`: New features
- `fix/`: Bug fixes
- `docs/`: Documentation changes
- `refactor/`: Code refactoring
- `test/`: Test improvements
- `perf/`: Performance improvements

### 2. Make Changes

**Write tests first** (TDD approach):

```python
# tests/storage/test_new_feature.py
def test_new_feature():
    """Test description."""
    # Arrange
    setup_data = ...

    # Act
    result = new_feature(setup_data)

    # Assert
    assert result == expected_value
```

**Implement feature:**

```python
# src/breadcrumb/storage/new_feature.py
def new_feature(data):
    """
    Docstring explaining what this does.

    Args:
        data: Input data

    Returns:
        Processed result
    """
    # Implementation
    return result
```

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/storage/test_new_feature.py

# Run with coverage
pytest --cov=breadcrumb --cov-report=html

# Run specific test
pytest tests/storage/test_new_feature.py::test_new_feature
```

### 4. Check Code Style

```bash
# Check style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
black src/ tests/

# Type checking
mypy src/breadcrumb
```

### 5. Update Documentation

If your change affects the API:

- Update docstrings
- Update `docs/API_REFERENCE.md`
- Add examples to `examples/`
- Update `README.md` if needed

### 6. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add new query optimization feature

- Implement query caching layer
- Add cache invalidation logic
- Update documentation
- Add tests for cache behavior

Closes #123"
```

**Commit message format:**

```
<type>: <summary>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Example:**

```
feat: Add query caching for performance

Implement LRU cache for frequently executed queries to reduce
database load. Cache size is configurable via config option.

- Add cache.py module
- Update query.py to use cache
- Add cache_size config parameter
- Add tests for cache behavior
- Update API_REFERENCE.md

Closes #123
```

### 7. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

---

## Testing

### Test Organization

Tests are organized by component:

```
tests/
├── instrumentation/     # Phase 1 tests
├── storage/            # Phase 2 tests
├── test_mcp/           # Phase 3 tests
├── cli/                # Phase 4 tests
├── capture/            # Phase 5 tests
└── performance/        # Performance benchmarks
```

### Running Tests

```bash
# All tests
pytest

# Specific directory
pytest tests/storage/

# Specific file
pytest tests/storage/test_query.py

# Specific test
pytest tests/storage/test_query.py::test_query_traces

# With coverage
pytest --cov=breadcrumb --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Test Coverage Requirements

- **Minimum coverage:** 80% for new code
- **Critical paths:** 100% coverage (security, query layer)
- **Exceptions:** Integration tests, performance tests

### Writing Good Tests

**Structure:**

```python
def test_feature_name():
    """Test that feature works in normal case."""
    # Arrange: Set up test data
    input_data = {"key": "value"}

    # Act: Execute the feature
    result = my_function(input_data)

    # Assert: Verify the result
    assert result == expected_value
```

**Test names:**

- Start with `test_`
- Describe what you're testing
- Be specific: `test_query_with_invalid_sql_raises_error`

**Good practices:**

- One assertion per test (when possible)
- Test edge cases (empty input, None, large values)
- Test error conditions
- Use fixtures for setup
- Mock external dependencies

**Example:**

```python
import pytest
from breadcrumb.storage.query import query_traces, InvalidQueryError

def test_query_traces_with_select_succeeds():
    """Test that SELECT queries work."""
    result = query_traces("SELECT * FROM traces LIMIT 1")
    assert isinstance(result, list)

def test_query_traces_with_update_raises_error():
    """Test that UPDATE queries are rejected."""
    with pytest.raises(InvalidQueryError):
        query_traces("UPDATE traces SET status='hacked'")

def test_query_traces_with_empty_result_returns_empty_list():
    """Test that queries with no results return empty list."""
    result = query_traces("SELECT * FROM traces WHERE id='nonexistent'")
    assert result == []
```

### Performance Tests

Located in `tests/performance/`, these benchmark critical paths:

```bash
# Run performance tests
pytest tests/performance/ -v

# With profiling
pytest tests/performance/ --profile
```

**Benchmark requirements:**
- PEP 669 backend: < 2% overhead
- sys.settrace backend: < 5% overhead
- Query performance: < 100ms for typical queries

---

## Code Style

### Python Style Guide

We follow **PEP 8** with some adjustments:

**Line length:** 100 characters (not 79)

**Tools:**
- **Ruff:** Linting and auto-fixing
- **Black:** Code formatting
- **MyPy:** Type checking

### Formatting

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

**Black configuration** (pyproject.toml):

```toml
[tool.black]
line-length = 100
target-version = ['py312']
```

### Linting

```bash
# Lint code
ruff check .

# Auto-fix issues
ruff check --fix .
```

**Ruff configuration** (pyproject.toml):

```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N"]
ignore = ["E501"]  # Line length (handled by Black)
```

### Type Hints

**All public APIs must have type hints:**

```python
from typing import List, Dict, Optional, Any

def query_traces(
    sql: str,
    params: Optional[List[Any]] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Execute SQL query."""
    ...
```

**Type checking:**

```bash
# Check types
mypy src/breadcrumb

# Strict mode
mypy --strict src/breadcrumb
```

### Docstrings

Use **Google style** docstrings:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """
    Brief one-line description.

    Longer description if needed. Explain what the function does,
    not how it does it.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When arg2 is negative
        TypeError: When arg1 is not a string

    Examples:
        >>> function_name("test", 42)
        True

        >>> function_name("", -1)
        ValueError: arg2 must be positive
    """
    if arg2 < 0:
        raise ValueError("arg2 must be positive")

    return len(arg1) > arg2
```

### Import Order

Organized into groups:

```python
# 1. Standard library
import os
import sys
from typing import List, Optional

# 2. Third-party
import duckdb
from fastmcp import FastMCP

# 3. Local imports
from breadcrumb.config import get_config
from breadcrumb.storage.query import query_traces
```

---

## Pull Request Process

### Before Submitting

**Checklist:**

- [ ] Tests pass: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Linting passes: `ruff check .`
- [ ] Type checking passes: `mypy src/breadcrumb`
- [ ] Documentation updated (if needed)
- [ ] Examples added (for new features)
- [ ] CHANGELOG updated (for significant changes)

### PR Description

Use this template:

```markdown
## Summary
Brief description of what this PR does.

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- List of changes made
- Each on its own line

## Testing
How did you test this? What test cases did you add?

## Documentation
What documentation did you update?

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Linting passes
- [ ] Documentation updated
- [ ] Examples added (if applicable)

## Related Issues
Closes #123
Fixes #456
```

### Review Process

1. **Automated checks:** CI runs tests, linting, type checking
2. **Code review:** Maintainer reviews code
3. **Feedback:** Address review comments
4. **Approval:** Maintainer approves PR
5. **Merge:** Maintainer merges PR

**Response time:**
- Initial review: Within 3-5 business days
- Follow-up reviews: Within 2 business days

### After Merge

- Your branch will be deleted
- Changes will be in the main branch
- CHANGELOG will be updated
- Next release will include your changes

---

## Documentation

### When to Update Docs

Update documentation when you:

- Add new public API
- Change existing API
- Add new CLI command
- Change behavior
- Fix significant bug

### Documentation Files

**README.md:** Overview and quick start
- Update for major features
- Keep examples up to date

**docs/API_REFERENCE.md:** Complete API docs
- Add new functions/classes
- Update signatures
- Add examples

**docs/QUICKSTART.md:** For AI agents
- Update for new MCP tools
- Add common use cases

**docs/SECURITY.md:** Security documentation
- Update for security features
- Add best practices

**CONTRIBUTING.md:** This file
- Update for process changes

### Docstring Style

Follow Google style (see [Code Style](#code-style) section).

### Examples

Add runnable examples to `examples/`:

```python
# examples/new_feature_demo.py
"""
Demonstration of new feature.

This example shows how to use the new feature in a real scenario.
"""

import breadcrumb

# Initialize
breadcrumb.init()

# Use new feature
result = breadcrumb.new_feature()

print(f"Result: {result}")
```

---

## Getting Help

### Resources

- **Documentation:** See `docs/` directory
- **Examples:** See `examples/` directory
- **Issues:** GitHub Issues for bugs and features
- **Discussions:** GitHub Discussions for questions

### Questions?

**Before asking:**

1. Check existing documentation
2. Search closed issues
3. Read FAQ (if available)

**When asking:**

- Be specific
- Provide context
- Include code samples
- Mention your environment (OS, Python version)

**Where to ask:**

- **General questions:** GitHub Discussions
- **Bug reports:** GitHub Issues
- **Feature requests:** GitHub Issues
- **Security issues:** See SECURITY.md

### Community

- **Be patient:** Maintainers are volunteers
- **Be respectful:** Follow code of conduct
- **Be helpful:** Help others when you can
- **Give back:** Contribute code, docs, examples

---

## Development Tips

### Working with uv

```bash
# Install dependency
uv pip install package-name

# Update dependency
uv pip install --upgrade package-name

# Install dev dependencies
uv pip install -e ".[dev]"
```

### Debugging Tests

```bash
# Run with print output
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run specific test with verbose output
pytest -v tests/storage/test_query.py::test_specific_case
```

### Performance Profiling

```bash
# Profile a script
python -m cProfile -o profile.out examples/script.py

# Analyze profile
python -m pstats profile.out
```

### Database Inspection

```bash
# Open database in DuckDB CLI
duckdb .breadcrumb/traces.duckdb

# Run queries
SELECT * FROM traces;
```

---

## Release Process

(For maintainers)

### Versioning

We use **Semantic Versioning**:

- **Major (1.0.0):** Breaking changes
- **Minor (0.1.0):** New features, backward compatible
- **Patch (0.0.1):** Bug fixes

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `__version__` in `src/breadcrumb/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Build package: `python -m build`
- [ ] Test installation: `pip install dist/*.whl`
- [ ] Create git tag: `git tag v0.1.0`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Create GitHub release
- [ ] Publish to PyPI: `twine upload dist/*`

---

## Thank You!

Thank you for contributing to Breadcrumb! Your contributions help make AI-native debugging better for everyone.

**Happy coding!**
