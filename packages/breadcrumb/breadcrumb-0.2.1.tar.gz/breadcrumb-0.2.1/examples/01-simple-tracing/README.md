# Example 1: Simple Function Tracing

**Learning Objective**: Understand how to initialize Breadcrumb and trace basic function calls.

## What This Example Demonstrates

- Zero-config tracing with `breadcrumb.init()`
- Automatic function call capture
- Basic trace querying with CLI
- Understanding trace structure (traces, events, arguments)

## Prerequisites

1. Breadcrumb installed:
   ```bash
   cd /path/to/breadcrumb
   uv pip install -e .
   # or: pip install -e .
   ```

2. Python 3.12+ (or 3.10+ for sys.settrace fallback)

## How to Run

```bash
# From this directory
python main.py
```

## Expected Output

```
============================================================
Breadcrumb Example 1: Simple Function Tracing
============================================================

1. Testing add function:
   add(5, 3) = 8

2. Testing multiply function:
   multiply(7, 6) = 42

3. Testing greet function:
   greet('Alice') = 'Hello, Alice!'

4. Testing complex calculation:
   calculate_total(100, 2, 0.15) = $230.00

============================================================
Execution complete! Traces captured.
============================================================

Next Steps:
  1. Run: breadcrumb list
  2. Run: breadcrumb query "SELECT * FROM events WHERE function_name='add'"
  3. See README.md for more query examples
```

## Trace Queries

After running the example, try these queries:

### Using CLI

```bash
# List all recent traces
breadcrumb list

# Show the most recent trace with all events
breadcrumb get <trace-id>

# Find all calls to the 'add' function
breadcrumb query "SELECT * FROM events WHERE function_name='add'"

# Find all calls to 'multiply' with their arguments
breadcrumb query "SELECT function_name, arguments FROM events WHERE function_name='multiply'"

# See all function calls in order
breadcrumb query "SELECT timestamp, function_name, file_path, line_number FROM events ORDER BY timestamp"
```

### Using MCP (Claude Desktop)

Ask Claude:

- "Show me the last trace from Breadcrumb"
- "What functions were called in the most recent trace?"
- "Show me all calls to the 'add' function with their arguments"
- "What was the execution order of functions?"

Claude will use the Breadcrumb MCP tools:
- `breadcrumb__query_traces` - Execute SQL queries
- `breadcrumb__get_trace` - Get trace details
- `breadcrumb__analyze_performance` - Analyze function performance

## Understanding the Trace Structure

Breadcrumb captures:

1. **Traces**: Top-level execution sessions
   - `id`: Unique trace identifier
   - `status`: completed, failed, running
   - `started_at`, `ended_at`: Timestamps
   - `thread_id`: Thread identifier

2. **Events**: Individual function calls/returns/exceptions
   - `event_type`: call, return, exception, line
   - `function_name`: Name of the function
   - `file_path`: Source file location
   - `line_number`: Line in source code
   - `arguments`: Function arguments (JSON)
   - `return_value`: Return value (JSON)
   - `timestamp`: When the event occurred

3. **Exceptions**: Error details (none in this example)
   - `exception_type`: Type of exception
   - `exception_message`: Error message
   - `traceback`: Full stack trace

## Code Explanation

```python
import breadcrumb

# Initialize Breadcrumb - this starts tracing automatically
breadcrumb.init()

# All functions are now traced automatically
def add(a, b):
    return a + b  # Arguments and return value captured
```

When you call `add(5, 3)`, Breadcrumb captures:
- Function entry event with arguments `{"a": 5, "b": 3}`
- Function return event with return value `8`
- Timing information
- Source location (file, line number)

## What You Learned

1. **Zero Configuration**: Just `import breadcrumb; breadcrumb.init()` and tracing starts
2. **Automatic Capture**: All function calls, arguments, and return values are tracked
3. **SQL Queries**: Use standard SQL to query your execution data
4. **AI Integration**: Claude can query traces using MCP tools

## Next Steps

1. **Example 2**: Learn async/await tracing → `../02-async-tracing/`
2. **Example 3**: Debug exceptions with traces → `../03-exception-debugging/`
3. **Example 4**: Profile performance bottlenecks → `../04-performance-profiling/`

## Troubleshooting

**Problem**: No traces appear

**Solution**:
- Check that Breadcrumb is installed: `python -c "import breadcrumb; print(breadcrumb.__version__)"`
- Check database exists: `ls -la .breadcrumb/traces.duckdb`
- Enable debug logging: `export BREADCRUMB_LOG_LEVEL=DEBUG`

**Problem**: "Module not found: breadcrumb"

**Solution**:
- Install Breadcrumb: `uv pip install -e /path/to/breadcrumb`
- Or adjust `sys.path` in the example

**Problem**: Permission denied on database

**Solution**:
- Check `.breadcrumb/` directory permissions
- Try running with: `breadcrumb init --reset` to recreate the database
