# Breadcrumb Examples

This directory contains practical examples demonstrating how to use Breadcrumb AI Tracer for different scenarios.

## Quick Start

All examples follow the same pattern:

1. **Navigate to the example directory**
2. **Run the example**: `python main.py`
3. **Query the traces**: Use CLI or MCP tools
4. **Read the README**: Each example has detailed documentation

## Example Overview

### [Example 1: Simple Function Tracing](./01-simple-tracing/)

**What**: Basic "hello world" for Breadcrumb tracing
**Learn**: Zero-config initialization, function call capture, basic queries
**Time**: 5-10 minutes
**Best for**: First-time users, understanding trace structure

**Key Concepts**:
- `breadcrumb.init()` - Start tracing
- Automatic function capture
- Querying with SQL
- Understanding events and traces

**Run**:
```bash
cd 01-simple-tracing
python main.py
breadcrumb list
```

---

### [Example 2: Async/Await Tracing](./02-async-tracing/)

**What**: Tracing async functions and concurrent execution
**Learn**: Async context preservation, concurrency analysis, async timing
**Time**: 10-15 minutes
**Best for**: Async/await developers, API applications, concurrent systems

**Key Concepts**:
- Tracing async functions
- Context across await points
- Parallel vs sequential execution
- Async exception handling
- Performance of async operations

**Run**:
```bash
cd 02-async-tracing
python main.py
breadcrumb query "SELECT * FROM events WHERE function_name LIKE '%fetch%'"
```

---

### [Example 3: Exception Debugging](./03-exception-debugging/)

**What**: Using traces to debug exceptions and find root causes
**Learn**: Exception capture, stack analysis, root cause identification
**Time**: 15-20 minutes
**Best for**: Debugging production issues, understanding failure patterns

**Key Concepts**:
- Automatic exception capture
- Tracing back from error to cause
- Analyzing function arguments
- Comparing failed vs successful executions
- Common exception patterns (AttributeError, KeyError, ZeroDivisionError)

**Run**:
```bash
cd 03-exception-debugging
python main.py
breadcrumb exceptions --since 1h
breadcrumb get <trace-id>
```

---

### [Example 4: Performance Profiling](./04-performance-profiling/)

**What**: Identifying and fixing performance bottlenecks
**Learn**: Performance analysis, bottleneck identification, optimization strategies
**Time**: 20-25 minutes
**Best for**: Performance optimization, finding slow code, algorithm comparison

**Key Concepts**:
- Finding slowest functions
- Comparing algorithm performance (O(n²) vs O(n))
- Measuring optimization impact
- Redundant computation detection
- End-to-end pipeline profiling

**Run**:
```bash
cd 04-performance-profiling
python main.py
breadcrumb performance --sort duration
```

---

## Learning Path

### Path 1: Quick Start (30 minutes)
For developers who want to get started quickly:

1. **Example 1** (10 min) - Learn basic tracing
2. **Example 3** (20 min) - Learn debugging with traces

### Path 2: Complete Course (60 minutes)
For developers who want comprehensive understanding:

1. **Example 1** (10 min) - Basic tracing
2. **Example 2** (15 min) - Async tracing
3. **Example 3** (20 min) - Exception debugging
4. **Example 4** (25 min) - Performance profiling

### Path 3: Targeted Learning
Choose based on your needs:

- **Debugging Production Issues** → Example 3
- **Optimizing Performance** → Example 4
- **Building Async Applications** → Example 2
- **Just Getting Started** → Example 1

## Common Workflows

### Workflow 1: Debug a Crash

1. Run your application with `breadcrumb.init()`
2. When it crashes, run: `breadcrumb exceptions`
3. Get the trace: `breadcrumb get <trace-id>`
4. Examine arguments and return values
5. Trace backwards to find root cause

**See**: Example 3

### Workflow 2: Find Performance Bottleneck

1. Run your application with `breadcrumb.init()`
2. Run: `breadcrumb performance --sort duration`
3. Identify the slowest function
4. Optimize that function
5. Re-run and verify improvement

**See**: Example 4

### Workflow 3: Understand Async Flow

1. Run your async application with `breadcrumb.init()`
2. Query async functions: `breadcrumb query "SELECT * FROM events WHERE function_name LIKE '%async%'"`
3. Analyze timing to see which operations ran in parallel
4. Identify opportunities for concurrency

**See**: Example 2

### Workflow 4: Ask AI for Help

1. Run your application with `breadcrumb.init()`
2. Configure MCP in Claude Desktop
3. Ask Claude: "Use breadcrumb to find recent exceptions"
4. Ask Claude: "Analyze the performance of my code"
5. Claude uses MCP tools to query and analyze traces

**See**: All examples

## Using with MCP (Claude Desktop)

All examples work with the Breadcrumb MCP server. After running an example:

1. **Ask Claude to analyze traces**:
   - "Show me the last trace from Breadcrumb"
   - "Find exceptions in the last hour"
   - "Which function is slowest?"
   - "Analyze the execution flow"

2. **Claude will use these MCP tools**:
   - `breadcrumb__query_traces` - Execute SQL queries
   - `breadcrumb__get_trace` - Get trace details
   - `breadcrumb__find_exceptions` - Find exceptions
   - `breadcrumb__analyze_performance` - Analyze performance

3. **Claude provides insights**:
   - Root cause analysis for exceptions
   - Performance bottleneck identification
   - Optimization suggestions
   - Code improvement recommendations

## CLI Quick Reference

```bash
# List recent traces
breadcrumb list

# Get specific trace
breadcrumb get <trace-id>

# Find exceptions
breadcrumb exceptions --since 1h

# Analyze performance
breadcrumb performance --sort duration

# Custom SQL query
breadcrumb query "SELECT * FROM events WHERE function_name='my_func'"

# Start MCP server
breadcrumb serve-mcp
```

## Database Location

All examples store traces in:
```
.breadcrumb/traces.duckdb
```

You can query this database directly with DuckDB:
```bash
duckdb .breadcrumb/traces.duckdb
```

## Tips for Learning

1. **Run examples multiple times**: See how traces accumulate
2. **Modify the code**: Try breaking things and fixing them
3. **Experiment with queries**: Write your own SQL queries
4. **Use with your own code**: Add `breadcrumb.init()` to your projects
5. **Ask Claude**: Use the MCP integration for AI-assisted analysis

## Troubleshooting

**Problem**: No traces appear

**Solution**:
- Verify Breadcrumb is installed: `python -c "import breadcrumb"`
- Check database exists: `ls -la .breadcrumb/traces.duckdb`
- Check logs for errors

**Problem**: Examples fail to run

**Solution**:
- Ensure Python 3.12+ (or 3.10+ with sys.settrace)
- Install Breadcrumb: `uv pip install -e /path/to/breadcrumb`
- Check dependencies are installed

**Problem**: Queries return no results

**Solution**:
- Run an example first to generate traces
- Check database path is correct
- Verify trace_id exists: `breadcrumb list`

## Next Steps

After completing the examples:

1. **Add to your project**: `import breadcrumb; breadcrumb.init()`
2. **Configure for production**: Set sample_rate, filters, etc.
3. **Set up MCP**: Configure Claude Desktop for AI assistance
4. **Explore advanced queries**: Write custom SQL for your use cases
5. **Monitor performance**: Track trends over time

## Documentation

- **Main README**: `../README.md`
- **Contributing Guide**: `../CONTRIBUTING.md`
- **API Documentation**: `../docs/`

## Feedback

Found a bug or have a suggestion? Please open an issue on GitHub!

## License

MIT License - See LICENSE file in repository root
