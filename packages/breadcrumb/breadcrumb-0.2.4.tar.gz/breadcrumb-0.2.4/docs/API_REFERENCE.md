# Breadcrumb AI Tracer - API Reference

Complete API documentation for Python API, MCP tools, and CLI commands.

## Table of Contents

- [Python API](#python-api)
  - [Configuration](#configuration)
  - [Initialization](#initialization)
  - [Query Interface](#query-interface)
- [MCP Tools](#mcp-tools)
  - [breadcrumb__query_traces](#breadcrumb__query_traces)
  - [breadcrumb__get_trace](#breadcrumb__get_trace)
  - [breadcrumb__find_exceptions](#breadcrumb__find_exceptions)
  - [breadcrumb__analyze_performance](#breadcrumb__analyze_performance)
- [CLI Commands](#cli-commands)
  - [Global Options](#global-options)
  - [list](#list)
  - [get](#get)
  - [query](#query)
  - [exceptions](#exceptions)
  - [performance](#performance)
  - [serve-mcp](#serve-mcp)
- [Database Schema](#database-schema)
- [Error Handling](#error-handling)

---

## Python API

### Configuration

#### `breadcrumb.init()`

Initialize Breadcrumb tracer with configuration.

**Signature:**

```python
def init(
    enabled: Optional[bool] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    sample_rate: Optional[float] = None,
    db_path: Optional[str] = None,
    backend: Optional[Literal["sqlite", "memory", "pep669"]] = None,
    silent: bool = False,
) -> BreadcrumbConfig
```

**Parameters:**

- `enabled` (bool, optional): Enable or disable tracing. Default: `True`
- `include` (List[str], optional): Glob patterns for files to trace. Default: `["**/*.py"]`
- `exclude` (List[str], optional): Glob patterns for files to exclude. Default: `[]`
- `sample_rate` (float, optional): Sampling rate 0.0-1.0. Default: `1.0` (trace all)
- `db_path` (str, optional): Path to SQLite database. Default: `".breadcrumb/traces.db"`
- `backend` (Literal["sqlite", "memory", "pep669"], optional): Storage backend. Default: `"sqlite"`
- `silent` (bool, optional): Suppress initialization message. Default: `False`

**Returns:**

`BreadcrumbConfig` instance with active configuration.

**Raises:**

- `ValueError`: If configuration values are invalid (e.g., sample_rate not in 0.0-1.0 range)
- `TypeError`: If configuration types are incorrect
- `RuntimeError`: If PEP 669 backend requested but Python version < 3.12

**Configuration Precedence:**

Configuration is applied in this order (highest to lowest priority):
1. Python API parameters (arguments to `init()`)
2. Environment variables (`BREADCRUMB_*`)
3. Default values

**Environment Variables:**

- `BREADCRUMB_ENABLED`: Enable/disable tracing (`1`/`true`/`yes`/`on` or `0`/`false`/`no`/`off`)
- `BREADCRUMB_DB_PATH`: Path to SQLite database
- `BREADCRUMB_SAMPLE_RATE`: Sampling rate (0.0-1.0)

**Examples:**

Basic initialization:
```python
import breadcrumb
breadcrumb.init()
```

Custom sampling:
```python
breadcrumb.init(sample_rate=0.5)  # Trace 50% of calls
```

Selective instrumentation:
```python
breadcrumb.init(
    include=["src/**/*.py"],
    exclude=["tests/**", "scripts/**"]
)
```

Custom database path:
```python
breadcrumb.init(db_path="/var/traces/app.db")
```

PEP 669 backend (Python 3.12+):
```python
breadcrumb.init(backend="pep669")
```

Disable tracing:
```python
breadcrumb.init(enabled=False)
```

#### `breadcrumb.get_config()`

Get the current configuration.

**Signature:**

```python
def get_config() -> Optional[BreadcrumbConfig]
```

**Returns:**

`BreadcrumbConfig` instance if initialized, `None` otherwise.

**Example:**

```python
import breadcrumb

breadcrumb.init()
config = breadcrumb.get_config()
print(config.summary())
# Output: "Breadcrumb enabled: backend=sqlite db=.breadcrumb/traces.db, sample_rate=1.0, include=1 exclude=0"
```

#### `breadcrumb.reset_config()`

Reset configuration to uninitialized state.

**Signature:**

```python
def reset_config() -> None
```

**Notes:**

- Stops active backend if running
- Primarily used for testing
- Not recommended in production code

**Example:**

```python
breadcrumb.init()
# ... some code ...
breadcrumb.reset_config()
# Tracing is now disabled
```

#### `breadcrumb.get_backend()`

Get the active backend instance.

**Signature:**

```python
def get_backend() -> Optional[Backend]
```

**Returns:**

Backend instance if initialized and using PEP 669 backend, `None` otherwise.

**Example:**

```python
breadcrumb.init(backend="pep669")
backend = breadcrumb.get_backend()
if backend:
    print(f"Backend active: {backend}")
```

#### `breadcrumb.get_events()`

Get trace events from the active backend.

**Signature:**

```python
def get_events() -> Optional[List[TraceEvent]]
```

**Returns:**

List of `TraceEvent` objects if PEP 669 backend is active, `None` otherwise.

**Example:**

```python
breadcrumb.init(backend="pep669")
# ... run some code ...
events = breadcrumb.get_events()
if events:
    print(f"Captured {len(events)} events")
```

---

### Initialization

#### `BreadcrumbConfig`

Configuration dataclass for Breadcrumb tracer.

**Attributes:**

- `enabled` (bool): Whether tracing is enabled
- `include` (List[str]): Glob patterns for files to trace
- `exclude` (List[str]): Glob patterns for files to exclude
- `sample_rate` (float): Sampling rate 0.0-1.0
- `db_path` (str): Path to SQLite database
- `backend` (Literal["sqlite", "memory", "pep669"]): Storage backend

**Methods:**

- `summary() -> str`: Returns one-line configuration summary

**Example:**

```python
from breadcrumb import BreadcrumbConfig

config = BreadcrumbConfig(
    enabled=True,
    include=["src/**/*.py"],
    exclude=["tests/**"],
    sample_rate=0.5,
    db_path=".breadcrumb/traces.db",
    backend="sqlite"
)

print(config.summary())
```

---

### Query Interface

#### `query_traces()`

Execute SQL query on trace database (SELECT only).

**Signature:**

```python
def query_traces(
    sql: str,
    params: Optional[List[Any]] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]
```

**Parameters:**

- `sql` (str): SQL SELECT query to execute
- `params` (List[Any], optional): Query parameters for parameterized queries
- `db_path` (str, optional): Path to database (auto-discovered if not provided)

**Returns:**

List of dictionaries, one per row, with column names as keys.

**Raises:**

- `InvalidQueryError`: If query is not a SELECT or contains unsafe operations
- `QueryError`: If query fails or database is not accessible
- `QueryTimeoutError`: If query exceeds 30 second timeout

**Safety Features:**

- Only SELECT queries allowed (no INSERT, UPDATE, DELETE, etc.)
- SQL injection prevention via parameterized queries
- 30-second query timeout
- Automatic retry on database lock errors

**Examples:**

Basic query:
```python
from breadcrumb.storage.query import query_traces

results = query_traces("SELECT * FROM traces LIMIT 10")
for trace in results:
    print(f"Trace {trace['id']}: {trace['status']}")
```

Parameterized query:
```python
results = query_traces(
    "SELECT * FROM traces WHERE status = ? LIMIT 10",
    params=['failed']
)
```

Join tables:
```python
sql = """
    SELECT t.id, t.status, e.exception_type
    FROM traces t
    JOIN exceptions e ON t.id = e.trace_id
    WHERE t.status = 'failed'
"""
results = query_traces(sql)
```

#### `get_trace()`

Get full trace with all events and exceptions.

**Signature:**

```python
def get_trace(
    trace_id: str,
    db_path: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**

- `trace_id` (str): Trace UUID to retrieve
- `db_path` (str, optional): Path to database

**Returns:**

Dictionary with keys:
- `trace` (dict): Trace metadata
- `events` (list): List of trace events
- `exceptions` (list): List of exceptions

**Raises:**

- `TraceNotFoundError`: If trace ID not found
- `QueryError`: If query fails

**Example:**

```python
from breadcrumb.storage.query import get_trace

trace = get_trace("123e4567-e89b-12d3-a456-426614174000")

print(f"Status: {trace['trace']['status']}")
print(f"Events: {len(trace['events'])}")
print(f"Exceptions: {len(trace['exceptions'])}")

for event in trace['events']:
    print(f"  {event['event_type']}: {event['function_name']}")
```

#### `find_exceptions()`

Find recent exceptions within time range.

**Signature:**

```python
def find_exceptions(
    since: str = "1h",
    limit: int = 10,
    db_path: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**

- `since` (str, optional): Time range to search. Default: `"1h"`
  - Relative: `"30m"`, `"2h"`, `"1d"`, `"7d"`
  - Absolute: `"2025-01-10"`, `"2025-01-10T14:30:00"`
- `limit` (int, optional): Maximum exceptions to return. Default: `10`
- `db_path` (str, optional): Path to database

**Returns:**

Dictionary with keys:
- `exceptions` (list): List of exception dictionaries
- `total` (int): Total count of exceptions in time range
- `time_range` (str): Original time range string
- `since_datetime` (str): ISO format datetime of range start

**Raises:**

- `QueryError`: If query fails or time range is invalid

**Examples:**

Find exceptions in last hour:
```python
from breadcrumb.storage.query import find_exceptions

result = find_exceptions(since="1h", limit=10)

print(f"Found {result['total']} exceptions")
for exc in result['exceptions']:
    print(f"{exc['exception_type']}: {exc['exception_message']}")
```

Find exceptions since specific date:
```python
result = find_exceptions(since="2025-01-10", limit=20)
```

#### `analyze_performance()`

Analyze performance statistics for a function.

**Signature:**

```python
def analyze_performance(
    function: str,
    limit: int = 10,
    db_path: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**

- `function` (str): Function name to analyze
- `limit` (int, optional): Number of slowest traces to return. Default: `10`
- `db_path` (str, optional): Path to database

**Returns:**

Dictionary with keys:
- `stats` (dict or None): Statistics dictionary with:
  - `call_count` (int): Total number of calls
  - `avg_duration_ms` (float): Average duration in milliseconds
  - `min_duration_ms` (float): Minimum duration
  - `max_duration_ms` (float): Maximum duration
- `slowest_traces` (list): List of slowest trace dictionaries
- `function` (str): Function name

If no data found for function, `stats` will be `None`.

**Raises:**

- `QueryError`: If query fails

**Example:**

```python
from breadcrumb.storage.query import analyze_performance

result = analyze_performance("process_data", limit=10)

if result['stats']:
    stats = result['stats']
    print(f"Function: {result['function']}")
    print(f"Call count: {stats['call_count']}")
    print(f"Average: {stats['avg_duration_ms']:.2f}ms")
    print(f"Min: {stats['min_duration_ms']:.2f}ms")
    print(f"Max: {stats['max_duration_ms']:.2f}ms")

    print("\nSlowest traces:")
    for trace in result['slowest_traces']:
        print(f"  {trace['id']}: {trace['duration_ms']:.2f}ms")
else:
    print("No data found for function")
```

---

## MCP Tools

Breadcrumb provides 4 MCP tools for AI agents. All tools return JSON strings.

### breadcrumb__query_traces

Execute SQL queries against the trace database.

**Parameters:**

- `sql` (string, required): SQL SELECT query to execute

**Returns:**

JSON string with:
```json
{
  "traces": [...],           // Query results
  "total": 10,               // Number of results
  "query_time_ms": 42,       // Query execution time
  "schema_version": "1.0.0", // Database schema version
  "warning": "..."           // Optional: if results truncated
}
```

**Error Response:**

```json
{
  "error": "ErrorType",
  "message": "Error description",
  "suggestion": "How to fix"
}
```

**Error Types:**

- `QueryTimeoutError`: Query exceeded 30 second timeout
- `InvalidQueryError`: Invalid SQL or unsafe operation
- `EmptyDatabaseError`: No traces in database

**Example Usage:**

```
breadcrumb__query_traces(sql="SELECT * FROM traces WHERE status='failed' LIMIT 10")
```

**Available Tables:**

- `traces`: Trace metadata (id, status, started_at, ended_at, duration_ms)
- `trace_events`: Function calls and returns (trace_id, event_type, function_name, args, return_value)
- `exceptions`: Exception records (trace_id, exception_type, exception_message, stack_trace)

### breadcrumb__get_trace

Get complete trace details by ID.

**Parameters:**

- `trace_id` (string, required): UUID of trace to retrieve

**Returns:**

JSON string with:
```json
{
  "trace": {...},      // Trace metadata
  "events": [...],     // All trace events
  "exceptions": [...], // All exceptions
  "summary": {
    "trace_id": "...",
    "status": "failed",
    "event_count": 10,
    "exception_count": 1
  }
}
```

**Error Response:**

```json
{
  "error": "TraceNotFoundError",
  "message": "No trace found with ID: ...",
  "suggestion": "Use breadcrumb__query_traces to find available trace IDs"
}
```

**Example Usage:**

```
breadcrumb__get_trace(trace_id="123e4567-e89b-12d3-a456-426614174000")
```

### breadcrumb__find_exceptions

Find exceptions within a time range.

**Parameters:**

- `since` (string, optional): Time range to search. Default: `"1h"`
  - Relative: `"30m"`, `"2h"`, `"1d"`, `"7d"`
  - Absolute: `"2025-01-10"`, `"2025-01-10T14:30:00"`
- `limit` (int, optional): Maximum exceptions to return. Default: `10`

**Returns:**

JSON string with:
```json
{
  "exceptions": [...],  // List of exceptions
  "total": 5,           // Total count in time range
  "time_range": "1h",   // Original time range
  "limit": 10,          // Limit parameter
  "message": "..."      // Optional: if no exceptions found
}
```

**Error Response:**

```json
{
  "error": "ValueError",
  "message": "Invalid time range: ...",
  "suggestion": "Use relative time ('30m', '2h', '1d') or absolute time ('2025-01-10')"
}
```

**Example Usage:**

```
breadcrumb__find_exceptions(since="1h", limit=10)
breadcrumb__find_exceptions(since="2025-01-10", limit=5)
```

### breadcrumb__analyze_performance

Analyze performance statistics for a function.

**Parameters:**

- `function` (string, required): Name of function to analyze
- `limit` (int, optional): Number of slowest traces to return. Default: `10`

**Returns:**

JSON string with:
```json
{
  "function": "process_data",
  "statistics": {
    "call_count": 100,
    "avg_duration_ms": 150.5,
    "min_duration_ms": 10.2,
    "max_duration_ms": 500.3
  },
  "slowest_traces": [...]
}
```

**Error Response:**

```json
{
  "error": "FunctionNotFound",
  "message": "No traces found for function: ...",
  "suggestion": "Check function name spelling. Use breadcrumb__query_traces to find available functions"
}
```

**Example Usage:**

```
breadcrumb__analyze_performance(function="fetch_data", limit=10)
```

---

## CLI Commands

### Global Options

All commands support these global options:

```bash
--format json|table    # Output format (default: json)
--db-path PATH         # Custom database path (auto-discovered)
--verbose              # Enable verbose output
--version              # Show version and exit
```

**Examples:**

```bash
breadcrumb list --format table
breadcrumb query "SELECT * FROM traces" --db-path /custom/path/traces.db
breadcrumb --version
```

---

### list

List recent traces.

**Syntax:**

```bash
breadcrumb list [--limit N]
```

**Options:**

- `--limit N`, `-n N`: Number of traces to show (default: 10)

**Exit Codes:**

- `0`: Success
- `1`: Error (database not found, query failed)
- `2`: No results found

**Examples:**

```bash
# List 10 most recent traces (JSON)
breadcrumb list

# List 20 traces in table format
breadcrumb list --limit 20 --format table

# List with custom database
breadcrumb list --db-path /path/to/traces.db
```

**Output (JSON):**

```json
{
  "traces": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "success",
      "started_at": "2025-01-10T14:30:00",
      "duration_ms": 150.5
    }
  ],
  "total": 10
}
```

**Output (Table):**

```
Trace ID                              Status    Started At           Duration
123e4567-e89b-12d3-a456-426614174000  success   2025-01-10 14:30:00  150.5ms
```

---

### get

Get detailed trace by ID.

**Syntax:**

```bash
breadcrumb get <trace-id>
```

**Arguments:**

- `trace-id`: UUID of trace to retrieve (required)

**Exit Codes:**

- `0`: Success
- `1`: Error (trace not found, database error)

**Examples:**

```bash
# Get trace details (JSON)
breadcrumb get 123e4567-e89b-12d3-a456-426614174000

# Get trace in table format
breadcrumb get 123e4567-e89b-12d3-a456-426614174000 --format table
```

**Output (JSON):**

```json
{
  "trace": {...},
  "events": [...],
  "exceptions": [...],
  "summary": {
    "event_count": 10,
    "exception_count": 1
  }
}
```

---

### query

Execute SQL query against trace database.

**Syntax:**

```bash
breadcrumb query <sql>
```

**Arguments:**

- `sql`: SQL SELECT query to execute (required, must be quoted)

**Exit Codes:**

- `0`: Success
- `1`: Error (invalid SQL, unsafe query, database error)
- `2`: No results found

**Examples:**

```bash
# Get all failed traces
breadcrumb query "SELECT * FROM traces WHERE status='failed'"

# Count function calls
breadcrumb query "SELECT function_name, COUNT(*) as calls FROM trace_events GROUP BY function_name"

# Find slow traces
breadcrumb query "SELECT id, duration_ms FROM traces WHERE duration_ms > 1000 ORDER BY duration_ms DESC"
```

**Output (JSON):**

```json
{
  "results": [...],
  "total": 5,
  "query_time_ms": 42
}
```

---

### exceptions

Find recent exceptions.

**Syntax:**

```bash
breadcrumb exceptions [--since TIME] [--limit N]
```

**Options:**

- `--since TIME`, `-s TIME`: Time range (default: "1h")
  - Relative: "30m", "2h", "1d", "7d"
  - Absolute: "2025-01-10", "2025-01-10T14:30:00"
- `--limit N`, `-n N`: Maximum exceptions to show (default: 10)

**Exit Codes:**

- `0`: Success
- `1`: Error (invalid time range, database error)
- `2`: No exceptions found

**Examples:**

```bash
# Find exceptions in last hour
breadcrumb exceptions

# Find exceptions in last 30 minutes
breadcrumb exceptions --since 30m --limit 5

# Find exceptions since specific date
breadcrumb exceptions --since 2025-01-10

# Table format
breadcrumb exceptions --format table
```

**Output (JSON):**

```json
{
  "exceptions": [...],
  "total": 3,
  "time_range": "1h",
  "limit": 10
}
```

---

### performance

Analyze performance statistics for a function.

**Syntax:**

```bash
breadcrumb performance <function> [--limit N]
```

**Arguments:**

- `function`: Function name to analyze (required)

**Options:**

- `--limit N`, `-n N`: Number of slowest traces to show (default: 10)

**Exit Codes:**

- `0`: Success
- `1`: Error (database error)
- `2`: No data found for function

**Examples:**

```bash
# Analyze function performance
breadcrumb performance process_data

# Show top 5 slowest traces
breadcrumb performance fetch_api --limit 5

# Table format
breadcrumb performance my_function --format table
```

**Output (JSON):**

```json
{
  "function": "process_data",
  "statistics": {
    "call_count": 100,
    "avg_duration_ms": 150.5,
    "min_duration_ms": 10.2,
    "max_duration_ms": 500.3
  },
  "slowest_traces": [...]
}
```

---

### serve-mcp

Start MCP server for AI agents.

**Syntax:**

```bash
breadcrumb serve-mcp [--db-path PATH] [--port PORT]
```

**Options:**

- `--db-path PATH`: Custom database path (auto-discovered if not provided)
- `--port PORT`: Port for TCP transport (future feature, currently stdio only)

**Exit Codes:**

- `0`: Success (server stopped gracefully)
- `1`: Error (database not found, startup error)

**Examples:**

```bash
# Start MCP server (stdio transport)
breadcrumb serve-mcp

# Start with custom database
breadcrumb serve-mcp --db-path /path/to/traces.db
```

**Usage with Claude Desktop:**

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "breadcrumb": {
      "command": "breadcrumb",
      "args": ["serve-mcp"]
    }
  }
}
```

---

## Database Schema

Breadcrumb uses DuckDB with the following schema:

### traces Table

Stores trace metadata.

**Columns:**

- `id` (VARCHAR, PRIMARY KEY): Trace UUID
- `status` (VARCHAR): 'success', 'failed', or 'running'
- `started_at` (TIMESTAMP): Trace start time
- `ended_at` (TIMESTAMP): Trace end time (NULL if running)
- `duration_ms` (DOUBLE): Duration in milliseconds
- `metadata` (JSON): Additional trace metadata

**Indexes:**

- Primary key on `id`
- Index on `status`
- Index on `started_at`

### trace_events Table

Stores function calls and returns.

**Columns:**

- `id` (VARCHAR, PRIMARY KEY): Event UUID
- `trace_id` (VARCHAR, FOREIGN KEY): Parent trace ID
- `event_type` (VARCHAR): 'call' or 'return'
- `function_name` (VARCHAR): Function name
- `module_name` (VARCHAR): Module containing function
- `file_path` (VARCHAR): File path
- `line_number` (INTEGER): Line number
- `timestamp` (TIMESTAMP): Event timestamp
- `args` (JSON): Function arguments (for 'call' events)
- `return_value` (JSON): Return value (for 'return' events)
- `locals` (JSON): Local variables (optional)

**Indexes:**

- Primary key on `id`
- Index on `trace_id`
- Index on `function_name`
- Index on `event_type`

### exceptions Table

Stores exception records.

**Columns:**

- `id` (VARCHAR, PRIMARY KEY): Exception UUID
- `trace_id` (VARCHAR, FOREIGN KEY): Parent trace ID
- `exception_type` (VARCHAR): Exception class name (e.g., 'ValueError')
- `exception_message` (TEXT): Exception message
- `stack_trace` (TEXT): Full stack trace
- `file_path` (VARCHAR): File where exception occurred
- `line_number` (INTEGER): Line number
- `timestamp` (TIMESTAMP): Exception timestamp

**Indexes:**

- Primary key on `id`
- Index on `trace_id`
- Index on `exception_type`

### Direct SQL Access

You can query the database directly using DuckDB:

```python
import duckdb

conn = duckdb.connect('.breadcrumb/traces.duckdb')
result = conn.execute("SELECT * FROM traces").fetchall()
conn.close()
```

---

## Error Handling

### Exception Hierarchy

```
Exception
└── QueryError (base for all query errors)
    ├── InvalidQueryError (unsafe or malformed SQL)
    ├── TraceNotFoundError (trace ID not found)
    └── QueryTimeoutError (query exceeded timeout)
```

### Common Errors

#### Database Not Found

**Error:** `FileNotFoundError: Could not find .breadcrumb/traces.duckdb`

**Solution:**
1. Initialize Breadcrumb in your code: `import breadcrumb; breadcrumb.init()`
2. Run your application to generate traces
3. Verify `.breadcrumb/traces.duckdb` exists

#### Empty Database

**Error:** `EmptyDatabaseError: No traces found in database`

**Solution:**
1. Run your application with Breadcrumb initialized
2. Verify tracing is enabled: `breadcrumb.init(enabled=True)`
3. Check that your code is being executed

#### Invalid SQL

**Error:** `InvalidQueryError: Only SELECT queries are allowed`

**Solution:**
Use only SELECT queries. INSERT, UPDATE, DELETE, etc. are not allowed for safety.

#### Query Timeout

**Error:** `QueryTimeoutError: Query exceeded 30 second timeout`

**Solution:**
1. Add LIMIT clause to reduce result set
2. Use more selective WHERE conditions
3. Add indexes if querying large datasets

### Error Handling Best Practices

**Python API:**

```python
from breadcrumb.storage.query import (
    query_traces,
    QueryError,
    InvalidQueryError,
    TraceNotFoundError,
    QueryTimeoutError
)

try:
    results = query_traces("SELECT * FROM traces")
except QueryTimeoutError:
    print("Query too slow, try adding LIMIT")
except InvalidQueryError as e:
    print(f"Invalid query: {e}")
except TraceNotFoundError:
    print("Trace not found")
except QueryError as e:
    print(f"Query failed: {e}")
```

**CLI:**

Exit codes indicate error type:
- `0`: Success
- `1`: Error (check stderr for details)
- `2`: No results found

```bash
breadcrumb query "SELECT * FROM traces" || echo "Query failed: $?"
```

---

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide for AI agents
- [SECURITY.md](SECURITY.md) - Security and privacy documentation
- [README.md](../README.md) - Main documentation
