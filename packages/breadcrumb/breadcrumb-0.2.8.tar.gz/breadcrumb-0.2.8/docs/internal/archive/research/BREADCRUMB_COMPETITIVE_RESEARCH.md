# Breadcrumb Competitive Research: Execution Tracing & AI Agent Debugging Landscape

**Research Date:** October 10, 2025
**Researcher:** Technology Research Analysis
**Purpose:** Inform Breadcrumb PRD with competitive analysis, technology stack recommendations, and market gap identification

---

## Executive Summary

The execution tracing and debugging landscape for Python applications is fragmented between **production-focused APM tools** (DataDog, New Relic, Sentry), **AI-focused observability platforms** (LangSmith, Langfuse, Phoenix), and **developer debugging tools** (sys.settrace, VizTracer, rr).

**Key Finding:** There is a significant gap in the market for **AI-native execution tracing tools** that provide granular, queryable execution traces specifically designed for AI coding agents to understand code behavior without human-centric visualizations.

**Market Opportunity:** With MCP adoption projected to reach 90% of organizations by end of 2025 and major players (OpenAI, Google, Microsoft) adopting the protocol, there's a critical window to establish Breadcrumb as the standard debugging interface for AI agents.

---

## 1. Competitive Landscape Analysis

### 1.1 Python Execution Tracing Solutions

| Solution | Type | Target Audience | Auto-Instrumentation | Overhead | Data Richness | Query Interface | Unique Selling Points | Gaps/Weaknesses |
|----------|------|-----------------|---------------------|----------|---------------|-----------------|----------------------|-----------------|
| **sys.settrace** | Built-in tracer | Developers (dev) | Yes (code-level) | 2000%+ overhead | Every line executed | Python API | Built into Python, no dependencies | Unusably slow for production; dramatic slowdown in Python 3.12 (7x slower) |
| **PEP 669 (sys.monitoring)** | Built-in tracer | Developers (dev) | Yes (code-level) | 5% overhead | Selective events | Python API | 20x faster than sys.settrace; 1.2x slowdown when active | Python 3.12+ only; new API, limited adoption |
| **OpenTelemetry** | Observability framework | Production teams | Yes (framework-level) | 5-35% CPU | Spans/traces | OTLP, backends vary | Industry standard; broad framework support | Not designed for line-level tracing; requires backend infrastructure |
| **VizTracer** | Deterministic tracer | Developers (dev/debug) | Yes (code-level) | <1x overhead | Every function entry/exit | Perfetto UI, JSON | Timeline visualization; low overhead | Human-centric UI; no AI-native interface |
| **Py-Spy** | Sampling profiler | Production teams | Yes (process attach) | Minimal (<5%) | Statistical samples | Flame graphs | No code changes; Rust-based speed | Statistical (not deterministic); misses fine details |
| **eBPF-based** | Kernel-level profiler | Production/SRE | Yes (kernel-level) | <1% overhead | System-wide events | Various backends | Production-safe; no application changes | Requires kernel support; limited Python-level details |
| **rr debugger** | Record/replay | Developers (debug) | Yes (syscall record) | 1.2x overhead | Complete execution state | gdb interface | Time-travel debugging; deterministic replay | Linux x86-64 only; requires recording phase |

### 1.2 AI/LLM Observability Platforms

| Solution | Type | Target Audience | Auto-Instrumentation | Data Richness | Query Interface | MCP Support | Unique Selling Points | Gaps/Weaknesses |
|----------|------|-----------------|---------------------|---------------|-----------------|-------------|----------------------|-----------------|
| **LangSmith** | Proprietary platform | LLM app developers | Yes (LangChain native) | LLM traces, tokens | Web UI, API | No (closed) | Deep LangChain integration; enterprise features | Closed source; expensive self-hosting ($); LLM-focused only |
| **Langfuse** | Open-source platform | LLM app developers | Yes (multiple frameworks) | LLM traces, tokens | Web UI, SQL, API | No | Open source; free self-hosting; prompt management | Playground requires $100/user license; LLM-focused only |
| **Phoenix (Arize)** | Open-source platform | LLM app developers | Yes (OTEL-based) | LLM traces, embeddings | Web UI, API | No | OpenTelemetry-based; semantic analysis; fully OSS | LLM-focused only; no general Python tracing |
| **Pydantic Logfire** | Observability platform | Python/LLM developers | Yes (OTEL wrapper) | OTEL signals | Web UI, SQL | **Yes** (MCP server) | MCP integration; SQL queries; OTEL-based | Requires Logfire cloud/self-host; SaaS-first model |

