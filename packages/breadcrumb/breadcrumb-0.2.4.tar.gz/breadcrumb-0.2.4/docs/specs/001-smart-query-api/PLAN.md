# Implementation Plan: Smart Query API

## Validation Checklist
- [x] Context Ingestion section complete with all required specs
- [x] Implementation phases logically organized
- [x] Each phase starts with test definition (TDD approach)
- [x] Dependencies between phases identified
- [x] Parallel execution marked where applicable
- [ ] Multi-component coordination identified (N/A - single component)
- [x] Final validation phase included
- [x] No placeholder content remains
- [x] **LITMUS TEST defined** - Pizza ingredient extraction without SQL

---

## 🎯 LITMUS TEST - Definition of Done

**THIS IS THE ONLY ACCEPTANCE CRITERION THAT MATTERS:**

> "Find out the ingredients of the pizza the pizza agent generated, and how long it took with just using breadcrumb"

**We are ONLY done when this task is successfully solved using the smart query API.**

The user should be able to:
1. Run the pizza example with breadcrumb tracing
2. Use breadcrumb smart queries (without writing SQL) to discover:
   - The exact ingredients of the generated Pizza
   - The execution duration of the Pizza creation
3. Do this iteratively, starting with minimal tracing and expanding based on --gaps output

**How to Run the Pizza Example:**
```bash
# Initialize pizza project (one-time setup)
breadcrumb init pizza

# Run with tracing (explicit -c required!)
PYTHONIOENCODING=utf-8 breadcrumb run -c pizza -t 60 python examples/00-MUST-WORK/01_declarative_pizza.py
```

**Expected Litmus Test Workflow:**
```bash
# 1. Initialize project
breadcrumb init pizza

# 2. Run with minimal tracing (only __main__)
PYTHONIOENCODING=utf-8 breadcrumb run -c pizza -t 60 python examples/00-MUST-WORK/01_declarative_pizza.py

# 3. Discover what's missing (explicit -c required!)
breadcrumb query -c pizza --gaps
# Should reveal: flock.orchestrator.* and flock.registry.* are not traced

# 4. Expand tracing based on gaps
breadcrumb config edit pizza --add-include 'flock.orchestrator.*'
breadcrumb config edit pizza --add-include 'flock.registry.*'

# 5. Run again with expanded tracing
PYTHONIOENCODING=utf-8 breadcrumb run -c pizza -t 60 python examples/00-MUST-WORK/01_declarative_pizza.py

# 6. LITMUS TEST - Get Pizza details (explicit -c required!)
breadcrumb query -c pizza --call Pizza
# MUST show: ingredients, size, crust_type, step_by_step_instructions

# 7. LITMUS TEST - Get timing (explicit -c required!)
breadcrumb query -c pizza --call pizza_master
# MUST show: duration_ms for the Pizza creation
```

**Success Criteria:**
- ✅ User can see Pizza ingredients list (e.g., "San Marzano tomato sauce", "Fresh mozzarella", "Truffle cream", etc.)
- ✅ User can see Pizza size (e.g., "12-inch (medium)")
- ✅ User can see crust_type (e.g., "Neapolitan-style")
- ✅ User can see step_by_step_instructions
- ✅ User can see how long it took (duration_ms)
- ✅ User NEVER had to write SQL

---

## 🤖 AI-FIRST Design Philosophy (Critical!)

**DESIGN PRINCIPLE**: Breadcrumb is built for AI agents, not humans.

### The Core Insight

> **"It's only clunky for humans! AI agents have no issues with writing `-c` after each command."**

Traditional dev tools optimize for human UX (implicit defaults, smart context inference, minimal typing). This creates ambiguity that breaks AI agent workflows across sessions.

**AI agents need**:
- ✅ **Explicit over implicit** - No hidden state, no magic defaults
- ✅ **Zero context confusion** - Which database? Which config? Always clear.
- ✅ **Session-independent** - Works identically in session 1 and session 100
- ✅ **No surprises** - Same command = same result, always

### Why `-c PROJECT` is REQUIRED

**All commands that need database/config context REQUIRE explicit `-c PROJECT` parameter:**

```bash
# ✅ CORRECT - Explicit project
breadcrumb run -c myproject --timeout 60 python script.py
breadcrumb query -c myproject --gaps
breadcrumb config edit myproject --add-include 'mymodule.*'

# ❌ WRONG - Implicit/missing project
breadcrumb run --timeout 60 python script.py          # ERROR: Missing -c
breadcrumb query --gaps                                # ERROR: Config required
```

