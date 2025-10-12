# Breadcrumb AI Tracer - Current Capabilities Analysis

**Document Purpose**: Complete inventory of breadcrumb's current capabilities, features, and user interfaces as implemented in the codebase.

**Analysis Date**: 2025-10-11
**Version**: Based on commit a7a2967 (Phase 3 complete - 13/13 tests passing)

---

## Executive Summary

Breadcrumb is a zero-config Python execution tracer designed for AI agents and developers. It automatically captures function calls, arguments, returns, and exceptions in Python applications, storing them in a queryable DuckDB database. The system supports both high-performance PEP 669 instrumentation (Python 3.12+) and legacy sys.settrace fallback (Python 3.10-3.11).

**Core Value Proposition**: Enable AI agents and developers to understand code execution without manual instrumentation by providing structured, queryable trace data through both MCP tools and CLI commands.

**Architecture**: Event-driven with three layers:
1. **Instrumentation Layer**: PEP 669 or sys.settrace backend captures events
2. **Integration Layer**: Connects backend to storage via event callbacks
3. **Storage Layer**: Async writer with batching persists to DuckDB

---

## 1. Core Capabilities

### 1.1 Tracing Capabilities

#### What Breadcrumb Traces

**Function-Level Events**:
- **Call events**: Function entry with arguments (positional + keyword)
- **Return events**: Function exit with return values
- **Exception events**: Exceptions raised with type, message, and stack trace
- **Line events**: Line-by-line execution (optional, disabled by default due to overhead)

**Captured Metadata Per Event**:
- Timestamp (datetime with microsecond precision)
- Thread ID (supports multi-threaded applications)
- Function name (with class name for methods: `ClassName.method_name`)
- Module name (e.g., `myapp.utils`)
- File path (absolute path to source file)
- Line number (current execution line)
- Async context flag (detects async/await functions)

**Argument and Variable Capture**:
- Positional arguments (captured as dict: `{arg_name: value}`)
- Keyword arguments (captured separately)
- Return values (with safe repr for complex objects)
- Local variables (optional, expensive, disabled by default)
- Value truncation at 200 characters per value (configurable)
- Automatic secret redaction for sensitive data

**Exception Tracking**:
- Exception type (class name, e.g., `ValueError`)
- Exception message (str representation)
- Full stack trace (formatted traceback)
- Source location (file path and line number)

#### What Breadcrumb Does NOT Trace

**Explicitly Excluded**:
- Breadcrumb's own internal code (prevents recursion)
- Python standard library by default (threading, queue, os, sys, etc.)
- Common framework internals (asyncio, importlib, typing, dataclasses)
- Files in `.venv` directories (virtual environments)

**Not Captured**:
- Memory allocations or garbage collection
- CPU profiling data
- Network traffic details
- File I/O operations (unless explicitly in traced code)
- System calls
- C extension internals

### 1.2 Backend Implementations

#### PEP 669 Backend (Python 3.12+)

**Technical Details**:
- Uses `sys.monitoring` API introduced in PEP 669
- Tool ID 0 for third-party tool registration
- Event types: `PY_START`, `PY_RETURN`, `RAISE`, `LINE` (optional)
- Thread-safe with `threading.local()` storage
- Low overhead: ~2% performance impact

**Features**:
- Instrumentation-time filtering (events filtered before capture)
- Smart auto-filtering for hot loops (threshold: 100 calls/10 seconds)
- Workspace-aware filtering (only trace user code, not site-packages)
- Async function detection via code flags (`CO_COROUTINE`, `CO_ASYNC_GENERATOR`)
- Automatic class method name resolution (`ClassName.__init__`)

**Performance Optimizations**:
- Max 10,000 events per thread (prevents memory issues)
- Event callback integration (bypass local storage when writer active)
- Pattern-based exclusion at instrumentation time
- Path-based filtering (stdlib, site-packages, .venv detection)

**Implementation Location**: `breadcrumb/src/breadcrumb/instrumentation/pep669_backend.py` (813 lines)

#### sys.settrace Backend (Python 3.10-3.11)

**Technical Details**:
- Uses legacy `sys.settrace()` API
- Thread-local context with `threading.local()`
- Event types: `call`, `return`, `line`, `exception`
- Performance overhead: ~2000%+ (shows warning on first use)

**Features**:
- Same filtering patterns as PEP 669 backend
- Same data capture capabilities
- Fallback for older Python versions
- Overhead warning displayed on initialization

**Limitations**:
- Significantly higher overhead than PEP 669
- Must be set per-thread (not automatic across threads)
- Less efficient for high-frequency tracing
- Not recommended for production use

**Implementation Location**: `breadcrumb/src/breadcrumb/instrumentation/settrace_backend.py` (383 lines)

### 1.3 Storage and Persistence

#### DuckDB Database

**Schema Design**:

**traces** table:
- `id` (UUID): Unique trace identifier
- `started_at` (TIMESTAMP): Trace start time
- `ended_at` (TIMESTAMP): Trace end time (NULL for running traces)
- `status` (VARCHAR): 'running', 'completed', 'failed'
- `thread_id` (BIGINT): OS thread identifier
- `metadata` (JSON): Optional trace metadata

**trace_events** table:
- `id` (UUID): Unique event identifier
- `trace_id` (UUID): Foreign key to traces table
- `timestamp` (TIMESTAMP): Event timestamp
- `event_type` (VARCHAR): 'call', 'return', 'line', 'exception'
- `function_name` (VARCHAR): Function name
- `module_name` (VARCHAR): Module name
- `file_path` (VARCHAR): Source file path
- `line_number` (INTEGER): Line number
- `data` (JSON): Event data (args, kwargs, return_value, etc.)
- `created_at` (TIMESTAMP): Database insertion time

