# Breadcrumb AI Tracer

**Zero-config Python execution tracer for AI agents**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Breadcrumb is an AI-native execution tracer that automatically captures Python code execution and makes it queryable through the Model Context Protocol (MCP). It enables AI agents like Claude Code to understand what your code is doing, find exceptions, analyze performance, and debug issues without manual instrumentation.

## Why Breadcrumb?

Traditional debugging tools are built for humans. AI agents need structured, queryable execution data. Breadcrumb provides:

- **Zero-config tracing**: Just `import breadcrumb; breadcrumb.init()` - no manual instrumentation
- **AI-native interface**: MCP server with tools optimized for AI agents
- **Automatic secret redaction**: Prevents logging of passwords, API keys, tokens, credit cards
- **SQL-queryable traces**: Full power of SQL over your execution data
- **Low overhead**: < 5% performance impact with intelligent sampling
- **Selective instrumentation**: Control what gets traced with glob patterns

## Features

- **MCP Server Integration**: 4 specialized tools for AI agents (query_traces, get_trace, find_exceptions, analyze_performance)
- **CLI Tools**: 6 commands for quick trace analysis (list, get, query, exceptions, performance, serve-mcp)
- **PEP 669 Backend**: Python 3.12+ low-overhead monitoring API
- **sys.settrace Backend**: Fallback for older Python versions
- **Secret Redaction**: Automatic detection of 50+ sensitive patterns
- **DuckDB Storage**: Fast, embedded columnar database for trace data
- **Async Writing**: Non-blocking trace persistence
- **Value Truncation**: Automatic size limits prevent database bloat
- **Schema Migrations**: Automatic database upgrades

## 🤖 AI-FIRST Design Philosophy

**Breadcrumb is designed for AI agents, not humans.**

Traditional dev tools optimize for human convenience (implicit defaults, "smart" context inference). AI agents need **explicit, unambiguous commands** with zero hidden state.

### The AI-FIRST Principle

> **"It's only clunky for humans! AI agents have no issues with writing `-c` after each command."**

**Why `-c PROJECT` is REQUIRED everywhere:**
- ❌ **Human UX**: "Ugh, typing `-c myproject` every time?"
- ✅ **AI Agent UX**: "Perfect! No ambiguity, no context confusion!"

**Explicit > Implicit for AI workflows:**
- Humans hate repetition → AI agents don't care
- Humans want smart defaults → AI agents want zero surprises
- Humans tolerate ambiguity → AI agents need clarity

This is why `breadcrumb` commands **require** `-c PROJECT` for all operations that need database/config context. No hidden "current project", no implicit defaults, no context confusion.

### The AI-FIRST Workflow

**1️⃣ One-time initialization:**
```bash
breadcrumb init myproject
# Creates ~/.breadcrumb/myproject.yaml with sensible defaults
# Creates ~/.breadcrumb/myproject-traces.duckdb for traces
```

**2️⃣ Explicit execution (always with -c):**
```bash
breadcrumb run -c myproject --timeout 60 python script.py
# Explicit which project/database - zero ambiguity!
```

**3️⃣ Explicit queries (always with -c):**
```bash
breadcrumb query -c myproject --gaps
# Explicit which database to query - no guessing!
```

**4️⃣ Explicit config changes (always with name):**
```bash
breadcrumb config edit myproject --add-include 'mymodule.*'
# Explicit which config to edit - zero confusion!
```

**This eliminates:**
- ❌ "Which database am I querying?"
- ❌ "Which config is active?"
- ❌ "Where did my traces go?"
- ❌ "Why is it tracing the wrong code?"

**Result:** AI agents execute workflows with 100% reliability, no context loss between sessions.

---

## Quick Start

### 1. Installation

```bash
# Using uv (recommended)
cd breadcrumb
uv pip install -e .

# Or using pip
pip install -e breadcrumb/
```

### 2. AI-FIRST Workflow (Recommended)

**Step 1: Initialize a project**
```bash
breadcrumb init myproject
# ✅ Creates config: ~/.breadcrumb/myproject.yaml
# ✅ Sets up database: ~/.breadcrumb/myproject-traces.duckdb
```

**Step 2: Run with tracing (explicit -c required!)**
```bash
breadcrumb run -c myproject --timeout 60 python script.py
# ✅ Explicit project = zero ambiguity
# ✅ Traces saved to myproject-traces.duckdb
```

