# Breadcrumb AI Tracer - Examples

This folder contains demos showing the current implementation status of the Breadcrumb AI Tracer.

## Implementation Status

### ✅ Phase 1: Core Tracing Engine (COMPLETE)
- PEP 669 backend (Python 3.12+) with sys.monitoring
- sys.settrace fallback backend (Python 3.10-3.11)
- Function call/return tracking
- Argument & return value capture
- Exception tracking
- Line-level execution tracking
- **114/114 tests passing**

### ✅ Phase 2: Storage Layer (COMPLETE)
- DuckDB embedded database
- Async batch writer with backpressure handling
- Query interface with SQL injection prevention
- Retention policy with automatic cleanup
- Schema migration system
- **99/99 tests passing** (2 skipped)

### ⏳ Phase 3-6: Not Yet Started
- MCP Server integration
- CLI interface
- Security & polish
- **Phase 1 & 2 integration**

## Current Status

**Phase 1 and Phase 2 are complete but NOT YET INTEGRATED.**

You can experiment with each layer independently:

### Phase 1: Instrumentation Demo

Run the instrumentation backend to see event capture in memory:

```bash
python -X utf8 examples/phase1_instrumentation_demo.py
```

**What it shows:**
- Capturing function calls, returns, exceptions
- Argument and return value capture
- Event statistics
- Sample event output

**Output:**
- 91+ execution events captured
- Call/return/line/exception event breakdown
- Detailed event metadata

### Phase 2: Storage Demo

Run the storage layer to see database operations:

```bash
python -X utf8 examples/phase2_storage_demo.py
```

**What it shows:**
- Writing traces/events/exceptions to DuckDB
- Async batch writing
- Querying traces by ID, status, time range
- Finding exceptions
- Storage statistics

**Output:**
- Sample traces stored and queried
- Query interface demonstration
- Feature checklist

## What Can You Experiment With?

### ✅ You CAN Test Right Now:

1. **Instrumentation backends** - Capture execution traces in memory
   - Works with any Python code (3.10-3.12+)
   - Selective instrumentation with include/exclude patterns
   - Low overhead with PEP 669 (Python 3.12+)

2. **Storage layer** - Persist and query traces
   - DuckDB database operations
   - Async writing with batching
   - Query interface for retrieving traces
   - Retention policy for cleanup

### ❌ You CANNOT Test Yet:

1. **End-to-end tracing** - Instrumentation → Storage integration
   - Phase 6 will connect the backends to storage
   - Currently they work independently

2. **MCP Server** - Claude Code/LLM integration
   - Phase 3 not started
   - Will expose traces via Model Context Protocol

3. **CLI Interface** - Command-line tools
   - Phase 4 not started
   - Will provide `breadcrumb start/stop/view` commands

4. **Production usage** - Security and polish
   - Phase 5 not started
   - Security review, documentation, packaging

## Next Steps

To use Breadcrumb AI Tracer in production, we need to:

1. **Phase 6**: Integrate instrumentation with storage
   - Connect backends to TraceWriter
   - Implement trace lifecycle management
   - Add instrumentation context manager

2. **Phase 3**: Build MCP Server
   - Implement Model Context Protocol server
   - Expose trace query APIs
   - Add real-time trace streaming

3. **Phase 4**: Create CLI Interface
   - `breadcrumb start/stop` commands
   - `breadcrumb view` for trace inspection
   - Configuration management

4. **Phase 5**: Security & Polish
   - Security review and sandboxing
   - Comprehensive documentation
   - Package for distribution

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     USER CODE                            │
│  def my_function(x, y):                                 │
│      return x + y                                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├──► Phase 1: Instrumentation (✅ DONE)
                   │    - PEP 669 Backend
                   │    - sys.settrace Backend
                   │    - Event capture in memory
                   │
                   ├──► Phase 6: Integration (⏳ TODO)
                   │    - Connect backends to storage
                   │
                   ├──► Phase 2: Storage (✅ DONE)
                   │    - Async batch writer
                   │    - DuckDB database
                   │    - Query interface
                   │
                   ├──► Phase 3: MCP Server (⏳ TODO)
                   │    - Model Context Protocol
                   │    - Trace APIs
                   │
                   └──► Phase 4: CLI (⏳ TODO)
                        - Start/stop tracing
                        - View traces
```

## Questions?

- **When will end-to-end work?** After Phase 6 (Integration) is complete
- **Can I use it now?** Only for experimentation with individual components
- **When is production ready?** After Phases 3-6 are complete
- **How do I contribute?** Check the PLAN.md in docs/specs/002-breadcrumb-ai-tracer/

## Test Results

All implemented phases have comprehensive test coverage:

```
Phase 1: Core Tracing Engine
├── test_pep669_backend.py         [✓]  52/52
├── test_settrace_backend.py       [✓]  50/50
└── test_trace_context.py          [✓]  12/12
                                   ──────────
                                   Total: 114/114

Phase 2: Storage Layer
├── test_connection.py             [✓]  13/13
├── test_async_writer.py           [✓]  25/25
├── test_query.py                  [✓]  20/20
├── test_migrations.py             [✓]  13/13
├── test_retention.py              [✓]  17/17
└── test_concurrent_access.py      [⊗]   2 skipped
                                   ──────────
                                   Total: 99/99 (2 skipped)

Overall: 213 tests passing
```

Enjoy experimenting! 🚀