**exceptions** table:
- `id` (UUID): Unique exception identifier
- `event_id` (UUID): Foreign key to trace_events table
- `trace_id` (UUID): Foreign key to traces table
- `exception_type` (VARCHAR): Exception class name
- `message` (TEXT): Exception message
- `stack_trace` (TEXT): Full stack trace
- `created_at` (TIMESTAMP): Database insertion time

**Indexes**:
- `traces.started_at` (for time-range queries)
- `trace_events.trace_id` (for event lookups)
- `trace_events.event_type` (for filtering by event type)
- `exceptions.trace_id` (for exception lookups)

**Database Location**:
- Default: `~/.breadcrumb/traces.duckdb`
- Workspace: `.breadcrumb/traces.duckdb` (if initialized in project)
- Custom: Configurable via `db_path` parameter

#### Async Writer with Batching

**Architecture**:
- Background thread: `breadcrumb-writer` daemon thread
- Queue-based: Events queued for async writing
- Batch writes: Accumulates up to 100 events or 100ms, then bulk INSERT
- Backpressure handling: Queue size limit of 10,000 events

**Performance Features**:
- Bulk INSERT with `executemany()` for efficiency
- Grouped by event type (traces, trace_events, exceptions)
- Transaction batching reduces database locks
- Non-blocking: Instrumentation never waits for I/O

**Backpressure Mechanism**:
- Queue full: Drop events with warning (log every 100 dropped)
- Track dropped functions for diagnostics
- Auto-stop after 3 queue overflow warnings
- Generate diagnostic report on auto-stop

**Shutdown Handling**:
- `atexit` hook for graceful shutdown
- Flush remaining events (5 second timeout)
- Update running traces to 'completed'
- Connection pool cleanup

**Implementation Location**: `breadcrumb/src/breadcrumb/storage/async_writer.py` (621 lines)

### 1.4 Smart Auto-Filtering

**Call Tracker System**:
- Monitors call frequency per function
- Default threshold: 100 calls within 10 seconds
- Automatically filters hot loops after threshold exceeded
- Reset interval: 60 seconds (allows re-sampling)

**Behavior**:
1. First 100 calls to a function are always captured
2. After threshold exceeded, subsequent calls are filtered
3. Filters reset every 60 seconds to detect behavioral changes
4. Truncation metadata logged for transparency

**Diagnostic Information**:
- Which functions were filtered
- How many calls were dropped per function
- Reason for filtering (always `auto_filter_hot_loop`)
- First truncation timestamp

**Use Case**: Prevents event queue overflow when tracing code with tight loops or recursive functions while preserving initial samples for analysis.

**Implementation Location**: `breadcrumb/src/breadcrumb/instrumentation/call_tracker.py` (156 lines)

---

## 2. User Interfaces

### 2.1 CLI Commands

**Global Command**: `breadcrumb [OPTIONS] COMMAND [ARGS]`

**Global Options**:
- `--format/-f {json|table}`: Output format (default: json for AI agents, table for humans)
- `--db-path PATH`: Custom database path (auto-discovered if not specified)
- `--verbose/-v`: Enable verbose output with debug information
- `--version`: Show version and exit

**Exit Codes**:
- `0`: Success
- `1`: Error
- `2`: No results found

#### Command: `breadcrumb list`

**Purpose**: List recent traces with basic metadata

**Options**:
- `--limit/-n INT`: Number of traces to show (default: 10)

**Example Output (JSON)**:
```json
{
  "traces": [
    {
      "id": "abc-123",
      "status": "completed",
      "started_at": "2025-01-10T14:30:00",
      "ended_at": "2025-01-10T14:30:02",
      "duration_ms": 2000.5
    }
  ],
  "total": 1
}
```

**Example Output (Table)**:
```
ID       Status      Started At           Duration
abc-123  completed   2025-01-10 14:30:00  2000.5ms
```

#### Command: `breadcrumb get <trace-id>`

**Purpose**: Get complete trace details including all events and exceptions

**Arguments**:
- `trace_id`: UUID of trace to retrieve

**Output Includes**:
- Trace metadata
- All events (calls, returns, exceptions) in chronological order
- All exceptions with stack traces
- Summary statistics (event count, exception count)

#### Command: `breadcrumb query <sql>`

**Purpose**: Execute custom SQL queries against the trace database

**Safety Features**:
- Only SELECT queries allowed (enforced at validation layer)
- 30 second query timeout
- Parameterized queries supported for SQL injection prevention
- Result truncation at 1MB (with warning)

**Examples**:
```bash
breadcrumb query "SELECT * FROM traces LIMIT 10"
breadcrumb query "SELECT * FROM exceptions WHERE exception_type='ValueError'"
breadcrumb query "SELECT function_name, COUNT(*) FROM trace_events GROUP BY function_name"
```

#### Command: `breadcrumb exceptions`

**Purpose**: Find exceptions within a time range

**Options**:
- `--since/-s TIME`: Time range (default: 1h)
  - Relative: `30m`, `2h`, `1d`
  - Absolute: `2025-01-10`, `2025-01-10T14:30:00`
- `--limit/-n INT`: Maximum exceptions to show (default: 10)

**Examples**:
```bash
breadcrumb exceptions                    # Last hour
breadcrumb exceptions --since 30m        # Last 30 minutes
breadcrumb exceptions --since 2025-01-10 # Since specific date
```

#### Command: `breadcrumb performance <function>`

**Purpose**: Analyze performance statistics for a specific function

**Arguments**:
- `function`: Function name to analyze

**Options**:
- `--limit/-n INT`: Number of slowest traces to show (default: 10)

**Output**:
- Call count
- Average/min/max duration in milliseconds
- List of slowest traces with arguments and timestamps

**Examples**:
```bash
breadcrumb performance fetch_data
breadcrumb performance process_payment --limit 5
```

#### Command: `breadcrumb serve-mcp`

**Purpose**: Start MCP server for AI agents (stdio transport)

**Options**:
- `--db-path PATH`: Database path (overrides global --db-path)
- `--port INT`: Port for TCP transport (future feature, currently ignored)

