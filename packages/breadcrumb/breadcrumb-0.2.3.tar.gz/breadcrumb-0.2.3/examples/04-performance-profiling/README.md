# Example 4: Performance Profiling

**Learning Objective**: Learn how to use Breadcrumb to identify performance bottlenecks, measure function execution times, and guide optimization efforts.

## What This Example Demonstrates

- Identifying slowest functions
- Comparing algorithm performance (O(n²) vs O(n))
- Measuring optimization impact
- Finding redundant computations
- Profiling end-to-end pipelines
- Trace-driven optimization workflow

## Prerequisites

1. Breadcrumb installed (see Example 1)
2. Python 3.12+ (or 3.10+ for sys.settrace fallback)
3. Basic understanding of algorithm complexity

## How to Run

```bash
# From this directory
python main.py
```

## Expected Output

```
============================================================
Breadcrumb Example 4: Performance Profiling
============================================================

============================================================
Example 1: Identify Performance Bottleneck
============================================================
Running multiple functions with different speeds...

Functions executed:
  - fast_function: 5 calls
  - slow_function: 3 calls
  - very_slow_function: 1 call

Expected result:
  very_slow_function should be slowest (~500ms)
  slow_function should be second (~100ms each)
  fast_function should be fastest (~0ms)

============================================================
Example 2: Algorithm Optimization
============================================================
Comparing O(n²) vs O(n) implementations...

Running inefficient_loop (O(n²))...
  Completed in 123.4ms
Running efficient_loop (O(n))...
  Completed in 1.2ms
  Improvement: 99.0% faster

[... more examples ...]
```

## Performance Optimization Workflow

### Step 1: Identify Bottlenecks

```bash
# Find slowest functions
breadcrumb performance --sort duration --limit 10
```

Output:
```
Top 10 Slowest Functions:

1. very_slow_function
   Calls: 1
   Total: 500.2ms
   Avg: 500.2ms
   Min: 500.2ms
   Max: 500.2ms

2. slow_function
   Calls: 13
   Total: 1300.5ms
   Avg: 100.0ms
   Min: 99.8ms
   Max: 100.2ms

3. inefficient_loop
   Calls: 1
   Total: 123.4ms
   Avg: 123.4ms
   Min: 123.4ms
   Max: 123.4ms

4. wasteful_string_concat
   Calls: 1
   Total: 45.6ms
   ...
```

**Insight**: `very_slow_function` is the biggest bottleneck, followed by `slow_function`.

### Step 2: Analyze Function Details

```bash
# Get detailed stats for a specific function
breadcrumb performance slow_function
```

Output:
```
Performance Analysis: slow_function

Total Calls: 13
Total Time: 1300.5ms
Average: 100.0ms
Median: 100.0ms
P95: 100.2ms
P99: 100.2ms
Min: 99.8ms
Max: 100.2ms

Call Timeline:
  10:30:45.123 - 100.0ms
  10:30:45.234 - 100.1ms
  10:30:45.345 - 99.9ms
  [... more calls ...]
```

**Insight**: Every call takes ~100ms consistently. This is a systemic bottleneck.

### Step 3: Find Callers

```bash
# Who's calling the slow function?
breadcrumb query "
  SELECT
    caller_function,
    COUNT(*) as call_count,
    SUM(duration_ms) as total_time
  FROM events
  WHERE function_name = 'slow_function'
    AND event_type = 'call'
  GROUP BY caller_function
  ORDER BY total_time DESC
"
```

Output:
```
caller_function         | call_count | total_time
----------------------- | ---------- | ----------
redundant_computation   | 10         | 1000.2ms
process_data            | 3          | 300.3ms
```

**Insight**: `redundant_computation` is responsible for 10 out of 13 calls!

### Step 4: Optimize

Look at `redundant_computation`:

```python
# BEFORE (slow)
def redundant_computation(n):
    total = 0
    for i in range(n):
        total += slow_function(10)  # Called n times!
    return total

# AFTER (fast)
def cached_computation(n):
    cached_value = slow_function(10)  # Called once!
    total = 0
    for i in range(n):
        total += cached_value
    return total
```

### Step 5: Verify Improvement

Re-run the code and compare:

```bash
# Compare before and after
breadcrumb query "
  SELECT
    function_name,
    AVG(duration_ms) as avg_time
  FROM events
  WHERE function_name IN ('redundant_computation', 'cached_computation')
  GROUP BY function_name
"
```

Output:
```
function_name          | avg_time
---------------------- | --------
redundant_computation  | 1000.2ms
cached_computation     | 100.1ms    <- 10x faster!
```

**Result**: 90% performance improvement!

## Performance Analysis Queries

### Find Slowest Functions

```bash
breadcrumb query "
  SELECT
    function_name,
    COUNT(*) as calls,
    AVG(duration_ms) as avg_ms,
    MAX(duration_ms) as max_ms
  FROM events
  WHERE event_type = 'call' AND duration_ms > 0
  GROUP BY function_name
  ORDER BY avg_ms DESC
  LIMIT 10
"
```

### Find Functions With High Variance

```bash
breadcrumb query "
  SELECT
    function_name,
    AVG(duration_ms) as avg_ms,
    STDDEV(duration_ms) as stddev_ms,
    MAX(duration_ms) - MIN(duration_ms) as range_ms
  FROM events
  WHERE event_type = 'call' AND duration_ms > 0
  GROUP BY function_name
  HAVING COUNT(*) > 5
  ORDER BY stddev_ms DESC
"
```

**Use case**: High variance indicates inconsistent performance (caching, I/O, etc.)

