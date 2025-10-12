# Example 3: Exception Debugging

**Learning Objective**: Learn how to use Breadcrumb to debug exceptions by tracing execution flow and identifying root causes.

## What This Example Demonstrates

- Capturing exceptions with full context
- Tracing back from error to root cause
- Analyzing function arguments that caused failures
- Comparing failed vs successful executions
- Common Python exception patterns (AttributeError, KeyError, ZeroDivisionError, etc.)

## Prerequisites

1. Breadcrumb installed (see Example 1)
2. Python 3.12+ (or 3.10+ for sys.settrace fallback)
3. Understanding of Python exceptions

## How to Run

```bash
# From this directory
python main.py
```

## Expected Output

The script intentionally triggers various exceptions and shows how to debug them:

```
============================================================
Breadcrumb Example 3: Exception Debugging
============================================================

This example intentionally triggers errors to demonstrate
how Breadcrumb helps you debug exceptions.

============================================================
Example 1: NoneType Attribute Access
============================================================
Problem: Trying to process order for non-existent user

ERROR: 'NoneType' object has no attribute 'name'

How to debug with Breadcrumb:
  1. Run: breadcrumb exceptions --since 1m
  2. Find the exception trace
  3. Look at the arguments passed to process_order()
  4. See that load_user_data() returned None
  5. Root cause: User 999 doesn't exist in database

[... more examples ...]
```

## The Debugging Challenge

Each example presents a bug. Your task: use Breadcrumb to find the root cause!

### Example 1: NoneType Attribute Access

**Error**: `'NoneType' object has no attribute 'name'`

**What happened?**
- Called `process_order(user_id=999, ...)`
- User 999 doesn't exist in database
- `load_user_data()` returned `None`
- Code tried to access `None.name` → crash!

**Root cause**: Missing validation for non-existent users.

### Example 2: Division By Zero

**Error**: `division by zero`

**What happened?**
- Called `calculate_discount(100, 100)` (100% discount)
- Formula: `100 / (100 - 100)` = `100 / 0`
- Division by zero!

**Root cause**: Discount logic doesn't handle 100% discount.

### Example 3: KeyError

**Error**: `KeyError: 'address'`

**What happened?**
- Tried to access `data["user"]["profile"]["address"]["city"]`
- `data["user"]["profile"]` exists
- `data["user"]["profile"]["address"]` does NOT exist
- KeyError on missing `"address"` key

**Root cause**: Accessing nested key that doesn't exist.

### Example 4: None Value in Required Field

**Error**: `'NoneType' object has no attribute 'split'`

**What happened?**
- User 3 has `email=None` in database
- Called `user.get_domain()` which does `email.split('@')`
- `None.split('@')` → crash!

**Root cause**: Database contains None email, code assumes email is always a string.

## Debugging Workflow with Breadcrumb

### Step 1: Find Recent Exceptions

```bash
breadcrumb exceptions --since 10m
```

Output:
```
Recent Exceptions (last 10 minutes):

1. AttributeError: 'NoneType' object has no attribute 'name'
   Function: process_order
   File: main.py:55
   Trace ID: abc123...
   Time: 2025-10-11 10:30:45

2. ZeroDivisionError: division by zero
   Function: calculate_discount
   File: main.py:42
   Trace ID: def456...
   Time: 2025-10-11 10:30:46

[... more exceptions ...]
```

### Step 2: Get Full Trace

```bash
breadcrumb get abc123
```

Output:
```
Trace: abc123

Status: failed
Started: 2025-10-11 10:30:45.123
Ended: 2025-10-11 10:30:45.234
Duration: 111ms

Events:
  1. process_order(user_id=999, items=[...])
  2. load_user_data(user_id=999)
  3. load_user_data → None  (USER NOT FOUND!)
  4. AttributeError: 'NoneType' object has no attribute 'name'
```

### Step 3: Analyze Arguments

```bash
breadcrumb query "
  SELECT function_name, arguments, return_value
  FROM events
  WHERE trace_id = 'abc123'
  ORDER BY timestamp
"
```

Output:
```
function_name      | arguments            | return_value
------------------ | -------------------- | ------------
process_order      | {user_id: 999, ...}  | NULL (exception)
load_user_data     | {user_id: 999}       | None
```

**Insight**: `load_user_data(999)` returned `None`, but `process_order` didn't check!

### Step 4: Find Root Cause