**Usage**:
```bash
breadcrumb serve-mcp
breadcrumb serve-mcp --db-path /path/to/traces.duckdb
```

**Server Initialization**:
- Auto-discovers database in current directory and parents (up to 5 levels)
- Validates database exists before starting
- Logs initialization to stderr
- Runs in foreground (blocking)

#### Command: `breadcrumb run`

**Purpose**: Run command with automatic breadcrumb tracing injection

**Required Options**:
- `--timeout/-t SECONDS`: Maximum execution time (required for safety)

**Configuration Options**:
- `--config/-c NAME`: Named configuration profile
- `--include/-i PATTERN`: Module patterns to include (multiple allowed)
- `--exclude/-e PATTERN`: Module patterns to exclude (multiple allowed)
- `--db-path PATH`: Database path
- `--sample-rate FLOAT`: Sampling rate 0.0-1.0
- `--silent`: Suppress breadcrumb initialization message

**Examples**:
```bash
breadcrumb run --timeout 60 python main.py
breadcrumb run -t 120 uv run my_app.py
breadcrumb run -c flock --timeout 30 python main.py
breadcrumb run -t 30 --exclude "flock.*" --exclude "pydantic.*" python main.py
breadcrumb run --timeout 10 --include "__main__" python script.py
breadcrumb run -t 300 pytest tests/
```

**How It Works**:
1. Creates wrapper script that initializes breadcrumb before user code
2. Injects `breadcrumb.init()` with specified configuration
3. Runs user script via `runpy.run_path()` as `__main__`
4. Monitors execution with timeout
5. Generates run report on success or timeout report on failure

**Post-Execution Reports**:

**Run Report** (on success):
- Key metrics: Total events, calls, returns, exceptions, duration, status
- Exception summary (if any)
- Call tree visualization (if events < 100)
- Top 10 most called functions (if events > 100)
- Tips for using `breadcrumb top` command

**Timeout Report** (on timeout):
- Most recent trace information
- Top 20 functions called before timeout
- Last 10 events before timeout
- Likely call stack at timeout (reconstructed from events)
- Recommendations for debugging

#### Command: `breadcrumb top`

**Purpose**: Show most frequently called functions (CRITICAL debugging tool)

**Arguments**:
- `limit`: Number of top functions to show (default: 10)

**Options**:
- `--skip/-s INT`: Skip first N functions (for pagination)
- `--trace/-t UUID`: Specific trace ID to analyze (default: most recent)
- `--db-path PATH`: Database path

**Examples**:
```bash
breadcrumb top 10              # Top 10 from most recent trace
breadcrumb top 20              # Top 20
breadcrumb top 20 --skip 5     # Positions 6-26
breadcrumb top 15 --trace abc123  # Specific trace
```

**Output Features**:
- Shows function call counts in descending order
- Displays total unique functions
- Suggests exclude patterns for noisy functions
- Auto-detects infrastructure code (logging, serialization, telemetry)
- Provides iterative debugging workflow tips

**Use Case**: Essential for config optimization - identify noisy functions to exclude after initial run.

#### Command: `breadcrumb clear`

**Purpose**: Delete trace database (cannot be undone)

**Options**:
- `--db-path PATH`: Database path (default: ~/.breadcrumb/traces.duckdb)
- `--force/-f`: Skip confirmation prompt

**Behavior**:
- Prompts for confirmation unless --force specified
- Deletes entire database file
- Shows success message or error

#### Command: `breadcrumb report`

**Purpose**: Generate execution report from most recent trace

**Options**:
- `--db-path PATH`: Database path

**Output**: Same as run report (KPIs, call tree, or top functions)

**Use Case**: Re-generate report after running code separately (not via `breadcrumb run`)

#### Command Group: `breadcrumb config`

**Purpose**: Manage configuration profiles for reusable tracing configs

**Subcommands**:
1. `config create <name>`: Create new configuration profile
2. `config show <name>`: Display configuration profile
3. `config list`: List all configuration profiles
4. `config edit <name>`: Modify existing configuration
5. `config delete <name>`: Remove configuration profile

**Config Create Options**:
- `--include/-i PATTERN`: Include patterns (multiple)
- `--exclude/-e PATTERN`: Exclude patterns (multiple)
- `--sample-rate FLOAT`: Sampling rate
- `--db-path PATH`: Database path
- `--workspace-only/--all-code`: Workspace filtering
- `--force/-f`: Overwrite existing config

**Config Edit Options**:
- All create options plus:
- `--add-include PATTERN`: Add to include list
- `--add-exclude PATTERN`: Add to exclude list
- `--remove-include PATTERN`: Remove from include list
- `--remove-exclude PATTERN`: Remove from exclude list
- `--enabled/--disabled`: Enable/disable tracing

**Examples**:
```bash
breadcrumb config create flock --include "flock.*" --exclude "*webhook*"
breadcrumb config create production --sample-rate 0.1
breadcrumb config show flock
breadcrumb config edit flock --add-exclude "flock.logging*"
breadcrumb config delete old-config
```

**Configuration Storage**: Profiles stored in `~/.breadcrumb/configs/<name>.yaml`

**Implementation Location**: `breadcrumb/src/breadcrumb/cli/main.py` (840 lines)

### 2.2 MCP Server Tools

**Server Framework**: FastMCP 2.12.4+
**Transport**: stdio (stdin/stdout)
**Tool Count**: 4 specialized tools

#### Tool: `breadcrumb__query_traces`

**Purpose**: Execute SQL queries against trace database

**Parameters**:
- `sql` (string, required): SQL SELECT query to execute

**Returns**:
```json
{
  "traces": [...],
  "total": 100,
  "query_time_ms": 15,
  "schema_version": "1.0.0"
}
```

**Safety Features**:
- Only SELECT queries allowed
- SQL injection prevention via parameterization
- 30 second timeout
- Automatic response truncation at 1MB (with warning)

