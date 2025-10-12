# Breadcrumb AI Tracer - Quickstart for AI Agents

**This guide is optimized for AI agents like Claude Code to understand and use Breadcrumb tools effectively.**

## What is Breadcrumb?

Breadcrumb is a Python execution tracer that automatically captures function calls, arguments, return values, and exceptions. It stores this data in a queryable database and exposes it through Model Context Protocol (MCP) tools.

**Key concept**: When Python code runs with Breadcrumb initialized, every function call is traced and stored. You can then query this trace data to understand execution flow, find bugs, and analyze performance.

## Available MCP Tools

Breadcrumb provides 4 MCP tools for AI agents:

### 1. breadcrumb__query_traces

**Purpose**: Execute SQL queries against the trace database

**Parameters**:
- `sql` (string): SQL SELECT query to execute

**Returns**: JSON with query results, total count, and query time

**Use cases**:
- Find all failed traces
- List functions that were called
- Search for specific argument values
- Aggregate statistics

**Example queries**:

```sql
-- Get 10 most recent traces
SELECT * FROM traces ORDER BY started_at DESC LIMIT 10

-- Find all failed traces
SELECT * FROM traces WHERE status = 'failed'

-- List all function calls with their frequency
SELECT function_name, COUNT(*) as calls
FROM trace_events
WHERE event_type = 'call'
GROUP BY function_name
ORDER BY calls DESC

-- Find traces that took longer than 1 second
SELECT trace_id, duration_ms
FROM traces
WHERE duration_ms > 1000
ORDER BY duration_ms DESC

-- Search for specific function calls
SELECT * FROM trace_events
WHERE function_name = 'process_data'
AND event_type = 'call'
```

**Database schema**:

**traces** table:
- `trace_id` (UUID): Unique trace identifier
- `status` (string): 'success', 'failed', or 'running'
- `started_at` (timestamp): When trace started
- `finished_at` (timestamp): When trace finished
- `duration_ms` (float): Execution time in milliseconds

**trace_events** table:
- `event_id` (UUID): Unique event identifier
- `trace_id` (UUID): Parent trace ID
- `event_type` (string): 'call' or 'return'
- `function_name` (string): Function that was called
- `module_name` (string): Module containing the function
- `file_path` (string): File path
- `line_number` (int): Line number
- `timestamp` (timestamp): When event occurred
- `args` (JSON): Function arguments (for 'call' events)
- `return_value` (JSON): Return value (for 'return' events)

**exceptions** table:
- `exception_id` (UUID): Unique exception identifier
- `trace_id` (UUID): Parent trace ID
- `exception_type` (string): Exception class name (e.g., 'ValueError')
- `exception_message` (string): Exception message
- `stack_trace` (string): Full stack trace
- `file_path` (string): File where exception occurred
- `line_number` (int): Line number
- `timestamp` (timestamp): When exception occurred

### 2. breadcrumb__get_trace

**Purpose**: Get complete details for a specific trace

**Parameters**:
- `trace_id` (string): UUID of the trace to retrieve

**Returns**: JSON with trace metadata, all events, and exceptions

**Use cases**:
- Investigate a specific execution
- Understand the full call flow for one trace
- See all variables and return values for an execution

**Example usage**:

```
breadcrumb__get_trace(trace_id="123e4567-e89b-12d3-a456-426614174000")
```

**Response format**:

```json
{
  "trace": {
    "trace_id": "...",
    "status": "failed",
    "started_at": "2025-01-10T14:30:00",
    "finished_at": "2025-01-10T14:30:02",
    "duration_ms": 2000.5
  },
  "events": [
    {
      "event_type": "call",
      "function_name": "process_data",
      "args": {"x": 10, "y": 20},
      "timestamp": "2025-01-10T14:30:00"
    },
    {
      "event_type": "return",
      "function_name": "process_data",
      "return_value": 30,
      "timestamp": "2025-01-10T14:30:02"
    }
  ],
  "exceptions": [
    {
      "exception_type": "ValueError",
      "exception_message": "Invalid input",
      "stack_trace": "...",
      "timestamp": "2025-01-10T14:30:01"
    }
  ],
  "summary": {
    "trace_id": "...",
    "status": "failed",
    "event_count": 2,
    "exception_count": 1
  }
}
```

### 3. breadcrumb__find_exceptions

**Purpose**: Find exceptions within a time range

**Parameters**:
- `since` (string, default: "1h"): Time range to search
  - Relative: "30m", "2h", "1d", "7d"
  - Absolute: "2025-01-10", "2025-01-10T14:30:00"
- `limit` (int, default: 10): Maximum number of exceptions to return

**Returns**: JSON with exception list, total count, and time range

**Use cases**:
- Debug recent failures
- Find all occurrences of a specific exception type
- Understand what's been failing in the last hour/day

**Example usage**:

```
-- Find exceptions in last hour
breadcrumb__find_exceptions(since="1h", limit=10)

-- Find exceptions in last 30 minutes
breadcrumb__find_exceptions(since="30m", limit=5)

-- Find exceptions since specific date
breadcrumb__find_exceptions(since="2025-01-10", limit=20)
```