### 1.3 MCP Debugging Servers

| Solution | Capabilities | Language Support | Installation | Unique Features | Limitations |
|----------|--------------|------------------|--------------|-----------------|-------------|
| **claude-debugs-for-you** | Interactive debugging via VSCode debugger | Language-agnostic | VSCode extension + Node.js server | Breakpoints, expression evaluation, natural language | Requires VSCode debugger setup; runtime-only |
| **Chrome DevTools MCP** | Browser debugging | JavaScript/Web | Node.js server | Chrome DevTools Protocol integration | Browser/web-only |
| **Pydantic Logfire MCP** | Log/trace querying | Python (via OTEL) | PyPI package (uvx) | SQL queries on traces; exception search | Requires Logfire platform; post-execution only |
| **mcp-pdb** | Python debugger | Python | Unknown | Python pdb integration | Limited documentation; runtime-only |

### 1.4 Traditional APM Tools

| Solution | Auto-Instrumentation | Overhead | Target Audience | Query Capabilities | Unique Selling Points | Limitations for AI Agents |
|----------|---------------------|----------|-----------------|-------------------|----------------------|---------------------------|
| **DataDog** | Yes (ddtrace) | Not disclosed | Production teams | Proprietary dashboards | Enterprise features; broad integrations | Expensive; human-centric dashboards; no MCP |
| **New Relic** | Yes (8 languages) | Not disclosed | Production teams | NRQL query language | All-in-one platform | Expensive; human-centric; no MCP |
| **Dynatrace** | Yes (OneAgent) | Not disclosed | Enterprise teams | Proprietary AI engine | AI-powered insights | Most expensive; human-centric; no MCP |
| **Sentry** | Yes (SDK-based) | Not disclosed | Dev + Production | Web UI, API | Error tracking focus; developer-friendly | Limited execution traces; human-centric |

---

## 2. Technology Stack Evaluation

### 2.1 Trace Collection Mechanisms

| Technology | Pros | Cons | Recommendation |
|------------|------|------|----------------|
| **sys.settrace** | Built-in, no dependencies, complete coverage | 2000%+ overhead, Python 3.12 regression | **Avoid** for production; ok for dev-only lightweight tracing |
| **PEP 669 (sys.monitoring)** | 20x faster than sys.settrace (5% overhead), selective events | Python 3.12+ only, newer API | **Recommended** for Python 3.12+; primary tracing mechanism |
| **OpenTelemetry** | Industry standard, broad ecosystem, 5-35% overhead | Framework-level only (not line-level), requires backend | **Use for integration**, not primary collection |
| **eBPF** | Production-safe (<1% overhead), no app changes | Kernel support required, limited Python details | **Future enhancement** for production environments |
| **Hybrid Approach** | Use PEP 669 for dev, eBPF for production, OTEL for integration | More complex implementation | **Ideal long-term strategy** |

**Recommendation:** Start with PEP 669 (sys.monitoring) as the primary mechanism, with fallback to sys.settrace for Python 3.11 and below. Add OpenTelemetry integration layer for compatibility.

### 2.2 Storage Backend