**Error Handling**:
- `QueryTimeoutError`: Query exceeded 30s
- `InvalidQueryError`: Unsafe SQL or syntax error
- `EmptyDatabaseError`: No traces in database

**Example Queries**:
```sql
SELECT * FROM traces ORDER BY started_at DESC LIMIT 10
SELECT * FROM exceptions WHERE exception_type='ValueError'
SELECT function_name, COUNT(*) FROM trace_events GROUP BY function_name
```

#### Tool: `breadcrumb__get_trace`

**Purpose**: Retrieve complete trace details by ID

**Parameters**:
- `trace_id` (string, required): UUID of trace

**Returns**:
```json
{
  "trace": { /* trace metadata */ },
  "events": [ /* all events */ ],
  "exceptions": [ /* all exceptions */ ],
  "summary": {
    "trace_id": "...",
    "status": "completed",
    "event_count": 42,
    "exception_count": 0
  }
}
```

**Error Handling**:
- `TraceNotFoundError`: Trace ID doesn't exist

**Use Cases**:
- Investigate specific execution
- Understand call flow for one trace
- Debug specific failure

#### Tool: `breadcrumb__find_exceptions`

**Purpose**: Find exceptions within time range

**Parameters**:
- `since` (string, default: "1h"): Time range
  - Relative: "30m", "2h", "1d"
  - Absolute: "2025-01-10", "2025-01-10T14:30:00Z"
- `limit` (int, default: 10): Maximum exceptions

**Returns**:
```json
{
  "exceptions": [ /* exception list */ ],
  "total": 5,
  "time_range": "1h",
  "limit": 10
}
```

**Error Handling**:
- `ValueError`: Invalid time range format

**Use Cases**:
- Debug recent failures
- Find all occurrences of exception type
- Understand failure patterns

#### Tool: `breadcrumb__analyze_performance`

**Purpose**: Analyze performance statistics for function

**Parameters**:
- `function` (string, required): Function name
- `limit` (int, default: 10): Number of slowest traces

**Returns**:
```json
{
  "function": "process_data",
  "statistics": {
    "call_count": 100,
    "avg_duration_ms": 150.5,
    "min_duration_ms": 10.2,
    "max_duration_ms": 500.3
  },
  "slowest_traces": [ /* slowest executions */ ]
}
```

**Error Handling**:
- `FunctionNotFound`: No traces for function

**Use Cases**:
- Identify performance bottlenecks
- Analyze typical vs worst-case performance
- Find slow traces for specific function

**Implementation Location**: `breadcrumb/src/breadcrumb/mcp/server.py` (347 lines)

### 2.3 Python API

**Primary Entry Point**: `breadcrumb.init()`

**Configuration Parameters**:
```python
breadcrumb.init(
    enabled: bool = True,           # Enable/disable tracing
    include: List[str] = ["*"],     # Module patterns to include
    exclude: List[str] = [],        # Module patterns to exclude
    sample_rate: float = 1.0,       # Sampling rate 0.0-1.0
    db_path: str = "~/.breadcrumb/traces.duckdb",  # Database path
    backend: str = "auto",          # "pep669", "settrace", or "auto"
    workspace_only: bool = True,    # Only trace workspace code
    silent: bool = False            # Suppress init message
)
```

**Configuration Precedence**:
1. Python API parameters (highest)
2. Environment variables
3. Config file (`~/.breadcrumb/config.yaml`)
4. Defaults (lowest)

**Environment Variables**:
- `BREADCRUMB_ENABLED`: Enable/disable tracing (1/true/yes/on or 0/false/no/off)
- `BREADCRUMB_DB_PATH`: Database path
- `BREADCRUMB_SAMPLE_RATE`: Sampling rate (0.0-1.0)

**Helper Functions**:
```python
breadcrumb.get_config()        # Get current configuration
breadcrumb.get_backend()       # Get active backend instance
breadcrumb.get_events()        # Get events from backend
breadcrumb.reset_config()      # Reset to uninitialized state
```

**Example Usage**:
```python
import breadcrumb

# Basic usage
breadcrumb.init()

# Selective instrumentation
breadcrumb.init(
    include=["myapp.*"],
    exclude=["myapp.vendor.*", "myapp.tests.*"]
)

# Sampling
breadcrumb.init(sample_rate=0.5)  # Trace 50% of calls

# Custom backend
breadcrumb.init(backend="pep669")
```

**Implementation Location**: `breadcrumb/src/breadcrumb/config.py` (420 lines)

---

## 3. Key Features

### 3.1 Filtering and Sampling

#### Pattern-Based Filtering

**Glob-Style Patterns**:
- `*`: Match everything
- `module.*`: Match module and all submodules
- `module`: Exact module match

**Include Patterns** (default: `["*"]`):
- Whitelist approach: Only specified modules traced
- Multiple patterns OR'd together
- Applied after exclude patterns

**Exclude Patterns** (default: Python stdlib internals):
```python
[
    'threading', 'queue', '_thread', 'contextlib',
    'importlib.*', 'sys', 'os', 'posixpath',
    'asyncio.*', 'typing', 'dataclasses',
    'logging', 'json', 're', 'fractions.*'
]
```

**Filter Evaluation Order**:
1. Breadcrumb internal code (always excluded)
2. Workspace-only filtering (if enabled)
3. Exclude patterns (checked first)
4. Include patterns (checked if not excluded)
5. Default: exclude if no include pattern matches

**Implementation**: Filtering happens at instrumentation time (before event capture) for optimal performance.

#### Workspace-Only Tracing

**Purpose**: Only trace user's code, not external libraries

**Workspace Detection**:
- Workspace path: Current working directory by default (configurable)
- Site-packages paths: Auto-detected via `site.getsitepackages()`
- Stdlib path: Auto-detected via `sysconfig.get_path('stdlib')`
- .venv exclusion: Automatically excludes virtual environment directories