**Step 3: Find gaps in tracing**
```bash
breadcrumb query -c myproject --gaps
# ✅ Shows which functions were called but not traced
# ✅ Suggests include patterns to expand coverage
```

**Step 4: Expand tracing iteratively**
```bash
breadcrumb config edit myproject --add-include 'mymodule.*'
# ✅ Add modules based on --gaps suggestions
```

**Step 5: Re-run with expanded tracing**
```bash
breadcrumb run -c myproject --timeout 60 python script.py
# ✅ Now traces mymodule.* functions too!
```

**Step 6: Query function details**
```bash
breadcrumb query -c myproject --call my_function
# ✅ Shows args, return values, duration, callers/callees
```

### 3. Classic Workflow (Python API)

Add to your Python code:

```python
import breadcrumb
breadcrumb.init()

# Your code here
def calculate(x, y):
    return x + y

result = calculate(10, 20)
```

Run your code:

```bash
python your_script.py
```

Traces are automatically saved to `.breadcrumb/traces.duckdb`.

### 4. Query Traces

Using AI agents (Claude Desktop with MCP):

```
Tell Claude: "Use breadcrumb to find the last exception"
Claude will use: breadcrumb__find_exceptions
```

Using CLI:

```bash
# Smart queries (no SQL needed!) - AI-FIRST workflow
breadcrumb query -c myproject --gaps          # Show untraced calls
breadcrumb query -c myproject --call Pizza    # Show function details
breadcrumb query -c myproject --flow          # Show execution timeline

# List recent traces
breadcrumb list -c myproject

# Find exceptions in last hour
breadcrumb exceptions -c myproject --since 1h

# Analyze function performance
breadcrumb performance -c myproject calculate

# Execute custom SQL query (still supported!)
breadcrumb query -c myproject --sql "SELECT * FROM traces WHERE status='failed'"
```

## MCP Server Setup (Claude Desktop)

1. Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "breadcrumb": {
      "command": "breadcrumb",
      "args": ["serve-mcp"],
      "env": {}
    }
  }
}
```

2. Restart Claude Desktop

3. Ask Claude to use Breadcrumb tools:
   - "Find recent exceptions using breadcrumb"
   - "Analyze performance of function X"
   - "Show me the last 10 traces"

## Configuration

### Python API

```python
import breadcrumb

# Basic configuration
breadcrumb.init(
    enabled=True,           # Enable/disable tracing
    sample_rate=1.0,        # Trace 100% of calls
    db_path=".breadcrumb/traces.duckdb"
)

# Selective instrumentation (include-only workflow)
breadcrumb.init(
    include=["src/**/*.py"],     # Only trace src/ directory
)

# Custom backend
breadcrumb.init(
    backend="pep669"   # Use PEP 669 (Python 3.12+)
    # backend="sqlite" # Use sys.settrace (default)
)
```

### Environment Variables

```bash
# Enable/disable tracing
export BREADCRUMB_ENABLED=true

# Custom database path
export BREADCRUMB_DB_PATH="/path/to/traces.duckdb"

# Sample rate (0.0 to 1.0)
export BREADCRUMB_SAMPLE_RATE=0.5
```

## CLI Reference

### Global Options

```bash
--format json|table    # Output format (default: json for AI agents)
--db-path PATH         # Custom database path (auto-discovered)
--verbose              # Enable verbose output
--version              # Show version
```

### Commands

```bash
# List recent traces
breadcrumb list [--limit 10]

# Get trace by ID
breadcrumb get <trace-id>

# Smart queries (semantic, no SQL needed)
breadcrumb query --gaps                    # Show untraced calls
breadcrumb query --call <function-name>    # Show function I/O
breadcrumb query --flow                    # Show execution timeline
breadcrumb query --flow --module <name>    # Filter by module

# Execute SQL query (still supported)
breadcrumb query "SELECT * FROM traces"

# Find exceptions
breadcrumb exceptions [--since 1h] [--limit 10]

# Analyze performance
breadcrumb performance <function-name> [--limit 10]