| Database | Pros | Cons | Best Use Case | Recommendation |
|----------|------|------|---------------|----------------|
| **DuckDB** | Embedded (no server), excellent analytical performance, SQL interface, Parquet integration | Single-machine only | Local development, single-session analysis | **Primary recommendation** |
| **SQLite** | Ubiquitous, zero-config, row-based | Poor analytical performance, not designed for OLAP | Metadata, configuration storage | **Use for metadata only** |
| **ClickHouse** | Distributed, petabyte-scale, real-time analytics, observability-focused | Requires server infrastructure, operational complexity | Multi-user production environments | **Future scaling option** |
| **Parquet + Arrow** | Columnar format, excellent compression, portable, Arrow in-memory performance | No query engine (need DuckDB/etc.), file-based | Data interchange, archival, sharing | **Use with DuckDB** for storage |

**Recommendation:** DuckDB as primary storage with Parquet export capability. DuckDB can:
- Query Parquet files directly (no import needed)
- Provide SQL interface for AI agents
- Run embedded (no server required)
- Achieve millisecond-latency queries on large traces
- Export to Parquet for sharing/archival

**Architecture Pattern:**
```
Trace Collection (PEP 669)
  → Stream to DuckDB (in-memory or persistent)
  → Export to Parquet for archival/sharing
  → MCP server queries DuckDB with SQL
```

### 2.3 MCP Server Framework

| Framework | Maturity | Developer Experience | Enterprise Features | Recommendation |
|-----------|----------|---------------------|-------------------|----------------|
| **FastMCP** | Mature (2.0), active development | Excellent (Pythonic, decorator-based) | Yes (auth, proxying, testing) | **Primary recommendation** |
| **Official Python SDK** | Mature, Anthropic-maintained | Good (lower-level) | Basic | **Use for edge cases** FastMCP doesn't cover |

**Recommendation:** FastMCP for rapid development with excellent DX. Example tool pattern:

```python
from fastmcp import FastMCP

mcp = FastMCP("Breadcrumb")

@mcp.tool
def query_traces(sql: str) -> dict:
    """Execute SQL query on execution traces"""
    return duckdb.execute(sql).fetchdf().to_dict()

@mcp.resource("trace://{trace_id}")
def get_trace(trace_id: str) -> str:
    """Get detailed trace by ID"""
    return duckdb.execute(
        "SELECT * FROM traces WHERE id = ?", [trace_id]
    ).fetchall()
```

---

## 3. AI Agent Debugging Patterns & Limitations

### 3.1 Current AI Agent Debugging Workflow

**Research Findings:**

1. **Claude Code** - Uses extended thinking methodology: reads files, pauses to analyze, develops strategy before coding. Lacks runtime execution visibility.

2. **Cursor** - State-of-the-art editing but limited runtime debugging. Can search web for docs but can't inspect actual execution.

3. **GitHub Copilot** - Sharp brevity, tight IDE integration, but minimal debugging capabilities beyond code reading.

**Common Pattern:**
```
Read source files → Analyze static code → Make educated guesses → Run tests → Iterate
```

### 3.2 Major Limitations

| Limitation | Impact | Current Workaround | Breadcrumb Opportunity |
|------------|--------|-------------------|------------------------|
| **No execution visibility** | Agents guess at runtime behavior | Read stack traces after crash | Provide pre-execution traces |
| **Context window constraints** | Limited to small codebase subset | Summarization, sub-agents | Query-driven trace exploration |
| **Black-box execution** | Can't see intermediate states | Add print statements manually | Auto-capture all variables/state |
| **Async debugging difficulty** | Race conditions invisible | Trial-and-error | Timeline visualization in SQL |
| **Long conversation depth** | Context rot, loss of focus | Start new conversation | Persistent trace storage |
| **Static analysis only** | Misunderstand dynamic behavior | Guess from code structure | Ground understanding in actual execution |

### 3.3 Ideal AI Agent Debugging Workflow (with Breadcrumb)