**Filtering Logic**:
1. Exclude stdlib (e.g., `/usr/lib/python3.12/`)
2. Exclude site-packages (e.g., `/usr/lib/python3.12/site-packages/`)
3. Exclude .venv directories (e.g., `/project/.venv/`)
4. Only include files starting with workspace path
5. Still apply pattern-based filtering to workspace files

**Benefits**:
- Dramatically reduces noise
- Focuses on application code
- Excludes framework internals
- Works with editable installs

**Default**: Enabled (`workspace_only=True`)

#### Sampling

**Configuration**: `sample_rate` parameter (0.0 to 1.0)
- `1.0`: Trace 100% of calls (default)
- `0.5`: Trace 50% of calls
- `0.1`: Trace 10% of calls

**Implementation**: Currently placeholder - not fully implemented in reviewed code

**Use Cases**:
- Reduce overhead in production
- High-volume applications
- Continuous monitoring

### 3.2 Secret Redaction

**Status**: Mentioned in documentation but implementation not found in reviewed files

**Documented Patterns** (from README):
- Passwords (`password`, `passwd`, `secret`)
- API keys (`api_key`, `token`, `bearer`)
- Credit cards (16 digits with dashes/spaces)
- SSNs (XXX-XX-XXXX format)
- JWTs (eyJ... format)
- AWS keys (AKIA...)
- GitHub tokens (ghp_...)

**Expected Behavior**: Sensitive values replaced with `[REDACTED]` before storage

**Note**: Mentioned in README but not found in instrumentation or storage code paths reviewed. May be future work or separate module.

### 3.3 Value Truncation

**Purpose**: Prevent large values from bloating database

**Configuration**:
- Max value size: 1024 bytes (1KB) - `MAX_VALUE_SIZE`
- Applied to all captured values (args, returns, local vars)

**Truncation Strategy**:
1. Simple types (int, float, bool, None): No truncation
2. Strings: Truncate at 1KB, append indicator
3. Dicts/lists: JSON serialize, then truncate if needed
4. Other types: `repr()`, then truncate if needed

**Truncation Indicator**: `"[TRUNCATED: original size {N} bytes]"`

**Recursive Truncation**: `truncate_dict()` recursively truncates all values in nested dicts/lists

**Safe Repr**:
- Max length: 200 characters (in backend) or 1024 bytes (in storage)
- Handles circular references gracefully
- Returns `"<unable to represent>"` on error

**Implementation Locations**:
- Backend: `pep669_backend.py::_safe_repr()` (200 char limit)
- Storage: `value_truncation.py::truncate_value()` (1KB limit)

### 3.4 Performance Optimizations

#### Low Overhead Design

**PEP 669 Backend**:
- Overhead: ~2% (vs baseline)
- Benchmark: 1M function calls
  - Baseline: 0.85s
  - With Breadcrumb: 0.87s (+2.4%)

**sys.settrace Backend**:
- Overhead: ~2000%+ (shows warning)
- Not recommended for production
- Acceptable for debugging/development

#### Event Queue Management

**Queue Configuration**:
- Max queue size: 10,000 events
- Batch size: 100 events
- Batch timeout: 100ms

**Backpressure Handling**:
1. Queue full: Drop events (non-blocking)
2. Track dropped functions for diagnostics
3. Log warning every 100 dropped events
4. Auto-stop after 3 queue overflow warnings

**Batch Writing**:
- Groups events by type (traces, trace_events, exceptions)
- Uses `executemany()` for bulk INSERT
- Reduces database lock contention
- Non-blocking: instrumentation never waits

#### Smart Auto-Filtering

**Call Tracker**:
- Threshold: 100 calls per function in 10 seconds
- Window: Rolling 10 second window
- Reset interval: 60 seconds (allows re-sampling)
- Behavior: First 100 calls captured, then filtered

**Benefits**:
- Prevents queue overflow from hot loops
- Preserves initial samples for analysis
- Automatic, no configuration needed
- Transparent with truncation metadata

#### Memory Management

**Per-Thread Limits**:
- Max events per thread: 10,000 (PEP 669 backend)
- FIFO eviction: Oldest events dropped when limit reached

**Value Truncation**:
- Limits all values to 1KB
- Prevents large objects from consuming memory
- Applied before storage

**Event Callback Integration**:
- Events sent directly to writer (bypass local storage)
- Reduces memory footprint when writer active

### 3.5 Database Features

#### Schema Migrations

**Status**: Mentioned in README but implementation not found in reviewed storage files

**Expected Features**:
- Automatic schema version detection
- Upgrade migrations on database open
- Version tracking in database

**Current Schema Version**: "1.0.0" (from MCP tool response)

#### Retention Policies

**File Location**: `breadcrumb/src/breadcrumb/storage/retention.py` (not reviewed in detail)

**Expected Features**:
- Automatic cleanup of old traces
- Configurable retention periods
- Scheduled cleanup jobs

#### Connection Management

**Connection Pool**:
- Thread-safe connection manager
- Retry logic for database locks
- Context manager support for transactions

**Lock Handling**:
- Automatic retry on "database is locked" errors
- Helpful error messages for users
- Connection cleanup on shutdown

**Implementation Location**: `breadcrumb/src/breadcrumb/storage/connection.py` (not fully reviewed)

---

## 4. Output Formats and Reporting

### 4.1 Output Formats

#### JSON Format (Default for AI Agents)

**Structure**:
```json
{
  "traces": [ /* array of results */ ],
  "total": 100,
  "query_time_ms": 15,
  "metadata": { /* optional metadata */ }
}
```

**Features**:
- Machine-readable
- Consistent structure across all commands
- Includes metadata (total count, query time, schema version)
- Default for CLI (AI-optimized)

**Use Cases**:
- AI agent consumption
- Programmatic parsing
- Scripting and automation

#### Table Format (Human-Friendly)