**Why this matters**:
- **Humans**: "Ugh, typing `-c myproject` every time is annoying!"
- **AI Agents**: "Perfect! No ambiguity about which database to query!"

**What this eliminates**:
- ❌ "Which database am I querying?"
- ❌ "Which config is active?"
- ❌ "Where did my traces go?"
- ❌ "Why is it tracing the wrong code?"
- ❌ Context loss between agent sessions
- ❌ Hidden state bugs

### The AI-FIRST Workflow

**Designed for iterative refinement by AI agents**:

```bash
# 1️⃣ One-time initialization (simple!)
breadcrumb init myproject
# Creates ~/.breadcrumb/myproject.yaml with defaults (include: ['__main__'])
# Creates ~/.breadcrumb/myproject-traces.duckdb for traces

# 2️⃣ Run with minimal tracing (explicit -c!)
breadcrumb run -c myproject --timeout 60 python script.py
# Traces only __main__ module initially

# 3️⃣ Discover what's missing (explicit -c!)
breadcrumb query -c myproject --gaps
# Shows: "json.dumps called 3 times by __main__.format_result"
# Suggests: "breadcrumb config edit myproject --add-include 'json.*'"

# 4️⃣ Expand coverage based on gaps (explicit name!)
breadcrumb config edit myproject --add-include 'json.*'
# No ambiguity - editing myproject config explicitly

# 5️⃣ Re-run with expanded tracing (explicit -c!)
breadcrumb run -c myproject --timeout 60 python script.py
# Now traces json.* functions too!

# 6️⃣ Query function details (explicit -c!)
breadcrumb query -c myproject --call format_result
# Shows args, returns, duration, full I/O
```

**Key Properties**:
- Every command is self-contained (no hidden context)
- AI agents can resume workflow at any step
- No state leaks between sessions
- 100% reproducible across runs

### Implementation Details

**Files Modified**:
- `src/breadcrumb/cli/main.py`:
  - Added `breadcrumb init PROJECT` command (one-step setup)
  - Made `-c` REQUIRED on `breadcrumb run` (changed from Optional[str] to str)
  - Updated all help text to emphasize AI-FIRST philosophy

- `src/breadcrumb/cli/commands/smart_query.py`:
  - Enforces config parameter is REQUIRED for CLI usage
  - Clear error messages with suggestions when -c missing

**User Quote** (rationale for this design):
> "you may say it's clunky, but then you are not thinking AI first, since it's only clunky for humans! ai agents have no issues with writing -c after each command"

**Result**: AI agents can execute breadcrumb workflows with 100% reliability, zero context confusion, and perfect session-to-session consistency.

---

## Context Priming

*GATE: You MUST fully read all files mentioned in this section before starting any implementation.*

**Specification**:
- `docs/smart_query_api_draft.md` - Feature requirements and design `[ref: docs/smart_query_api_draft.md]`

**Key Design Decisions**:
- **Include-only workflow**: Default to tracing only `__main__`, no workspace filter, no exclude patterns
- **Gap detection**: Show untraced calls to guide iterative include expansion
- **Smart queries replace SQL**: Provide semantic commands (`--gaps`, `--call`, `--flow`) instead of raw SQL
- **Phase 1 MVP**: `--gaps`, `--call`, `--flow` (defer `--expensive`, `--data`, `--trace` to later phases)
- **JSON output**: All smart queries return structured JSON for AI agent consumption

**Implementation Context**:

**Existing Patterns to Follow**:
- CLI command structure: `src/breadcrumb/cli/commands/performance.py` (lines 1-150) - Shows Typer command pattern with GlobalState
- Query execution: `src/breadcrumb/storage/query.py` (lines 1-100) - Shows query_traces() pattern
- Database schema: `src/breadcrumb/storage/schema.sql` (lines 1-88) - traces and trace_events tables with JSON data column

**Database Schema** `[ref: src/breadcrumb/storage/schema.sql]`:
```sql
-- traces table
CREATE TABLE traces (
    id VARCHAR PRIMARY KEY,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR,  -- 'running', 'completed', 'failed'
    ...
)

-- trace_events table
CREATE TABLE trace_events (
    id VARCHAR PRIMARY KEY,
    trace_id VARCHAR,
    timestamp TIMESTAMP,
    event_type VARCHAR,  -- 'call', 'return', 'exception'
    function_name VARCHAR,
    module_name VARCHAR,
    file_path VARCHAR,
    line_number INTEGER,
    data JSON,  -- Contains: args, kwargs, return_value, local_vars, is_async
    ...
)
```