```
1. User reports bug → Agent reads error
2. Agent queries: "SELECT * FROM traces WHERE exception IS NOT NULL ORDER BY timestamp DESC LIMIT 1"
3. Agent analyzes trace_id: "SELECT function_name, line, variables FROM trace_events WHERE trace_id = X"
4. Agent identifies root cause in trace data
5. Agent fixes code based on actual execution, not guesses
6. Agent verifies: "SELECT * FROM traces WHERE function = 'fixed_function' ORDER BY timestamp DESC LIMIT 1"
```

### 3.4 Key Insight: AI Agents Need Data, Not Dashboards

**Human Tools:**
- Visual dashboards (charts, graphs, flame graphs)
- Interactive UIs (click to expand)
- Pretty formatting (colors, icons)

**AI Agent Tools:**
- Structured data (JSON, SQL results)
- Query interfaces (SQL, GraphQL, semantic search)
- Programmatic access (APIs, MCP tools)

**Breadcrumb Differentiation:** Design for AI consumption first, human consumption second (opposite of all existing tools).

---

## 4. Market Gaps & Breadcrumb Positioning

### 4.1 Identified Gaps

| Gap | Current Landscape | Breadcrumb Opportunity | Market Size Indicator |
|-----|------------------|------------------------|------------------------|
| **AI-native debugging** | All tools designed for humans | First MCP-native execution tracer | MCP adoption: 90% of orgs by EOY 2025 |
| **Line-level Python tracing** | APMs do framework-level only | PEP 669-based line-level tracing | Python #2 most used language |
| **Query-driven exploration** | Visual UIs, limited SQL/API access | SQL-first interface for agents | DuckDB analytical queries in milliseconds |
| **Lightweight dev tracing** | Sentry/DataDog too heavy for dev | Zero-config embedded tracing | Every Python developer (millions) |
| **Open MCP ecosystem** | Proprietary platforms (LangSmith, Logfire) | Open source, self-hostable | OSS preference in dev tools |
| **Cross-framework support** | LangSmith = LangChain only | Framework-agnostic Python tracing | Broader addressable market |

### 4.2 Competitive Positioning Matrix

```
                    Production-Ready
                           ↑
        Sentry/DataDog    |    ClickHouse/OTEL
                          |
        LangSmith/        |         ???
        Langfuse          |
                          |
←─────────────────────────┼─────────────────────────→
Human-Centric            |            AI-Native
                          |
        sys.settrace/     |    [BREADCRUMB]
        VizTracer         |    - MCP-first
                          |    - SQL queries
                          |    - PEP 669 tracing
                          |    - DuckDB backend
                          |
                          ↓
                    Dev/Debug-Focused
```

**Breadcrumb Sweet Spot:** AI-native, dev-focused execution tracing with production-capable performance (PEP 669).

### 4.3 Unique Value Propositions

1. **First AI-Native Execution Tracer**
   - Designed for LLM consumption, not human visualization
   - MCP protocol as primary interface
   - SQL queries instead of dashboards

2. **Zero-Infrastructure Embedded Database**
   - No server setup required
   - DuckDB runs in-process
   - Instant queries on million-event traces

3. **Line-Level Python Visibility**
   - Captures every execution step
   - Not just framework boundaries (like OTEL)
   - Variable state at each line

4. **Open & Self-Hosted**
   - No vendor lock-in
   - No data leaves your machine
   - Open source from day one

5. **Production-Capable Performance**
   - PEP 669: 5% overhead (vs 2000% for sys.settrace)
   - Selective instrumentation
   - Can run in production with sampling

### 4.4 Anti-Positioning (What Breadcrumb Is NOT)

- **Not an APM replacement** - Breadcrumb complements, doesn't replace DataDog/New Relic for production monitoring
- **Not LLM-specific** - Works for any Python code, not just AI applications
- **Not a visual debugger** - Primarily API/MCP interface, not GUI
- **Not distributed tracing** - Focus on single-process detailed tracing, not microservices
- **Not real-time streaming** - Focus on query-after-execution, not live dashboards

---

## 5. Technology Performance Benchmarks