**Example**:
```
ID       Status      Started At           Duration
abc-123  completed   2025-01-10 14:30:00  2000.5ms
def-456  failed      2025-01-10 14:35:00  1500.0ms
```

**Features**:
- Human-readable
- Column alignment
- Truncated values for display
- Requested with `--format table`

**Use Cases**:
- Terminal viewing
- Quick inspection
- Human debugging

### 4.2 Run Reports

**Generated After**: Successful `breadcrumb run` completion

**KPI Section**:
```
Key Metrics:
  Total Events: 250
  - Calls: 125
  - Returns: 123
  - Exceptions: 2
  Duration: 2000.50 ms
  Status: completed
```

**Exception Summary** (if present):
```
Exceptions Raised: 2
  - ValueError: Invalid input
  - KeyError: 'missing_key'
```

**Call Tree** (if events < 100):
```
Call Tree:
  -> myapp.main
    -> myapp.process_data
      -> myapp.utils.validate
      <- myapp.utils.validate (5.23ms)
      -> myapp.utils.transform
      <- myapp.utils.transform (10.45ms)
    <- myapp.process_data (20.15ms)
  <- myapp.main (50.75ms)
```

**Top Functions** (if events > 100):
```
Top 10 Most Called Functions:
  myapp.logging._serialize: 500 calls
  myapp.utils.helper: 200 calls
  myapp.process_item: 50 calls

TIP: Use 'breadcrumb top 20' to see more!
     High call counts? Consider excluding with:
     breadcrumb config edit <name> --add-exclude '<pattern>*'
```

**Purpose**: Immediate post-execution feedback for developers

### 4.3 Timeout Reports

**Generated After**: Command timeout in `breadcrumb run`

**Sections**:

1. **Timeout Information**:
```
Command exceeded timeout of 60 seconds
```

2. **Most Recent Trace**:
```
Most Recent Trace: abc-123
Started at: 2025-01-10T14:30:00
Thread ID: 12345
```

3. **Top 20 Functions Called Before Timeout**:
```
  myapp.main: 1 calls
  myapp.fetch_loop: 5000 calls
  myapp.process_item: 1000 calls
```

4. **Last 10 Events Before Timeout**:
```
  [call] myapp.fetch_loop at /path/file.py:42
  [call] myapp.process_item at /path/file.py:15
  [return] myapp.process_item at /path/file.py:20
```

5. **Likely Call Stack at Timeout**:
```
  0: myapp.main at /path/file.py:10
  1: myapp.fetch_loop at /path/file.py:42
  2: myapp.process_item at /path/file.py:15
```

6. **Recommendations**:
```
  1. Increase timeout if script needs more time
  2. Check if script is stuck in infinite loop
  3. Use breadcrumb query to investigate trace events
```

**Purpose**: Debug timeout issues with execution context

### 4.4 Top Functions Report

**Generated By**: `breadcrumb top` command

**Header**:
```
TOP 10 MOST CALLED FUNCTIONS
Showing 10 of 250 unique functions
```

**Function List**:
```
   1. myapp.logging._serialize    : 500 calls
   2. myapp.utils.helper           : 200 calls
   3. myapp.process_item           : 50 calls
   ...
```

**Debugging Tips Section**:
```
DEBUGGING TIPS:
  - High call counts often indicate:
    * Internal framework/library code (consider excluding)
    * Logging/serialization utilities (usually safe to exclude)
    * Hot loops in your application (keep these!)

  - To exclude noisy modules:
    breadcrumb config edit <name> --add-exclude '<pattern>'

  - Example patterns to exclude:
    --add-exclude 'myapp.logging.*'
```

**Auto-Suggested Excludes**:
- Analyzes top 5 functions
- Suggests patterns for infrastructure keywords (logging, telemetry, webhook, serialize)
- Shows concrete exclude commands

**Purpose**: Essential for iterative config optimization

### 4.5 Error Messages and Suggestions

#### Empty Database Error

**Message**:
```json
{
  "error": "EmptyDatabaseError",
  "message": "No traces found in database",
  "suggestion": "To start tracing, add 'import breadcrumb; breadcrumb.init()' to your Python code and run your application. See docs/QUICKSTART.md for setup instructions."
}
```

**Helpful Guidance**: Clear next steps for users

#### Invalid Query Error

**Message**:
```json
{
  "error": "InvalidQueryError",
  "message": "Unsafe SQL keyword detected: DELETE",
  "suggestion": "Only SELECT queries are allowed. Available tables: traces, trace_events, exceptions"
}
```

**Lists Available Tables**: Guides users to correct query

#### Query Timeout Error

**Message**:
```json
{
  "error": "QueryTimeoutError",
  "message": "Query exceeded 30 second timeout",
  "suggestion": "Use LIMIT to reduce result set or simplify your query"
}
```

**Actionable Advice**: Specific optimization suggestions

#### Trace Not Found Error

**Message**:
```json
{
  "error": "TraceNotFoundError",
  "message": "No trace found with ID: abc-123",
  "suggestion": "Use breadcrumb__query_traces to find available trace IDs"
}
```

**Suggests Alternative Tool**: Guides to discovery flow

#### Database Locked Error

**Message**:
```
Database is temporarily locked. This usually resolves automatically.
If the issue persists, ensure no other processes are writing to the database.
```

**Reassuring Tone**: Explains transient nature

#### Config Not Found Error

**CLI Output**:
```
Error: Config file not found: flock
Use 'breadcrumb config create flock' to create it
```

**Next Step Command**: Exact command to fix issue

#### sys.settrace Warning

**Warning Box** (shown once on first use):
```
╔════════════════════════════════════════════════════════════╗
║ WARNING: Using sys.settrace fallback backend              ║
║                                                            ║
║ Performance Impact: ~2000%+ overhead vs ~5% for PEP 669  ║
║                                                            ║
║ You are running Python 3.11 which doesn't support PEP 669.║
║ For production use, upgrade to Python 3.12+ for better    ║
║ performance.                                               ║
║                                                            ║
║ Recommendations:                                           ║
║   - Development: This backend is acceptable               ║
║   - Production: Upgrade to Python 3.12+ or disable        ║
╚════════════════════════════════════════════════════════════╝
```