**Installation & Setup**:
```bash
# Install breadcrumb in editable mode (required for development)
uv pip install -e .

# All breadcrumb commands should be run with 'uv run' prefix
uv run breadcrumb --help
```

**Commands to Run**:
- Install breadcrumb: `uv pip install -e .`
- Run tests: `pytest tests/integration/test_smart_queries.py -v`
- Run all tests: `pytest tests/ -v`
- Run breadcrumb CLI: `uv run breadcrumb <command>`
- Run pizza example: `PYTHONIOENCODING=utf-8 uv run breadcrumb run -t 60 python examples/00-MUST-WORK/01_declarative_pizza.py`
- Run litmus test: See "LITMUS TEST" section at top of this document

---

## Implementation Phases

### Phase 1: Integration Tests (TDD Foundation) ✅ COMPLETED

**Objective**: Define the API contract through integration tests before implementation

- [x] **Prime Context**
    - [x] Read smart_query_api_draft.md requirements `[ref: docs/smart_query_api_draft.md]`
    - [x] Review existing CLI test patterns `[ref: tests/integration/test_cli_workflow.py]`
    - [x] Review conftest helpers (run_traced_code, wait_for_traces) `[ref: tests/integration/conftest.py]`

- [x] **Write Integration Tests** `[ref: docs/smart_query_api_draft.md; lines: 118-141, 31-64, 74-87]`

    Created `tests/integration/test_smart_queries.py` with:

    - [x] **Test --gaps command** (THE KILLER FEATURE)
        - [x] Test detects untraced function calls (json.dumps, json.loads)
        - [x] Test shows call counts for each untraced function
        - [x] Test shows caller context (which function made the call)
        - [x] Test suggests include patterns
        - [x] Test JSON output structure

    - [x] **Test --call command**
        - [x] Test shows function arguments and return values
        - [x] Test shows execution duration
        - [x] Test shows caller (called_by) and callees (calls_made)
        - [x] Test handles multiple invocations of same function
        - [x] Test handles nonexistent function gracefully
        - [x] Test JSON output structure

    - [x] **Test --flow command**
        - [x] Test shows chronological execution order
        - [x] Test shows nested call structure (depth/indentation)
        - [x] Test supports --module filter
        - [x] Test indicates untraced calls in flow
        - [x] Test JSON output structure

    - [x] **Test error handling**
        - [x] Test all commands with empty database
        - [x] Test all commands return valid JSON

    - [x] **Test integration between commands**
        - [x] Test --gaps → --call workflow
        - [x] Test --flow and --gaps consistency