### 5.1 Tracing Overhead Comparison

| Technology | Overhead (CPU) | Use Case | Source |
|------------|---------------|----------|--------|
| sys.settrace | 2000%+ | Development only | Python docs, GitHub issues |
| PEP 669 (sys.monitoring) | 5% (no events), ~20% (LINE events) | Dev + Production | PEP 669 specification, PyDev blog |
| OpenTelemetry | 5-35% (configurable) | Production (with sampling) | Cross-language studies |
| eBPF | <1% | Production | Grafana Pyroscope docs |
| Py-Spy | <5% | Production sampling | Py-Spy docs |
| VizTracer | <100% (1x) | Development | VizTracer docs |

### 5.2 Storage Performance Benchmarks

| Database | Query Latency | Analytical Performance | Use Case |
|----------|---------------|----------------------|----------|
| DuckDB | Milliseconds on GB data | Excellent (columnar OLAP) | Analytical queries |
| SQLite | Sub-millisecond on MB data | Poor (row-based OLTP) | Transactional queries |
| ClickHouse | Sub-second on TB data | Excellent (distributed) | Multi-node production |
| Parquet (raw) | N/A (requires engine) | Excellent (with DuckDB/etc.) | Storage format |

**Key Insight:** DuckDB can query Parquet with millisecond latency without importing data.

---

## 6. MCP Ecosystem Context

### 6.1 Adoption Statistics (2025)

- **90% of organizations** projected to use MCP by end of 2025
- **Major adopters:** OpenAI (March 2025), Google DeepMind (April 2025), Microsoft, AWS
- **Market growth:** $1.2B (2022) → $4.5B (2025)
- **Enterprise deployment:** Block has 60+ MCP servers, thousands of daily users
- **Developer platforms:** Replit, Sourcegraph, Zed, Codeium, Apollo

### 6.2 MCP Debugging Servers (Current)

| Server | Focus | Maturity | Breadcrumb Comparison |
|--------|-------|----------|----------------------|
| claude-debugs-for-you | Runtime debugging (VSCode) | Early | Complementary (Breadcrumb = post-execution) |
| Pydantic Logfire MCP | Log/trace querying | Mature | Direct competitor (but requires Logfire platform) |
| Chrome DevTools MCP | Browser debugging | Mature | Different domain (web vs Python) |
| mcp-pdb | Python pdb integration | Unknown | Complementary (runtime vs post-execution) |

**Gap:** No dedicated Python execution tracer with MCP interface that works standalone.

---

## 7. Key Research Insights for PRD

### 7.1 Target Personas

**Primary: AI Coding Agent Developer**
- Uses Claude Code, Cursor, or Copilot
- Frustrated by agents that can't debug effectively
- Wants agents to understand execution, not just code
- Prefers open-source, self-hosted tools

**Secondary: Python Developer (Human)**
- Debugging complex async code
- Needs more than print statements
- Wants lightweight tool for dev environment
- Tired of heavy APM setup for local debugging

**Tertiary: LLM Application Developer**
- Building with LangChain, LlamaIndex, custom frameworks
- Needs to debug agent behavior
- Wants more detail than LangSmith/Langfuse provide

### 7.2 Must-Have Features (Informed by Research)

1. **MCP Server Interface**
   - Tools: `query_traces(sql)`, `get_trace(id)`, `find_exceptions()`, `analyze_performance()`
   - Resources: Individual traces as `trace://{id}`
   - FastMCP-based implementation

2. **PEP 669 Tracing Engine**
   - Auto-instrumentation of Python code
   - Line-level execution capture
   - Variable state recording
   - Selective instrumentation (avoid overhead on hot paths)

3. **DuckDB Storage Backend**
   - Embedded database (no server)
   - SQL query interface
   - Parquet export
   - Schema: traces, trace_events, variables, exceptions

4. **Zero-Configuration Setup**
   - `pip install breadcrumb` → works immediately
   - No config files required
   - Auto-detect MCP client (Claude Desktop, Cursor)