**Visual Impact**: Box drawing for attention

#### Queue Overflow Warning

**Initial Warning** (every 100 dropped events):
```
WARNING: Breadcrumb event queue full. Dropped 100 events total.

Most frequent calls being dropped:
  myapp.logging._serialize: 50 calls
  myapp.utils.helper: 30 calls
```

**Auto-Stop Report** (after 3 warnings):
```
🛑 QUEUE OVERFLOW LIMIT REACHED (3 breaks)

BREADCRUMB AUTO-STOP REPORT
============================

Writer Statistics:
  Events written: 10000
  Events dropped: 500
  Queue breaks: 3
  Batches written: 100

Top 20 Functions Causing Overflow:
  myapp.logging._serialize: 500 dropped events
  myapp.fetch_loop: 200 dropped events

Smart Auto-Filter Statistics:
  Truncated functions: 5
  Auto-filtered events: 1000

Recommendations:
  1. Use --exclude patterns to filter noisy frameworks
  2. Increase --sample-rate (e.g., 0.1 for 10% sampling)
  3. Focus tracing on specific modules with --include
  4. Smart auto-filter is already active (threshold: 100 calls/10s)
```

**Comprehensive Diagnostics**: Shows exactly what went wrong

---

## 5. Current UX Patterns

### 5.1 Helpful Tips and Messages

**Initialization Message**:
```
Breadcrumb enabled: backend=pep669 db=~/.breadcrumb/traces.duckdb, sample_rate=1.0, include=1 exclude=15 workspace_only
(config: ~/.breadcrumb/config.yaml)
```

**Configuration Summary**: One-line status on startup

**Verbose Mode**:
```
Breadcrumb CLI v0.1.0
Format: json
Database: auto-discover
```

**Debug Information**: Shows configuration when --verbose

**Top Command Tips** (after results):
```
DEBUGGING TIPS:
  - High call counts often indicate:
    * Internal framework/library code (consider excluding)
    * Logging/serialization utilities (usually safe to exclude)
    * Hot loops in your application (keep these!)
```

**Educational**: Teaches users to interpret results

**Run Command Documentation**:
```
IMPORTANT WORKFLOW: After running, use 'breadcrumb top' to identify noisy functions!

The "top" command shows most frequently called functions - this is CRITICAL
for iterative debugging. For example, you might see flock.logging called 500
times. Ask yourself: "Is this important for debugging? Probably not!"
Then exclude it: breadcrumb config edit myconfig --add-exclude "flock.logging*"
```

**Workflow Guidance**: Embedded in help text

### 5.2 Iterative Debugging Workflow

**Promoted Pattern**:
1. Run with basic config: `breadcrumb run -t 60 python app.py`
2. Check what's noisy: `breadcrumb top 10`
3. Optimize config: `breadcrumb config edit myconfig --add-exclude "noisy.module*"`
4. Re-run with refined config: `breadcrumb run -c myconfig -t 60 python app.py`

**Supported By**:
- Top command with auto-suggestions
- Config edit command with granular options
- Run report showing top functions
- Inline tips in command help

**Philosophy**: Discovery-driven configuration, not guesswork

### 5.3 AI-First Design

**JSON Default**:
- All commands default to JSON output
- Structured for machine parsing
- Consistent schema across commands

**MCP Tool Descriptions**:
- Clear purpose statements
- Parameter documentation
- Example usage in docstrings
- Error suggestion messages

**Table Format for Humans**:
- Explicitly opt-in with `--format table`
- Acknowledges dual audience (AI + humans)

**Safety First**:
- Only SELECT queries allowed
- Query timeouts prevent runaway queries
- Result truncation at 1MB
- Clear error messages

### 5.4 Progressive Disclosure

**Simple Start**:
```python
import breadcrumb
breadcrumb.init()
```

**Basic CLI**:
```bash
breadcrumb list
breadcrumb exceptions
```

**Advanced Features** (when needed):
- Custom SQL queries
- Config profiles
- Include/exclude patterns
- Sample rates
- Workspace filtering

**Documentation Hierarchy**:
1. README: Quick start
2. QUICKSTART.md: AI agent guide
3. API_REFERENCE.md: Complete reference

**Philosophy**: Easy to start, powerful when needed

### 5.5 Database Discovery

**Auto-Discovery Strategy**:
1. Check for `.breadcrumb/traces.duckdb` in current directory
2. Search up to 5 parent directories
3. Fall back to `~/.breadcrumb/traces.duckdb`

**User-Friendly**:
- No configuration required for common case
- Works across multi-project workspaces
- Explicit override available (`--db-path`)

**Error Messages**:
```
Could not find .breadcrumb/traces.duckdb.
Make sure you have initialized Breadcrumb tracing in your project.
Run: python -c 'import breadcrumb; breadcrumb.init()' to create the database.
```

**Actionable**: Tells user exactly how to fix

### 5.6 Configuration System

**Three-Layer Configuration**:
1. Defaults (sensible, zero-config start)
2. Config file (persistent, shareable)
3. CLI/API overrides (explicit, highest priority)

**Config File Features**:
- Human-readable YAML
- Comments with documentation
- Auto-created with defaults on first use
- Multiple named profiles

**Default Config** (~/.breadcrumb/config.yaml):
```yaml
# Breadcrumb AI Tracer Configuration
# This file is automatically created with defaults if it doesn't exist.

# Enable or disable tracing
enabled: true

# Module patterns to include (glob style)
include:
  - '*'

# Module patterns to exclude (glob style)
exclude: []

# Sampling rate (0.0 to 1.0)
sample_rate: 1.0

# Database path for traces
db_path: '~/.breadcrumb/traces.duckdb'

# Backend: 'pep669' (Python 3.12+) or 'settrace' (older Python)
backend: 'pep669'

# Only trace code in workspace (not stdlib/site-packages)
workspace_only: true
```

