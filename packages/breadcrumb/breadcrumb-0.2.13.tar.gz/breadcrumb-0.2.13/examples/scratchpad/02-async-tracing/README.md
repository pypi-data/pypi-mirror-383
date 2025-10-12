# Example 2: Async/Await Tracing

**Learning Objective**: Understand how Breadcrumb traces async functions, maintains context across await points, and handles concurrent execution.

## What This Example Demonstrates

- Tracing async/await functions
- Context preservation across await points
- Concurrent execution tracking (asyncio.gather)
- Async exception handling
- Timing analysis for async operations
- Understanding async execution flow

## Prerequisites

1. Breadcrumb installed (see Example 1)
2. Python 3.12+ (or 3.10+ for sys.settrace fallback)
3. Basic understanding of asyncio

## How to Run

```bash
# From this directory
python main.py
```

## Expected Output

```
============================================================
Breadcrumb Example 2: Async/Await Tracing
============================================================

1. Parallel User Fetching:
------------------------------------------------------------
  Fetching user 1...
  Fetching user 2...
  Fetching user 3...
  Fetched 3 users in parallel
    - User_1: user1@example.com
    - User_2: user2@example.com
    - User_3: user3@example.com

2. Sequential Profile Building:
------------------------------------------------------------
  Fetching user 10...
  Fetching posts for user 10...
    Fetching comments for post 0...
    Fetching comments for post 1...
  Profile for User_10:
    Email: user10@example.com
    Posts: 2
      - Post 0 by user 10 (1 comments)
      - Post 1 by user 10 (2 comments)

3. Async Error Handling:
------------------------------------------------------------
  Task results:
    Task 0: SUCCESS - 10
    Task 1: ERROR - Simulated async error!
    Task 2: SUCCESS - 20

============================================================
Async execution complete! Traces captured.
============================================================
```

## Why Async Tracing is Important

Async code is harder to debug because:
1. **Non-linear execution**: Functions don't execute in call order
2. **Context switching**: Multiple tasks interleave execution
3. **Hidden delays**: `await` points create gaps in execution
4. **Concurrent failures**: Errors in one task may affect others

Breadcrumb solves this by:
- Tracking each async function call with timing
- Maintaining trace context across await points
- Showing which tasks ran in parallel
- Capturing async exceptions with full context

## Trace Queries for Async Code

### Using CLI

```bash
# Find all async function calls
breadcrumb query "SELECT * FROM events WHERE function_name LIKE '%fetch%'"

# Analyze await timing (time between call and return)
breadcrumb query "
  SELECT
    function_name,
    EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (ORDER BY timestamp))) * 1000 as wait_ms
  FROM events
  WHERE function_name LIKE '%fetch%'
  ORDER BY timestamp
"

# Find which functions ran concurrently
breadcrumb query "
  SELECT
    e1.function_name as func1,
    e2.function_name as func2,
    e1.timestamp as start1,
    e2.timestamp as start2
  FROM events e1, events e2
  WHERE e1.event_type = 'call'
    AND e2.event_type = 'call'
    AND e1.timestamp < e2.timestamp
    AND e1.function_name != e2.function_name
  LIMIT 10
"

# Show async execution timeline
breadcrumb query "
  SELECT
    timestamp,
    event_type,
    function_name,
    CASE WHEN event_type = 'call' THEN 'START' ELSE 'END' END as status
  FROM events
  WHERE function_name IN ('fetch_user', 'fetch_posts', 'fetch_comments')
  ORDER BY timestamp
"

# Find async exceptions
breadcrumb exceptions --since 1h
```

### Using MCP (Claude Desktop)

Ask Claude:

- "Show me all async function calls from the last trace"
- "Which async functions ran in parallel?"
- "What was the slowest async operation?"
- "Show me the execution timeline for fetch_user calls"
- "Find any async exceptions that occurred"

Example MCP query Claude might use:

```python
# Claude uses: breadcrumb__query_traces
{
  "query": "SELECT function_name, timestamp FROM events WHERE function_name LIKE '%fetch%' ORDER BY timestamp",
  "limit": 50
}
```