### 7.3 Differentiation from Competitors

| Competitor | What They Do Well | What Breadcrumb Does Better |
|------------|------------------|----------------------------|
| **sys.settrace** | Built-in, simple | 400x faster (PEP 669) |
| **OpenTelemetry** | Industry standard | Line-level detail (not just spans) |
| **VizTracer** | Timeline visualization | AI-queryable (SQL), MCP interface |
| **LangSmith/Langfuse** | LLM-specific tracing | General Python, open source, embedded |
| **Pydantic Logfire MCP** | MCP + SQL queries | No platform required, self-contained |
| **DataDog/Sentry** | Production monitoring | Dev-focused, lightweight, free |

### 7.4 Success Metrics (Recommended)

**Adoption Metrics:**
- MCP server connections per week
- `pip install breadcrumb` downloads
- GitHub stars / community engagement

**Engagement Metrics:**
- Queries per trace session
- Trace storage size (GB) per user
- Repeat usage rate

**Quality Metrics:**
- Query latency (p50, p95, p99)
- Tracing overhead (% CPU)
- Bug discovery rate (traces with exceptions)

**AI Agent Impact:**
- Debugging success rate (before/after)
- Time to fix bugs (with/without Breadcrumb)
- Agent conversation length reduction

---

## 8. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **PEP 669 adoption slow** | High | Medium | Fallback to sys.settrace for Python <3.12 |
| **MCP ecosystem stalls** | High | Low | Also provide REST API, Python SDK |
| **DuckDB performance issues** | Medium | Low | Benchmark early; have ClickHouse migration path |
| **Storage size explosion** | Medium | Medium | Sampling, configurable detail levels, auto-cleanup |
| **Competitors add MCP** | Medium | Medium | First-mover advantage, open-source community |
| **Overhead unacceptable in production** | High | Low | Default to dev-only; add sampling for production |

---

## 9. Open Questions for PRD Development

1. **Pricing Model:** Free OSS with hosted option? Fully free? Enterprise support model?
2. **Default Sampling:** Should tracing be always-on or opt-in per function/module?
3. **Data Retention:** How long to keep traces? Auto-deletion policy?
4. **Multi-Language:** Should we plan for JS/TypeScript/Go support beyond Python?
5. **Real-Time vs Batch:** Should MCP server support live tracing or only post-execution?
6. **Privacy:** How to handle sensitive data in traces (env vars, secrets, PII)?
7. **Integration Priority:** Which frameworks to integrate first (FastAPI, Django, Flask, LangChain)?

---

## 10. Recommended Next Steps

1. **Validate with Users**
   - Interview 10 AI agent developers about debugging pain points
   - Survey 50+ Python developers on tracing needs
   - Beta test MCP interface with Claude Code users

2. **Technical Proof-of-Concept**
   - Build minimal PEP 669 tracer + DuckDB storage (1-2 weeks)
   - Implement basic MCP server with 3 tools (1 week)
   - Benchmark overhead and query performance (1 week)

3. **Refine PRD**
   - Define user stories based on research findings
   - Prioritize features using MoSCoW framework
   - Create detailed acceptance criteria

4. **Community Building**
   - Create GitHub repo with vision doc
   - Write blog post: "Why AI Agents Need Execution Traces"
   - Engage MCP community on Discord/forums

---

## 11. References & Sources

### Research Sources

**Python Tracing:**
- PEP 669 specification (peps.python.org/pep-0669)
- Python sys module documentation
- PyDev Debugger blog post on sys.monitoring
- Python 3.12 performance regression GitHub issue #107674

**OpenTelemetry:**
- OTEL Python documentation (opentelemetry.io/docs/languages/python)
- Performance benchmarking discussions (GitHub)
- SigNoz, HyperDX OTEL guides
- Coroot Go overhead study (proxy for Python)