Trace backwards:
1. **Exception**: `'NoneType' object has no attribute 'name'` in `process_order`
2. **Proximate cause**: Variable `user` is `None`
3. **Source**: `user = load_user_data(999)` returned `None`
4. **Root cause**: User 999 doesn't exist in database

**Fix**: Add validation:
```python
user = load_user_data(user_id)
if user is None:
    raise ValueError(f"User {user_id} not found")
```

## Using MCP (Claude Desktop)

Ask Claude to help debug:

**You**: "I'm getting an AttributeError in my code. Can you help me debug it?"

**Claude**: *Uses `breadcrumb__find_exceptions`*

"I found an AttributeError: 'NoneType' object has no attribute 'name' in the `process_order` function. Let me get the full trace..."

*Uses `breadcrumb__get_trace`*

"Looking at the trace, I see that:
1. `process_order` was called with `user_id=999`
2. `load_user_data(999)` returned `None`
3. The code then tried to access `None.name`, causing the error

The root cause is that user 999 doesn't exist in your database, but the code doesn't check if `load_user_data` returns `None` before using it.

Here's how to fix it:
[... Claude suggests the fix ...]"

## Advanced Debugging Queries

### Find All Exceptions of a Specific Type

```bash
breadcrumb query "
  SELECT trace_id, function_name, exception_message, timestamp
  FROM exceptions
  WHERE exception_type = 'AttributeError'
  ORDER BY timestamp DESC
"
```

### Find Functions That Often Fail

```bash
breadcrumb query "
  SELECT
    function_name,
    COUNT(*) as error_count,
    COUNT(DISTINCT exception_type) as unique_errors
  FROM exceptions
  GROUP BY function_name
  ORDER BY error_count DESC
"
```

### Compare Successful vs Failed Calls

```bash
# Successful calls to process_order
breadcrumb query "
  SELECT arguments
  FROM events
  WHERE function_name = 'process_order'
    AND trace_id NOT IN (SELECT DISTINCT trace_id FROM exceptions)
"

# Failed calls to process_order
breadcrumb query "
  SELECT arguments
  FROM events
  WHERE function_name = 'process_order'
    AND trace_id IN (SELECT DISTINCT trace_id FROM exceptions)
"
```

### Find What Arguments Cause Failures

```bash
breadcrumb query "
  SELECT
    e.arguments,
    ex.exception_type,
    ex.exception_message
  FROM events e
  JOIN exceptions ex ON e.trace_id = ex.trace_id
  WHERE e.function_name = 'calculate_discount'
    AND e.event_type = 'call'
"
```

## What You Learned

1. **Exception Capture**: Breadcrumb automatically captures all exceptions with full context
2. **Stack Traces**: See the complete call chain leading to an error
3. **Argument Analysis**: Examine exactly what arguments caused a failure
4. **Root Cause Analysis**: Trace backwards from error to find the true cause
5. **Pattern Recognition**: Find common failure patterns across executions

## Common Exception Patterns

### Pattern 1: Missing Null Checks

```python
# BAD
user = get_user(id)
print(user.name)  # Crashes if user is None

# GOOD
user = get_user(id)
if user is None:
    raise ValueError(f"User {id} not found")
print(user.name)
```

**Breadcrumb insight**: Trace shows `get_user()` returned `None`

### Pattern 2: Missing Key Validation

```python
# BAD
value = data[key]  # Crashes if key doesn't exist

# GOOD
value = data.get(key)
if value is None:
    raise KeyError(f"Missing required key: {key}")
```

**Breadcrumb insight**: Trace shows `data` structure and missing key

### Pattern 3: Invalid Input Values

```python
# BAD
def divide(a, b):
    return a / b  # Crashes if b is 0

# GOOD
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**Breadcrumb insight**: Trace shows arguments `(a=10, b=0)`

## Next Steps

1. **Example 4**: Profile performance bottlenecks → `../04-performance-profiling/`
2. **Practice**: Introduce bugs in your own code and use Breadcrumb to debug
3. **Advanced**: Combine exception analysis with performance profiling

## Troubleshooting

**Problem**: Exceptions not appearing in breadcrumb exceptions

**Solution**: Make sure the exception occurred while tracing was active. Check that `breadcrumb.init()` was called before the error.

**Problem**: Stack trace is incomplete

**Solution**: Some exceptions may be caught and re-raised. Look for the original exception in the trace using `exception_type` and `exception_message`.

**Problem**: Too many exceptions to analyze

**Solution**: Filter by time period (`--since 1h`), function name, or exception type using SQL queries.