**Response format**:

```json
{
  "exceptions": [
    {
      "exception_id": "...",
      "trace_id": "...",
      "exception_type": "ValueError",
      "exception_message": "Invalid input: x must be positive",
      "file_path": "/path/to/file.py",
      "line_number": 42,
      "timestamp": "2025-01-10T14:30:00"
    }
  ],
  "total": 1,
  "time_range": {
    "since": "2025-01-10T13:30:00",
    "until": "2025-01-10T14:30:00"
  },
  "limit": 10
}
```

### 4. breadcrumb__analyze_performance

**Purpose**: Analyze performance statistics for a specific function

**Parameters**:
- `function` (string): Name of the function to analyze
- `limit` (int, default: 10): Number of slowest traces to return

**Returns**: JSON with statistics (avg/min/max duration) and slowest traces

**Use cases**:
- Find performance bottlenecks
- See which calls to a function are slowest
- Understand typical vs worst-case performance

**Example usage**:

```
breadcrumb__analyze_performance(function="process_data", limit=10)
breadcrumb__analyze_performance(function="fetch_api", limit=5)
```

**Response format**:

```json
{
  "function": "process_data",
  "statistics": {
    "call_count": 100,
    "avg_duration_ms": 150.5,
    "min_duration_ms": 10.2,
    "max_duration_ms": 500.3
  },
  "slowest_traces": [
    {
      "trace_id": "...",
      "duration_ms": 500.3,
      "timestamp": "2025-01-10T14:30:00",
      "args": {"x": 1000000}
    },
    {
      "trace_id": "...",
      "duration_ms": 450.1,
      "timestamp": "2025-01-10T14:25:00",
      "args": {"x": 900000}
    }
  ]
}
```

## Common Use Cases

### Finding the Last Exception

**User request**: "What was the last exception?"

**Solution**:

```
Use: breadcrumb__find_exceptions(since="1h", limit=1)
```

**Alternative** (if you need more control):

```sql
Use: breadcrumb__query_traces with SQL:
SELECT * FROM exceptions ORDER BY timestamp DESC LIMIT 1
```

### Understanding Execution Flow

**User request**: "Show me what happened in trace abc-123"

**Solution**:

```
Use: breadcrumb__get_trace(trace_id="abc-123")
```

Then analyze the events array to understand the call sequence.

### Finding Performance Bottlenecks

**User request**: "Which function is slowest?"

**Solution**:

```sql
Step 1: Use breadcrumb__query_traces with SQL:
SELECT function_name, AVG(duration_ms) as avg_ms
FROM trace_events
WHERE event_type = 'call'
GROUP BY function_name
ORDER BY avg_ms DESC
LIMIT 10

Step 2: For the slowest function, use:
breadcrumb__analyze_performance(function="<slowest_function>", limit=10)
```

### Debugging Specific Function

**User request**: "Why is process_data failing?"

**Solution**:

```sql
Step 1: Find failed traces with this function:
Use breadcrumb__query_traces with SQL:
SELECT t.trace_id, t.status, e.exception_type, e.exception_message
FROM traces t
JOIN trace_events te ON t.trace_id = te.trace_id
LEFT JOIN exceptions e ON t.trace_id = e.trace_id
WHERE te.function_name = 'process_data' AND t.status = 'failed'
LIMIT 10

Step 2: Investigate specific trace:
Use breadcrumb__get_trace(trace_id="<one_of_the_failed_traces>")
```

### Finding All Calls to a Function

**User request**: "How many times was calculate called?"

**Solution**:

```sql
Use breadcrumb__query_traces with SQL:
SELECT COUNT(*) as total_calls
FROM trace_events
WHERE function_name = 'calculate' AND event_type = 'call'
```

Or to see the actual calls:

```sql
SELECT * FROM trace_events
WHERE function_name = 'calculate' AND event_type = 'call'
ORDER BY timestamp DESC
LIMIT 20
```

### Analyzing Argument Patterns

**User request**: "What values were passed to process_data?"

**Solution**:

```sql
Use breadcrumb__query_traces with SQL:
SELECT args, COUNT(*) as frequency
FROM trace_events
WHERE function_name = 'process_data' AND event_type = 'call'
GROUP BY args
ORDER BY frequency DESC
LIMIT 10
```

## Tips for Effective Queries

### 1. Start Broad, Then Narrow

First get an overview:
```sql
SELECT * FROM traces ORDER BY started_at DESC LIMIT 10
```

Then drill down into specific traces:
```
breadcrumb__get_trace(trace_id="...")
```

### 2. Use Time Ranges

For recent activity, use `breadcrumb__find_exceptions` with time ranges:
- `"30m"` - Last 30 minutes
- `"1h"` - Last hour
- `"1d"` - Last day

### 3. Filter by Status

Focus on failures:
```sql
SELECT * FROM traces WHERE status = 'failed'
```

Or successful executions:
```sql
SELECT * FROM traces WHERE status = 'success'
```

### 4. Join Tables for Context

Get exceptions with their trace context:
```sql
SELECT t.trace_id, t.started_at, e.exception_type, e.exception_message
FROM traces t
JOIN exceptions e ON t.trace_id = e.trace_id
ORDER BY t.started_at DESC
```