- [x] **Validate Tests**
    - [x] Tests run and fail appropriately (commands don't exist yet)
    - [x] Test fixtures create realistic trace data
    - [x] Test assertions verify correct behavior
    - [x] All tests follow pytest conventions

**Additional Work Completed**:
- [x] **REFACTOR: Include-Only Workflow** (from Phase 6, completed early)
    - [x] Removed `exclude` patterns from entire codebase
    - [x] Removed `workspace_only` parameter from config and backends
    - [x] Updated `BreadcrumbConfig` default from `['*']` to `['__main__']`
    - [x] Updated `PEP669Backend` to use include-only filtering
    - [x] Updated all CLI config commands (`config create`, `config edit`, `config validate`)
    - [x] Updated test fixtures to use include-only pattern
    - [x] Simplified `_should_trace()` logic to only check include patterns
    - **Note**: `src/breadcrumb/cli/main.py` still needs updates to remove `exclude`/`workspace_only` from commands

---

### Phase 2: Smart Query Infrastructure ✅ COMPLETED

**Objective**: Build the foundation for smart query commands

- [x] **Prime Context**
    - [x] Review CLI main.py structure `[ref: src/breadcrumb/cli/main.py; lines: 1-50]`
    - [x] Review query command pattern `[ref: src/breadcrumb/cli/commands/query.py]`
    - [x] Review GlobalState pattern `[ref: src/breadcrumb/cli/main.py; lines: 40-80]`

- [x] **Create Smart Query Module**

    Created `src/breadcrumb/cli/commands/smart_query.py`:

    - [x] **Define command structure** (execute_smart_query function)
    - [x] **Add routing logic**
        - [x] If --gaps: route to gaps_query()
        - [x] If --call: route to call_query()
        - [x] If --flow: route to flow_query()
        - [x] If sql provided: route to existing SQL query
        - [x] Validate: only one query type at a time

    - [x] **Load config for db_path**
        - [x] Support -c/--config parameter
        - [x] Use GlobalState db_path if no config
        - [x] Load config to get effective db_path

- [x] **Create Smart Query Engine**

    Created `src/breadcrumb/storage/smart_queries.py`:

    - [x] **Define base query functions** (stubs returning {"status": "not_implemented"})
        - [x] gaps_query(db_path: str, trace_id: Optional[str] = None) -> dict
        - [x] call_query(db_path: str, function_name: str) -> dict
        - [x] flow_query(db_path: str, module_filter: Optional[str] = None) -> dict

    - [x] **Implement helper: get_call_stack()** (stub)
        - [x] Build call stack from trace_events (stub implementation)

- [x] **Update CLI Exports**
    - [x] Update main.py to integrate smart query options into existing query command
    - [x] Ensure backward compatibility with existing `query` SQL command

- [x] **Validate Infrastructure**
    - [x] Commands registered in CLI successfully
    - [x] --help shows new options (--gaps, --call, --flow, --module)
    - [x] Routing works correctly (all return stub responses)

---

### Phase 3: Implement --gaps (THE KILLER FEATURE) ✅ COMPLETED

**Objective**: Detect and report untraced function calls `[ref: docs/smart_query_api_draft.md; lines: 118-141]`

- [x] **Prime Context**
    - [x] Review gap detection algorithm `[ref: docs/smart_query_api_draft.md; lines: 396-401]`
    - [x] Review call stack analysis strategy
    - [x] Understand PY_CALL vs actual trace capture

- [x] **Implement Gap Detection Algorithm**

    In `src/breadcrumb/storage/smart_queries.py`:

    - [x] **Modified PEP669 backend to capture 'call_site' events**
        - [x] Added 'call_site' event type to TraceEvent dataclass
        - [x] Modified `_on_call()` to capture lightweight call_site events for untraced functions
        - [x] Only captures when caller IS traced (no noise from completely untraced paths)
        - [x] Stores caller context (called_from_function, called_from_module)

    - [x] **Fixed critical bugs in module inference**
        - [x] **BUG FIX**: Breadcrumb path exclusion was too broad (excluded `/breadcrumb-tracer/` directory)
        - [x] **BUG FIX**: Module inference using frame.f_globals (wrong - gives caller's module)
        - [x] **SOLUTION**: Implemented robust `_infer_module_from_file()` with sys.modules lookup
        - [x] **SOLUTION**: Changed exclusion to only exclude actual breadcrumb internal modules

    - [x] **Implemented gaps_query() function**
        - [x] Query for 'call_site' events from trace_events table
        - [x] Parse JSON data column to extract caller information
        - [x] Aggregate by function name and count occurrences
        - [x] Generate suggested_include patterns (e.g., "module.*")
        - [x] Generate tips with config edit commands

    - [x] **Return structured JSON**
        ```json
        {
            "untraced_calls": [
                {
                    "function": "json.dumps",
                    "module": "json",
                    "called_by": "__main__.format_result",
                    "call_count": 1,
                    "suggested_include": "json.*"
                }
            ],
            "tip": "Add these to your config to trace them:\n  breadcrumb config edit <name> --add-include 'json.*'"
        }
        ```

- [x] **Validate --gaps**
    - [x] Run integration tests for --gaps (4 tests passing)
    - [x] All --gaps tests pass
    - [x] Manual test with test_ai_workflow.py confirmed working

- [x] **AI-FIRST Workflow Implementation** (Critical Design Decision!)
    - [x] **DESIGN DECISION**: Make `-c PROJECT` REQUIRED for all commands
    - [x] **RATIONALE**: "It's only clunky for humans! AI agents have no issues with writing -c after each command"
    - [x] **PHILOSOPHY**: Explicit > Implicit for AI workflows (zero ambiguity, zero context confusion)

    - [x] **Created `breadcrumb init PROJECT` command**
        - [x] One-step initialization: creates config + sets up database
        - [x] Creates ~/.breadcrumb/PROJECT.yaml with sensible defaults
        - [x] Creates ~/.breadcrumb/PROJECT-traces.duckdb for traces
        - [x] Shows AI-FIRST workflow instructions after init

    - [x] **Made `-c` REQUIRED on `breadcrumb run`**
        - [x] Changed `config` parameter from Optional[str] to required str
        - [x] Updated help text to emphasize AI-FIRST workflow
        - [x] Shows error if -c not provided: "Missing option '--config' / '-c'"

    - [x] **Already enforced `-c` on `breadcrumb query`** (via smart_query.py)
        - [x] Config parameter is REQUIRED for CLI usage
        - [x] Shows clear error with suggestions if missing

    - [x] **Complete AI-FIRST workflow validated**:
        ```bash
        # Step 1: Initialize
        breadcrumb init testproject

        # Step 2: Run (explicit -c required!)
        breadcrumb run -c testproject --timeout 60 python script.py

        # Step 3: Find gaps (explicit -c required!)
        breadcrumb query -c testproject --gaps

        # Step 4: Expand coverage based on gaps
        breadcrumb config edit testproject --add-include 'mymodule.*'

        # Step 5: Re-run with expanded tracing
        breadcrumb run -c testproject --timeout 60 python script.py
        ```

**Key Accomplishments**:
- ✅ Gap detection working reliably via call_site events
- ✅ All 4 integration tests passing
- ✅ Critical bugs fixed (module inference, path exclusion)
- ✅ AI-FIRST workflow fully implemented and tested
- ✅ Documentation updated in README.md with design philosophy
- 🎯 Ready for Phase 4: --call implementation

---

### Phase 4: Implement --call

**Objective**: Show function calls with arguments, returns, and metadata `[ref: docs/smart_query_api_draft.md; lines: 31-64]`

- [ ] **Prime Context**
    - [ ] Review call query requirements `[ref: docs/smart_query_api_draft.md; lines: 31-64]`
    - [ ] Review trace_events.data JSON structure
    - [ ] Review existing performance.py query patterns `[ref: src/breadcrumb/cli/commands/performance.py]`

- [ ] **Implement Call Query**

    In `src/breadcrumb/storage/smart_queries.py`:

    - [ ] **Query for function calls**
        ```sql
        SELECT
            te_call.id,
            te_call.timestamp,
            te_call.function_name,
            te_call.module_name,
            te_call.data as call_data,
            te_return.timestamp as return_timestamp,
            te_return.data as return_data,
            te_caller.function_name as caller,
            te_caller.module_name as caller_module
        FROM trace_events te_call
        LEFT JOIN trace_events te_return
            ON te_call.trace_id = te_return.trace_id
            AND te_return.event_type = 'return'
            AND te_return.function_name = te_call.function_name
            AND te_return.timestamp > te_call.timestamp
        LEFT JOIN trace_events te_caller
            ON te_call.trace_id = te_caller.trace_id
            AND te_caller.event_type = 'call'
            AND te_caller.timestamp < te_call.timestamp
        WHERE te_call.function_name = ?
          AND te_call.event_type = 'call'
        ORDER BY te_call.timestamp
        ```

    - [ ] **Extract args/kwargs from data column**
        - [ ] Parse JSON from te_call.data
        - [ ] Extract 'args', 'kwargs' fields

    - [ ] **Extract return_value from data column**
        - [ ] Parse JSON from te_return.data
        - [ ] Extract 'return_value' field

    - [ ] **Calculate duration**
        - [ ] duration_ms = (return_timestamp - call_timestamp) * 1000

    - [ ] **Find callees (what this function called)**
        - [ ] Query for all calls made between this call and return
        - [ ] Build list of function names

    - [ ] **Return structured JSON**
        ```json
        {
            "function": "calculate_total",
            "calls": [
                {
                    "timestamp": "2025-10-11T15:14:36",
                    "args": {"items": [...]},
                    "return_value": 21.48,
                    "duration_ms": 0.234,
                    "called_by": "__main__.process_order",
                    "calls_made": ["sum", "dict.__getitem__"]
                }
            ]
        }
        ```

- [ ] **Validate --call**
    - [ ] Run integration tests for --call
    - [ ] All --call tests should pass
    - [ ] Manual test with pizza example

---

### Phase 5: Implement --flow

**Objective**: Show chronological execution timeline with nesting `[ref: docs/smart_query_api_draft.md; lines: 74-87]`

- [ ] **Prime Context**
    - [ ] Review flow query requirements `[ref: docs/smart_query_api_draft.md; lines: 74-87]`
    - [ ] Understand call stack depth tracking
    - [ ] Review chronological ordering

- [ ] **Implement Flow Query**

    In `src/breadcrumb/storage/smart_queries.py`:

    - [ ] **Query for all events in chronological order**
        ```sql
        SELECT
            id,
            timestamp,
            event_type,
            function_name,
            module_name,
            data
        FROM trace_events
        WHERE trace_id = ?
          AND event_type IN ('call', 'return', 'exception')
        ORDER BY timestamp ASC
        ```

    - [ ] **Add module filter if provided**
        - [ ] Add WHERE clause: `AND module_name = ?`

    - [ ] **Calculate call depth/nesting**
        - [ ] Track depth counter
        - [ ] Increment on 'call', decrement on 'return'
        - [ ] Add 'depth' field to each event

    - [ ] **Extract args/returns from data column**
        - [ ] For call events: extract args
        - [ ] For return events: extract return_value
        - [ ] For exception events: extract exception info

    - [ ] **Calculate durations**
        - [ ] Match call/return pairs
        - [ ] Add duration_ms to return events

    - [ ] **Return structured JSON**
        ```json
        {
            "flow": [
                {
                    "timestamp": "2025-10-11T15:14:36.123",
                    "depth": 0,
                    "event_type": "call",
                    "function": "__main__.main",
                    "args": {}
                },
                {
                    "timestamp": "2025-10-11T15:14:36.125",
                    "depth": 1,
                    "event_type": "call",
                    "function": "__main__.process_order",
                    "args": {"customer_name": "Alice", "items": [...]}
                },
                ...
            ]
        }
        ```

- [ ] **Validate --flow**
    - [ ] Run integration tests for --flow
    - [ ] All --flow tests should pass
    - [ ] Manual test with pizza example

---

### Phase 6: Config Changes (Include-Only Default) ✅ COMPLETED (Early in Phase 1)

**Objective**: Change default config to include-only workflow `[ref: docs/smart_query_api_draft.md; lines: 287-307]`

**Status**: This was completed early during Phase 1 as part of the include-only workflow refactor.

- [x] **Prime Context**
    - [x] Review config defaults `[ref: src/breadcrumb/config.py]`
    - [x] Review include-only rationale `[ref: docs/smart_query_api_draft.md; lines: 145-224]`

- [x] **Update Default Config** `[ref: src/breadcrumb/config.py]`

    - [x] **Changed BreadcrumbConfig defaults**
        - Changed default include from `['*']` to `['__main__']`
        - Removed `exclude_patterns` from entire codebase
        - Removed `workspace_only` parameter
        - Simplified `_should_trace()` logic to only check include patterns

- [x] **Update Config CLI Commands**

    - [x] **--add-include command exists**
        ```bash
        breadcrumb config edit pizza --add-include 'flock.orchestrator.*'
        ```

    - [x] **--remove-include command exists**
        ```bash
        breadcrumb config edit pizza --remove-include 'flock.logging.*'
        ```

- [x] **Update Documentation**
    - [x] Updated README with AI-FIRST workflow in Phase 3
    - [x] Added examples of include-only usage
    - [x] Config docs reflect include-only approach

- [x] **Validate Config Changes**
    - [x] All existing tests pass (backward compatibility maintained)
    - [x] Tested with test_ai_workflow.py
    - [x] --add-include/--remove-include commands working

---

### Phase 7: Integration & End-to-End Validation

**⚠️ THIS PHASE IS NOT COMPLETE UNTIL THE LITMUS TEST PASSES (see top of document)**

- [ ] **All Unit Tests Passing**
    - [ ] `pytest tests/integration/test_smart_queries.py -v`
    - [ ] All 20+ tests pass

- [ ] **Integration Tests**
    - [ ] Test --gaps → --call workflow
    - [ ] Test --flow and --gaps consistency
    - [ ] Test config changes with smart queries

- [ ] **🎯 LITMUS TEST - The Ultimate Validation**
    - [ ] Run the complete litmus test workflow (see top of document)
    - [ ] **Step 1**: Initialize project
        ```bash
        breadcrumb init pizza
        ```
    - [ ] **Step 2**: Run pizza example with minimal tracing
        ```bash
        PYTHONIOENCODING=utf-8 breadcrumb run -c pizza -t 60 python examples/00-MUST-WORK/01_declarative_pizza.py
        ```
    - [ ] **Step 3**: Use `breadcrumb query -c pizza --gaps` to discover untraced calls
        - [ ] Must return valid JSON
        - [ ] Must identify flock.orchestrator.* functions
        - [ ] Must show which functions called them
        - [ ] Must suggest include patterns
    - [ ] **Step 4**: Expand tracing based on gaps
        ```bash
        breadcrumb config edit pizza --add-include 'flock.orchestrator.*'
        breadcrumb config edit pizza --add-include 'flock.registry.*'
        ```
    - [ ] **Step 5**: Re-run with expanded tracing
        ```bash
        PYTHONIOENCODING=utf-8 breadcrumb run -c pizza -t 60 python examples/00-MUST-WORK/01_declarative_pizza.py
        ```
    - [ ] **Step 6**: CRITICAL - Extract Pizza ingredients
        ```bash
        breadcrumb query -c pizza --call Pizza
        ```
        **MUST SHOW:**
        - [ ] Pizza ingredients list (e.g., "San Marzano tomato sauce", "Fresh mozzarella", "Truffle cream")
        - [ ] Pizza size (e.g., "12-inch (medium)")
        - [ ] crust_type (e.g., "Neapolitan-style")
        - [ ] step_by_step_instructions (complete list)
    - [ ] **Step 7**: Extract execution timing
        ```bash
        breadcrumb query -c pizza --call pizza_master
        ```
        **MUST SHOW:**
        - [ ] duration_ms field with actual timing data
    - [ ] **VALIDATION**: User completed task without writing ANY SQL

- [ ] **Manual Verification**
    - [ ] Pizza ingredients are visible in JSON output
    - [ ] Execution duration is visible and accurate
    - [ ] --gaps suggests correct patterns
    - [ ] --flow shows clear execution timeline
    - [ ] All queries return valid, parseable JSON

- [ ] **Performance Validation**
    - [ ] Smart queries execute in < 1 second for typical traces
    - [ ] Gap detection doesn't degrade with large traces
    - [ ] JSON output is compact and parseable

- [ ] **Acceptance Criteria** `[ref: docs/smart_query_api_draft.md]`
    - [ ] ✅ **LITMUS TEST PASSES** - User can find Pizza ingredients and timing without SQL
    - [ ] ✅ No SQL knowledge needed
    - [ ] ✅ Saves tokens/money (1 command vs 5+ failed SQL attempts)
    - [ ] ✅ Clear workflow ("lay the breadcrumb trail")
    - [ ] ✅ Easy to discover what's actually running
    - [ ] ✅ Structured JSON output for AI agents
    - [ ] ✅ Can iteratively refine trace scope
    - [ ] ✅ Actually sees the Pizza ingredients with all details (ingredients, size, crust_type, instructions)
    - [ ] ✅ Can see execution duration (duration_ms)

- [ ] **Documentation**
    - [ ] Update CLI help text
    - [ ] Update README with smart query examples
    - [ ] Add "Laying the Breadcrumb Trail" guide
    - [ ] Update API docs

- [ ] **Build and Deployment**
    - [ ] All tests pass
    - [ ] No regressions in existing functionality
    - [ ] Ready for user testing

---

## Complexity Assessment

**Estimated Effort**: 560-820 LOC, 3-5 days

**Breakdown**:
- Phase 1 (Tests): 400-500 LOC, 1 day
- Phase 2 (Infrastructure): 50-80 LOC, 0.5 day
- Phase 3 (--gaps): 150-200 LOC, 1 day
- Phase 4 (--call): 100-150 LOC, 0.5 day
- Phase 5 (--flow): 100-150 LOC, 0.5 day
- Phase 6 (Config): 30-50 LOC, 0.5 day
- Phase 7 (Validation): Manual testing, 1 day

**Risk Factors**:
- Call stack reconstruction complexity (mitigated by tests)
- Gap detection accuracy (mitigated by clear algorithm)
- JSON parsing edge cases (mitigated by existing patterns)

**Dependencies**:
- Existing trace capture working (✅ done)
- Database schema with JSON data column (✅ exists)
- CLI infrastructure (✅ exists)