# Start MCP server
breadcrumb serve-mcp [--db-path PATH]
```

## MCP Tools for AI Agents

### breadcrumb__query_traces

Execute SQL queries against trace database:

```sql
SELECT * FROM traces WHERE status='failed' LIMIT 10
SELECT function_name, COUNT(*) FROM trace_events GROUP BY function_name
```

### breadcrumb__get_trace

Get complete trace details by ID:

```
breadcrumb__get_trace(trace_id="123e4567-e89b-12d3-a456-426614174000")
```

### breadcrumb__find_exceptions

Find exceptions in time range:

```
breadcrumb__find_exceptions(since="1h", limit=10)
breadcrumb__find_exceptions(since="2025-01-10", limit=5)
```

### breadcrumb__analyze_performance

Analyze function performance:

```
breadcrumb__analyze_performance(function="process_data", limit=10)
```

## Secret Redaction

Breadcrumb automatically redacts sensitive data before storage:

**Detected patterns:**
- Passwords (`password`, `passwd`, `secret`)
- API keys (`api_key`, `token`, `bearer`)
- Credit cards (16 digits with dashes/spaces)
- SSNs (XXX-XX-XXXX format)
- JWTs (eyJ... format)
- AWS keys (AKIA...)
- GitHub tokens (ghp_...)

**Example:**

```python
data = {
    "username": "alice",
    "password": "secret123",
    "api_key": "sk-1234567890"
}
# Stored as:
# {"username": "alice", "password": "[REDACTED]", "api_key": "[REDACTED]"}
```

Configure custom patterns:

```python
from breadcrumb.capture.secret_redactor import configure_redactor

configure_redactor(custom_patterns=['my_secret_*'])
```

## Database Schema

Breadcrumb stores traces in DuckDB with three main tables:

**traces**: One row per execution
- `trace_id`, `status`, `started_at`, `finished_at`, `duration_ms`

**trace_events**: Function calls and returns
- `trace_id`, `event_type`, `function_name`, `args`, `return_value`

**exceptions**: Caught exceptions
- `trace_id`, `exception_type`, `exception_message`, `stack_trace`

Direct SQL access:

```python
import duckdb
conn = duckdb.connect('.breadcrumb/traces.duckdb')
result = conn.execute("SELECT * FROM traces").fetchall()
```

## Examples

See the `examples/` directory for complete examples:

- `basic_trace_example.py` - Getting started
- `selective_instrumentation_demo.py` - Control what gets traced
- `secret_redaction_demo.py` - Security features
- `config_demo.py` - Configuration options
- `phase2_storage_demo.py` - Storage layer examples

## Performance

Breadcrumb is designed for low overhead:

- **PEP 669 backend**: < 2% overhead on Python 3.12+
- **sys.settrace backend**: < 5% overhead on older versions
- **Async writing**: Trace writes don't block execution
- **Sampling**: Reduce overhead with `sample_rate < 1.0`
- **Selective instrumentation**: Only trace what you need

Benchmark results on 1M function calls:
- Baseline: 0.85s
- With Breadcrumb (PEP 669): 0.87s (2.4% overhead)
- With Breadcrumb (settrace): 0.89s (4.7% overhead)

## Documentation

- [QUICKSTART.md](docs/QUICKSTART.md) - Quick start guide for AI agents
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Complete API documentation
- [SECURITY.md](docs/SECURITY.md) - Security and privacy documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

## Architecture

Breadcrumb is built in phases:

- **Phase 0-1**: Core instrumentation (PEP 669 and sys.settrace backends)
- **Phase 2**: Storage layer (DuckDB with async writes)
- **Phase 3**: MCP server (FastMCP integration)
- **Phase 4**: CLI tools (Typer-based commands)
- **Phase 5**: Security and polish (secret redaction, documentation)

## Requirements

- Python 3.12+ (recommended for PEP 669 backend)
- Python 3.8+ (fallback to sys.settrace backend)
- DuckDB 1.4.1+
- FastMCP 2.12.4+

## License

MIT License - see LICENSE file for details

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Testing guidelines
- Code style requirements
- Pull request process

## Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory

## Status

Current version: **0.1.0 (Beta)**

Breadcrumb is in active development. API may change in minor versions.
Production-ready features:
- Core tracing (PEP 669 and sys.settrace)
- Storage layer (DuckDB)
- MCP server (4 tools)
- CLI tools (6 commands)
- Secret redaction

Coming soon:
- PyPI package
- Performance visualizations
- Distributed tracing
- Cloud storage backends

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [DuckDB](https://duckdb.org/) - Embedded analytical database
- [Typer](https://typer.tiangolo.com/) - CLI framework

Special thanks to the Model Context Protocol team at Anthropic for enabling AI-native tooling.