**MCP Ecosystem:**
- Anthropic MCP announcement (anthropic.com/news/model-context-protocol)
- Block MCP enterprise case study (block.github.io/goose)
- MCP adoption projections (Abovo research report)
- FastMCP documentation (github.com/jlowin/fastmcp)

**Databases:**
- DuckDB documentation (duckdb.org)
- MotherDuck DuckDB vs SQLite comparison
- ClickHouse vs DuckDB performance analyses (Airbyte, Cloudraft, bicortex)
- Apache Arrow/Parquet documentation

**AI Observability:**
- Langfuse vs LangSmith comparisons (langfuse.com, various blogs)
- Phoenix (Arize AI) documentation (phoenix.arize.com)
- Pydantic Logfire MCP announcement (pydantic.dev/articles/mcp-launch)
- Agent tracing blog posts (Maxim, AWS)

**AI Agent Debugging:**
- Microsoft Research Debug-gym paper
- Claude Code vs Cursor comparisons (Haihai AI, Qodo, Render benchmarks)
- JetBrains AI agent notebook debugging blog
- Akira.ai future of debugging article

**Alternative Tools:**
- VizTracer documentation (github.com/gaogaotiantian/viztracer)
- Py-Spy documentation (github.com/benfred/py-spy)
- rr debugger documentation (rr-project.org)
- eBPF profiling guides (Brendan Gregg, Grafana)

**APM Tools:**
- DataDog vs Dynatrace vs New Relic comparisons (Better Stack, SigNoz)
- Sentry Python tracing documentation
- APM overhead discussions (various forums)

---

## Appendix A: Glossary

- **APM:** Application Performance Monitoring
- **eBPF:** Extended Berkeley Packet Filter (Linux kernel tracing)
- **MCP:** Model Context Protocol (Anthropic's protocol for AI context)
- **OTEL/OpenTelemetry:** Open-source observability framework
- **PEP 669:** Python Enhancement Proposal for low-impact monitoring
- **Span:** Unit of work in distributed tracing
- **Trace:** Complete execution path through a system
- **OLAP:** Online Analytical Processing (analytics databases)
- **OLTP:** Online Transaction Processing (transactional databases)

---

## Appendix B: Example Use Cases

### Use Case 1: AI Agent Debugs Async Race Condition

**Without Breadcrumb:**
```
Agent: I see you have async code. Race conditions are tricky.
       Try adding locks around shared state. [guessing]
User: Still broken.
Agent: Maybe try asyncio.sleep to change timing? [more guessing]
```

**With Breadcrumb:**
```
Agent: Let me query execution traces...
       > SELECT * FROM traces WHERE has_exception ORDER BY timestamp DESC LIMIT 1
Agent: I found the trace. Analyzing event timeline...
       > SELECT timestamp, function, line, variables
         FROM trace_events WHERE trace_id = 'abc123' ORDER BY timestamp
Agent: I see variable 'counter' was modified at:
       - Line 45 by task_1 at t=100ms (value: 5 → 6)
       - Line 67 by task_2 at t=101ms (value: 5 → 6)
       Both read value 5 and incremented. This is a race condition.
       Fix: Add asyncio.Lock around lines 45-46 and 67-68.
```

### Use Case 2: Human Developer Debugs Complex State Mutation

**Scenario:** Multi-step state transformation, unclear where bug occurs

**Query:**
```sql
-- Find where user.balance becomes negative
SELECT
  function_name,
  line,
  variables->>'user.balance' as balance,
  timestamp
FROM trace_events
WHERE trace_id = 'xyz789'
  AND variables->>'user.balance' IS NOT NULL
ORDER BY timestamp
```

**Result:**
```
withdraw_funds  | 45 | 100.00  | t=0ms
process_fee     | 78 | 95.00   | t=10ms
apply_discount  | 112| 85.00   | t=15ms
charge_card     | 156| -15.00  | t=25ms  ← Bug: should check balance first
```

**Fix:** Add balance check before `charge_card()` call.

---

*End of Research Report*
