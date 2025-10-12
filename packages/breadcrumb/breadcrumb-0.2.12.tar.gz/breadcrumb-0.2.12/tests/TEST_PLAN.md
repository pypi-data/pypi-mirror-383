# Testing Expansion Plan

Goal: raise coverage from ~51% to ≥80% by exercising core user workflows (CLI, instrumentation, storage) and safeguarding critical behaviours.

## 1. CLI Workflows
- [ ] Add end-to-end `CliRunner` tests for the top-level `breadcrumb` command (help, version).
- [ ] Cover `breadcrumb run` end-to-end: provide temp config; ensure wrapper script injects config includes/excludes, sample-rate, and `--max-chars`.
- [ ] Exercise `breadcrumb query` smart commands:
  - [ ] `--gaps`, `--call`, `--flow`, `--fuzzy` with realistic DuckDB fixtures.
  - [ ] Table output (`--format table`) with and without `--disable-truncation`.
  - [ ] Error scenarios (missing config, multiple query types).
- [ ] Test `breadcrumb config` subcommands through CLI (create/edit/list/show/delete/validate) to confirm option parsing and messaging.
- [ ] Add coverage for `breadcrumb top`, `breadcrumb list`, `breadcrumb get`, and `breadcrumb exceptions` when backed by a small fixture DB.

## 2. Instrumentation Backends
- [ ] Expand PEP 669 tests:
  - [ ] Verify include/exclude patterns, auto-filter, exception capture, async awareness.
  - [ ] Ensure `max_repr_length` affects args, kwargs, returns independently.
- [ ] Introduce regression tests for the `settrace` backend to at least sanity-check call/return capture.
- [ ] Test call-site gap detection pipeline end-to-end (call-site events persist → `gaps_query` surfaces them).

## 3. Storage Layer
- [ ] Cover `TraceWriter` queue overflow, truncation summaries, and context-manager behaviour.
- [ ] Add tests for `query_traces` timeout handling, invalid SQL, locked DB retries.
- [ ] Validate migration/connection helpers (`get_manager`, `reset_manager`) in isolation.
- [ ] Exercise retention policy (if restored) with synthetic timestamps.
- [ ] Include multi-trace flow tests (`flow_query`, `call_query`) with nested call trees.

## 4. Integration & Higher-Level Scenarios
- [ ] Simulate a full “init → run → query” lifecycle in-process using temporary scripts to ensure instrumentation + storage cooperate.
- [ ] Add tests for MCP server entrypoints (`serve_mcp`) with mocked streams (scope permitting).
- [ ] Ensure README / docs examples are runnable via automated smoke tests where feasible.

## 5. Tooling & Thresholds
- [ ] Keep `.coveragerc` updated as modules become fully covered (remove from omit list).
- [ ] Add a coverage gate to CI (e.g., `pytest --cov --cov-fail-under=80` once stable).
- [ ] Document fixture utilities and helpers inside `tests/` to reduce duplication.