## Understanding Async Trace Structure

### Parallel Execution Example

When you run `await asyncio.gather(fetch_user(1), fetch_user(2))`, the trace shows:

```
Timestamp    Event    Function         User ID
---------    -----    --------         -------
10:00:00.0   call     fetch_user       1
10:00:00.0   call     fetch_user       2       <- Started immediately!
10:00:00.2   return   fetch_user       1       <- First one completes
10:00:00.3   return   fetch_user       2       <- Second completes
```

Key insight: Both `call` events happen at nearly the same time (concurrent execution).

### Sequential Execution Example

When you run:
```python
user = await fetch_user(1)
posts = await fetch_posts(1)
```

The trace shows:

```
Timestamp    Event    Function
---------    -----    --------
10:00:00.0   call     fetch_user
10:00:00.2   return   fetch_user       <- Must complete first
10:00:00.2   call     fetch_posts      <- Then this starts
10:00:00.5   return   fetch_posts
```

Key insight: The second `call` happens after the first `return` (sequential execution).

## Code Explanation

```python
import breadcrumb
breadcrumb.init()

async def fetch_user(user_id):
    await asyncio.sleep(0.1)  # Breadcrumb tracks the wait time!
    return {"id": user_id}

# Parallel execution
users = await asyncio.gather(
    fetch_user(1),  # Trace shows concurrent execution
    fetch_user(2),
    fetch_user(3),
)

# Sequential execution
user = await fetch_user(1)   # Trace shows sequential execution
posts = await fetch_posts(1) # This starts after user completes
```

Breadcrumb captures:
- Each async function call with arguments
- Timing for each await point
- Which tasks ran in parallel
- Context is maintained even when tasks interleave

## Performance Analysis

Use Breadcrumb to identify async performance issues:

```bash
# Find slowest async operations
breadcrumb performance --sort duration --limit 10

# Compare parallel vs sequential timing
breadcrumb query "
  SELECT
    function_name,
    AVG(duration_ms) as avg_duration,
    COUNT(*) as call_count
  FROM events
  WHERE event_type = 'call' AND function_name LIKE '%fetch%'
  GROUP BY function_name
"
```

## What You Learned

1. **Async Tracing**: Breadcrumb automatically traces async functions
2. **Context Preservation**: Trace context maintained across await points
3. **Concurrency Visibility**: See which tasks ran in parallel
4. **Timing Analysis**: Measure async operation durations
5. **Exception Tracking**: Async errors are captured with full context

## Common Patterns

### Pattern 1: Parallel API Calls

```python
# Fetch multiple resources concurrently
results = await asyncio.gather(
    fetch_user(1),
    fetch_posts(1),
    fetch_comments(1)
)
# Trace shows all three start at once
```

### Pattern 2: Sequential Data Dependencies

```python
# Fetch data that depends on previous results
user = await fetch_user(1)
posts = await fetch_posts(user["id"])  # Depends on user
# Trace shows sequential execution
```

### Pattern 3: Map-Reduce Pattern

```python
# Fetch many items in parallel, then aggregate
tasks = [fetch_user(i) for i in range(10)]
users = await asyncio.gather(*tasks)
# Trace shows all fetches start together, then complete
```

## Next Steps

1. **Example 3**: Debug exceptions with traces → `../03-exception-debugging/`
2. **Example 4**: Profile performance bottlenecks → `../04-performance-profiling/`
3. **Advanced**: Combine async tracing with performance analysis

## Troubleshooting

**Problem**: Async traces look sequential even with gather()

**Solution**: Check that you're using `await asyncio.gather()` not sequential awaits. Compare trace timestamps to verify concurrency.

**Problem**: Missing async function calls in trace

**Solution**: Ensure all async functions are actually being called with `await`. Unawaited coroutines won't execute.

**Problem**: Trace context lost across awaits

**Solution**: This is expected behavior - Breadcrumb maintains trace_id but tasks may interleave. Use trace_id and timestamps to reconstruct execution flow.