### 5. Use Aggregations

Find patterns:
```sql
-- Most common exceptions
SELECT exception_type, COUNT(*) as count
FROM exceptions
GROUP BY exception_type
ORDER BY count DESC

-- Average function performance
SELECT function_name, AVG(duration_ms) as avg_ms, COUNT(*) as calls
FROM trace_events
WHERE event_type = 'call'
GROUP BY function_name
HAVING calls > 10
ORDER BY avg_ms DESC
```

### 6. Limit Result Sets

Always use LIMIT to avoid overwhelming responses:
```sql
SELECT * FROM traces LIMIT 10
```

The MCP server automatically truncates responses over 1MB.

## Error Handling

### Empty Database

If no traces exist, you'll see:
```json
{
  "error": "EmptyDatabaseError",
  "message": "No traces found in database",
  "suggestion": "To start tracing, add 'import breadcrumb; breadcrumb.init()' to your Python code"
}
```

**Solution**: User needs to initialize Breadcrumb in their Python code and run it.

### Invalid SQL

```json
{
  "error": "InvalidQueryError",
  "message": "Syntax error near 'SEELCT'",
  "suggestion": "Check SQL syntax and ensure only SELECT queries are used"
}
```

**Solution**: Fix the SQL syntax. Only SELECT queries are allowed for safety.

### Trace Not Found

```json
{
  "error": "TraceNotFoundError",
  "message": "No trace found with ID: abc-123",
  "suggestion": "Use breadcrumb__query_traces to find available trace IDs"
}
```

**Solution**: Query the database to find valid trace IDs.

### Query Timeout

```json
{
  "error": "QueryTimeoutError",
  "message": "Query exceeded 30 second timeout",
  "suggestion": "Use LIMIT to reduce result set or simplify your query"
}
```

**Solution**: Add LIMIT clause or use more selective WHERE conditions.

## CLI Alternative

Users can also interact with Breadcrumb via CLI instead of MCP tools:

### Smart Queries (No SQL Needed!)

**New in Phase 2**: Semantic query commands that don't require SQL knowledge:

```bash
# Show untraced function calls (gaps in coverage)
breadcrumb query --gaps

# Show function call details (args, returns, duration)
breadcrumb query --call Pizza
breadcrumb query --call calculate_total

# Show execution timeline
breadcrumb query --flow
breadcrumb query --flow --module flock  # Filter by module
```

**Use cases**:
- `--gaps`: Discover what's not being traced, get suggestions for include patterns
- `--call <function>`: See function arguments, return values, execution time
- `--flow`: Understand chronological execution order with nesting

### Traditional Commands

```bash
# List recent traces
breadcrumb list --limit 10

# Get specific trace
breadcrumb get <trace-id>

# Find exceptions
breadcrumb exceptions --since 1h --limit 10

# Analyze performance
breadcrumb performance <function-name>

# Execute custom SQL (still supported!)
breadcrumb query "SELECT * FROM traces"

# Start MCP server
breadcrumb serve-mcp
```

The CLI supports both JSON (for programmatic use) and table (for human reading) formats:

```bash
breadcrumb list --format table
breadcrumb exceptions --format json
breadcrumb query --gaps --format json  # Smart queries always return JSON
```

## Setup Instructions for Users

If a user wants to use Breadcrumb, guide them through:

### 1. Install Breadcrumb

```bash
cd breadcrumb
uv pip install -e .
```

### 2. Initialize in Their Code

```python
import breadcrumb
breadcrumb.init()

# Their existing code here
```

### 3. Run Their Code

```bash
python their_script.py
```

### 4. Query Traces

Now you can use the MCP tools to query the traces.

### 5. Configure MCP Server (for Claude Desktop)

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

## Advanced Features

### Selective Instrumentation

Users can control what gets traced:

```python
breadcrumb.init(
    include=["src/**/*.py"],    # Only trace src/ directory (include-only workflow)
)
```

### Sampling

Reduce overhead by sampling:

```python
breadcrumb.init(sample_rate=0.1)  # Trace 10% of calls
```

### Custom Database Path

```python
breadcrumb.init(db_path="/custom/path/traces.duckdb")
```

Or via environment variable:
```bash
export BREADCRUMB_DB_PATH="/custom/path/traces.duckdb"
```

## Secret Redaction

Breadcrumb automatically redacts sensitive data. The following will be `[REDACTED]`:

- Passwords, secrets, tokens
- API keys, access tokens
- Credit card numbers
- SSNs
- JWTs
- AWS keys, GitHub tokens

When you query traces, sensitive values appear as `[REDACTED]`.

## Summary

As an AI agent, you have 4 powerful tools to understand Python execution:

1. **breadcrumb__query_traces**: SQL queries for flexible analysis
2. **breadcrumb__get_trace**: Deep dive into specific executions
3. **breadcrumb__find_exceptions**: Quickly find errors
4. **breadcrumb__analyze_performance**: Identify bottlenecks

Use SQL queries for exploratory analysis, and specialized tools for common debugging tasks.