### Find Nested Call Overhead

```bash
breadcrumb query "
  WITH call_tree AS (
    SELECT
      function_name,
      duration_ms,
      (SELECT SUM(duration_ms)
       FROM events e2
       WHERE e2.parent_event_id = e1.event_id) as children_time
    FROM events e1
    WHERE event_type = 'call'
  )
  SELECT
    function_name,
    AVG(duration_ms - COALESCE(children_time, 0)) as self_time_ms
  FROM call_tree
  GROUP BY function_name
  ORDER BY self_time_ms DESC
"
```

**Use case**: Distinguish function's own time from time spent in called functions.

### Timeline Analysis

```bash
breadcrumb query "
  SELECT
    timestamp,
    function_name,
    duration_ms,
    SUM(duration_ms) OVER (ORDER BY timestamp) as cumulative_ms
  FROM events
  WHERE event_type = 'call'
  ORDER BY timestamp
"
```

**Use case**: See how execution time accumulates over the trace.

## Using MCP (Claude Desktop)

Ask Claude to help with performance:

**You**: "My code is slow. Can you help me find the bottleneck?"

**Claude**: *Uses `breadcrumb__analyze_performance`*

"I analyzed your recent traces and found that `very_slow_function` is the biggest bottleneck, taking 500ms per call. It was called once.

The second biggest bottleneck is `slow_function` with 13 calls totaling 1.3 seconds.

Looking deeper, I see that `redundant_computation` calls `slow_function` 10 times in a loop, which accounts for 1 second of the total time.

Here's my optimization recommendation:
1. Cache the result of `slow_function` outside the loop
2. This will reduce 10 calls to 1 call
3. Expected speedup: ~90%

Would you like me to help refactor this code?"

## Optimization Strategies

### Strategy 1: Algorithm Improvement

**Problem**: O(n²) nested loop

```python
# SLOW: O(n²)
for i in range(len(items)):
    for j in range(len(items)):
        if items[j]["id"] == i:
            result.append(items[j])
```

**Solution**: Use dictionary lookup O(n)

```python
# FAST: O(n)
lookup = {item["id"]: item for item in items}
result = [lookup[i] for i in range(len(items)) if i in lookup]
```

**Breadcrumb insight**: Compare execution times using `breadcrumb performance`.

### Strategy 2: Cache Expensive Operations

**Problem**: Recomputing same value

```python
# SLOW: Computes expensive_function() n times
for i in range(n):
    result += expensive_function(constant_input)
```

**Solution**: Compute once, reuse

```python
# FAST: Computes once
cached = expensive_function(constant_input)
for i in range(n):
    result += cached
```

**Breadcrumb insight**: Trace shows how many times `expensive_function` is called.

### Strategy 3: Batch Operations

**Problem**: Making many small I/O calls

```python
# SLOW: n separate I/O calls
for item in items:
    save_to_db(item)
```

**Solution**: Batch into fewer calls

```python
# FAST: 1 I/O call
save_to_db_batch(items)
```

**Breadcrumb insight**: Count function calls to identify batching opportunities.

### Strategy 4: Lazy Evaluation

**Problem**: Computing results never used

```python
# SLOW: Computes all results upfront
all_results = [expensive_function(x) for x in large_list]
first_result = all_results[0]  # Only need first one!
```

**Solution**: Compute on demand

```python
# FAST: Only computes what's needed
first_result = expensive_function(large_list[0])
```

**Breadcrumb insight**: See which computed values are actually used.

### Strategy 5: Use Better Data Structures

**Problem**: Linear search in list

```python
# SLOW: O(n) lookup
if value in my_list:  # Searches entire list
    ...
```

**Solution**: Use set or dict

```python
# FAST: O(1) lookup
if value in my_set:  # Instant lookup
    ...
```

**Breadcrumb insight**: Identify frequently-called functions doing list operations.

## What You Learned

1. **Bottleneck Identification**: Use `breadcrumb performance` to find slow functions
2. **Timing Analysis**: Measure average, min, max, and total execution times
3. **Caller Analysis**: Find which functions are calling expensive operations
4. **Optimization Verification**: Compare performance before and after changes
5. **Algorithm Complexity**: See real-world impact of O(n²) vs O(n)
6. **Trace-Driven Development**: Let execution data guide your optimizations

## Performance Tips

1. **Profile First, Optimize Later**: Don't guess where the bottleneck is - measure it!
2. **Focus on Impact**: Optimize the 20% that accounts for 80% of the time
3. **Measure Improvement**: Always verify that your optimization actually helps
4. **Watch for Regressions**: Track performance over time to catch slowdowns
5. **Consider Trade-offs**: Faster isn't always better if it uses much more memory

## Next Steps

1. **Review all examples**: `../01-simple-tracing/`, `../02-async-tracing/`, `../03-exception-debugging/`
2. **Profile your own code**: Add `breadcrumb.init()` to your project and find bottlenecks
3. **Combine techniques**: Use exception debugging + performance profiling together
4. **Advanced profiling**: Explore custom SQL queries for deeper insights

## Troubleshooting

**Problem**: All functions show 0ms duration

**Solution**: Functions are too fast to measure. Try running them in a loop or profiling larger operations.

**Problem**: Performance data seems inconsistent

**Solution**: System load, I/O, and caching can affect timing. Run multiple times and look at average/median values.

**Problem**: Can't find the bottleneck

**Solution**: Look at cumulative time, not just per-call time. A function called 1000 times at 1ms each is slower than one called once at 100ms.