**Self-Documenting**: Config file includes usage instructions

---

## 6. Architecture Summary

### 6.1 System Components

**Instrumentation Layer**:
- PEP 669 backend (Python 3.12+)
- sys.settrace backend (Python 3.10-3.11)
- Call tracker (smart auto-filtering)
- Event filtering (patterns, workspace-aware)

**Integration Layer**:
- Event callback system
- Trace lifecycle management
- Event-to-storage conversion
- Exception handling

**Storage Layer**:
- DuckDB database (embedded, columnar)
- Async writer (queue-based batching)
- Connection manager (thread-safe pooling)
- Value truncation (size limits)
- Query interface (safety, timeouts)

**Interface Layer**:
- CLI (Typer-based, 13 commands)
- MCP server (FastMCP, 4 tools)
- Python API (init, config, helpers)

### 6.2 Data Flow

**Capture Path**:
1. Python code executes
2. Backend captures event (PEP 669 or sys.settrace)
3. Filtering applied at instrumentation time
4. Event callback invoked (if integration active)
5. Integration creates/updates trace record
6. Event queued in async writer
7. Writer batches events (100ms or 100 events)
8. Bulk INSERT to DuckDB
9. Connection released to pool

**Query Path**:
1. User invokes CLI command or MCP tool
2. Command validates input (SQL safety, parameters)
3. Connection acquired from pool
4. Query executed with timeout (30s)
5. Results fetched and formatted
6. Response truncated if > 1MB
7. JSON or table output returned
8. Connection released to pool

### 6.3 Threading Model

**Instrumentation**:
- PEP 669: Thread-safe via `threading.local()`
- sys.settrace: Per-thread activation required
- Events stored per-thread

**Integration**:
- Event callbacks invoked on instrumented thread
- Trace ID tracking with thread-safe dict
- Lock-protected trace creation

**Storage**:
- Background writer thread (`breadcrumb-writer`)
- Thread-safe queue for event passing
- Connection pool for thread-safe DB access
- Daemon thread (doesn't block exit)

**Query**:
- Runs on caller's thread (CLI or MCP server)
- Connection pool ensures thread safety
- Query timeout via threading (separate thread)

### 6.4 Performance Characteristics

**Memory**:
- Per-thread event limit: 10,000 events
- Queue size: 10,000 events
- Value truncation: 1KB per value
- Smart auto-filtering reduces hot loop memory

**CPU**:
- PEP 669 overhead: ~2%
- sys.settrace overhead: ~2000%+
- Batch writing reduces CPU spikes
- Background thread for I/O

**I/O**:
- Async writes (non-blocking instrumentation)
- Batch INSERT reduces DB locks
- Connection pooling reuses connections
- DuckDB columnar storage (efficient reads)

**Disk**:
- DuckDB database file (size depends on traces)
- Value truncation prevents bloat
- Retention policies (future) will manage size

---

## 7. Testing and Quality

**Test Coverage**: 13/13 tests passing (Phase 3 complete)

**Test Locations**:
- Unit tests for each component
- Integration tests for end-to-end flows
- MCP server tests

**Quality Indicators**:
- Type hints throughout codebase
- Comprehensive docstrings
- Error handling with helpful messages
- Graceful degradation (fallback backend)
- Thread-safe design

---

## 8. Gaps and Future Work

**Identified Gaps** (mentioned but not fully implemented):

1. **Secret Redaction**: Mentioned in README but implementation not found in reviewed code
2. **Sampling**: `sample_rate` parameter exists but implementation not verified
3. **Schema Migrations**: Mentioned but `migrations.py` not reviewed in detail
4. **Retention Policies**: `retention.py` exists but not reviewed in detail
5. **TCP Transport**: MCP server --port flag exists but ignored (stdio only)

**Future Features** (from README):
- PyPI package
- Performance visualizations
- Distributed tracing
- Cloud storage backends

---

## Appendix: File Inventory

**Key Implementation Files** (reviewed):

| File | Lines | Purpose |
|------|-------|---------|
| `cli/main.py` | 840 | CLI entry point, all commands |
| `cli/commands/run.py` | 500 | Run command with injection |
| `cli/commands/top.py` | 196 | Top functions command |
| `config.py` | 420 | Configuration system |
| `instrumentation/pep669_backend.py` | 813 | PEP 669 backend |
| `instrumentation/settrace_backend.py` | 383 | sys.settrace backend |
| `instrumentation/call_tracker.py` | 156 | Smart auto-filtering |
| `storage/async_writer.py` | 621 | Async writer with batching |
| `storage/query.py` | 502 | Query interface |
| `storage/value_truncation.py` | 105 | Value size limits |
| `integration.py` | 294 | Backend-storage bridge |
| `mcp/server.py` | 347 | MCP server and tools |

**Total Reviewed Lines**: ~5,177 lines of implementation code

---

## Conclusion

Breadcrumb is a comprehensive, AI-native Python execution tracer with a mature feature set across instrumentation, storage, and user interfaces. The system demonstrates thoughtful design with strong emphasis on:

1. **Performance**: Low-overhead instrumentation, async I/O, smart filtering
2. **Usability**: Zero-config start, iterative optimization workflow, helpful error messages
3. **Safety**: Query timeouts, SQL injection prevention, backpressure handling
4. **Dual Audience**: JSON for AI agents, table for humans, MCP tools + CLI
5. **Production Readiness**: Thread-safety, graceful degradation, comprehensive error handling

The codebase is well-structured, thoroughly documented, and production-ready for the implemented features. Future work should focus on completing secret redaction, schema migrations, and retention policies to reach full v1.0 status.
