# Smart Query API Draft

## Problem Statement

**Current issues:**
- Raw SQL queries are difficult to write, error-prone, and waste tokens/money
- Workspace filtering is confusing and battles with exclude patterns
- Hard to discover what code is actually being called
- No iterative workflow for focusing on relevant code

**Token waste example:**
```bash
# User wants to see Pizza ingredients
# Current: 5+ failed SQL attempts, 10k+ tokens wasted
breadcrumb query "SELECT ... WHERE data LIKE '%ingredient%' ..." # syntax error
breadcrumb query "SELECT ... WHERE data != '{\"is_async\": true}' ..." # escaping hell
breadcrumb query "SELECT ... WHERE function_name = 'Pizza' ..." # no data captured

# Desired: 1 simple command, <100 tokens
breadcrumb query --call Pizza
```

---

## Solution 1: Smart Query Commands

Replace raw SQL with semantic queries that understand your code.

### Core Smart Queries

#### `--call <function>` - Show function calls with I/O
```bash
# Show all calls to a function with args/returns
breadcrumb query -c pizza --call Pizza
breadcrumb query --call "flock.orchestrator.publish"

# Output:
{
  "function": "Pizza",
  "calls": [
    {
      "timestamp": "2025-10-11T15:14:36",
      "args": {
        "ingredients": ["tomato sauce", "mozzarella", "truffle oil"],
        "size": "large",
        "crust_type": "thin"
      },
      "return_value": {
        "Pizza": {
          "ingredients": ["..."],
          "size": "large",
          "step_by_step_instructions": ["1. Preheat oven...", "..."]
        }
      },
      "duration_ms": 234.5,
      "called_by": "__main__.main",
      "calls_made": [
        "pydantic.BaseModel.__init__",
        "pydantic.validate"
      ]
    }
  ]
}
```

#### `--trace <function>` - Show full call tree
```bash
# Show what a function calls (and what those call)
breadcrumb query --trace main --depth 3

# Output: Tree showing main() -> publish() -> serialize() -> ...
```

#### `--flow` - Show execution flow
```bash
# Show chronological execution with I/O
breadcrumb query --flow --module __main__

# Output:
1. __main__.main() called
   args: {}
2.   flock.orchestrator.publish(pizza_idea) called  # <-- NOT TRACED (needs include)
   args: {"pizza_idea": {"pizza_idea": "pizza with tartufo"}}
3.   flock.orchestrator.run_until_idle() called  # <-- NOT TRACED
4. __main__.main() returned
   duration: 12.3s
```

#### `--data <type>` - Find data by type
```bash
# Find all Pizza objects that were created
breadcrumb query --data Pizza

# Find all exceptions
breadcrumb query --data Exception
```

#### `--expensive` - Find slow functions
```bash
# Show slowest functions
breadcrumb query --expensive --limit 10

# Output:
{
  "slowest_functions": [
    {"function": "openai.chat.complete", "avg_ms": 2341, "calls": 3},
    {"function": "flock.orchestrator.run_until_idle", "avg_ms": 1234, "calls": 1}
  ]
}
```

#### `--called-by <function>` - Reverse lookup
```bash
# What called this function?
breadcrumb query --called-by "openai.chat.complete"
```

#### `--gaps` - Show untraced calls (THE KEY FEATURE!)
```bash
# Show which functions were called but NOT traced
breadcrumb query --gaps

# Output:
{
  "untraced_calls": [
    {
      "function": "flock.orchestrator.publish",
      "called_by": "__main__.main",
      "call_count": 1,
      "suggested_include": "flock.orchestrator.*"
    },
    {
      "function": "flock.orchestrator.run_until_idle",
      "called_by": "__main__.main",
      "call_count": 1,
      "suggested_include": "flock.orchestrator.*"
    }
  ],
  "tip": "Add these to your config to trace them:\n  breadcrumb config edit pizza --add-include 'flock.orchestrator.*'"
}
```

---

## Solution 2: Iterative Include-Only Workflow

### "Laying the Breadcrumb Trail"

**Core Philosophy:**
- No workspace filtering (too confusing)
- No exclude patterns (battling namespace hell)
- **Only include patterns** - you explicitly say what to trace
- Start with the entry point file, then iteratively expand

### Default Behavior
```bash
# By default: only trace the target file
breadcrumb run -t 60 python pizza.py

# Only traces:
# - __main__.<module>
# - __main__.main
# - __main__.MyDreamPizza
# - __main__.Pizza
```

This shows you **what these functions call** but doesn't trace those calls yet.

### Iterative Expansion

#### Step 1: See what your code calls
```bash
breadcrumb query --gaps

# Output:
Untraced calls from your code:
  - flock.orchestrator.publish (called 1x from __main__.main)
  - flock.orchestrator.run_until_idle (called 1x from __main__.main)

Suggestion: breadcrumb config edit pizza --add-include 'flock.orchestrator.*'
```

#### Step 2: Add what's interesting
```bash
breadcrumb config edit pizza --add-include 'flock.orchestrator.*'
breadcrumb run -c pizza -t 60 python pizza.py
```

Now you see:
- Your `__main__` code
- `flock.orchestrator.*` code
- What orchestrator calls (but not traced yet)

#### Step 3: Keep expanding the trail
```bash
breadcrumb query --gaps

# Output:
Untraced calls from flock.orchestrator:
  - flock.agent.on_evaluate (called 3x from flock.orchestrator.dispatch)
  - openai.chat.complete (called 1x from flock.agent.on_evaluate)

Suggestion: Add the interesting ones!
  breadcrumb config edit pizza --add-include 'flock.agent.on_evaluate'
  breadcrumb config edit pizza --add-include 'openai.chat.*'
```

#### Step 4: You've laid the perfect trail!
```yaml
# pizza.yaml now contains exactly what you need
include:
  - '__main__'
  - 'flock.orchestrator.*'
  - 'flock.agent.on_evaluate'
  - 'openai.chat.*'
```

This gives you:
- Zero noise from irrelevant code
- Complete visibility into the execution path
- Easy to understand what's happening
- Agent can see Pizza ingredients because you traced the right functions!

---

## How to Use Breadcrumb: "First, Lay the Breadcrumb Trail!"

### Quick Start Guide

**1. Start with just your file**
```bash
breadcrumb run -t 60 python pizza.py
```

**2. See what you're missing**
```bash
breadcrumb query --gaps
```

**3. Add the interesting bits**
```bash
breadcrumb config edit pizza --add-include 'flock.orchestrator.*'
breadcrumb run -c pizza -t 60 python pizza.py
```

**4. Repeat until you can see the data you need**
```bash
breadcrumb query --call Pizza  # Can I see ingredients? Yes!
```

### Why This Is Better

**Old Way (Workspace + Excludes):**
- ❌ Traces EVERYTHING in workspace (noisy!)
- ❌ Fight with exclude patterns (pydantic, typing, etc.)
- ❌ Hard to know what's relevant
- ❌ Captures 10,000 events you don't care about

**New Way (Include-Only Trail):**
- ✅ Start minimal (just your file)
- ✅ Iteratively expand (follow the breadcrumbs)
- ✅ Only trace what matters
- ✅ See exactly where data flows

---

## Smart Query Implementation Priority

### Phase 1 (MVP)
1. `--gaps` - Show untraced calls (THE KILLER FEATURE)
2. `--call <function>` - Show function I/O
3. `--flow` - Show execution timeline

### Phase 2
4. `--trace <function>` - Call tree
5. `--expensive` - Performance analysis
6. `--data <type>` - Find objects by type

### Phase 3
7. `--called-by` - Reverse lookup
8. Natural language queries: "show me all Pizza objects created"

---

## Config Changes

### New Default Config
```yaml
# Default: Only trace the target file
enabled: true
include:
  - '__main__'  # Only the file you're running
# Note: No exclude patterns - include-only workflow
```

### Iterative Include Workflow
```bash
# Add includes easily
breadcrumb config edit pizza --add-include 'flock.agent.*'

# Remove if too noisy
breadcrumb config edit pizza --remove-include 'flock.logging.*'

# See what you're tracing
breadcrumb config show pizza
```

---

## Benefits

### For Users
- ✅ No SQL knowledge needed
- ✅ Saves tokens/money (1 command vs 5+ failed SQL attempts)
- ✅ Clear workflow ("lay the breadcrumb trail")
- ✅ Easy to discover what's actually running

### For AI Agents
- ✅ Structured JSON output (easy to parse)
- ✅ Clear next steps (--gaps tells you what to include)
- ✅ Can iteratively refine the trace scope
- ✅ Actually sees the Pizza ingredients!

### For Debugging
- ✅ See function I/O without print statements
- ✅ Understand execution flow
- ✅ Find performance bottlenecks
- ✅ Track data transformations

---

## Branding

**Tagline:** "First, lay the breadcrumb trail!"

**How it works:**
1. Run your code with minimal tracing (just your file)
2. See what functions get called (breadcrumb query --gaps)
3. Add the interesting ones to your trail (--add-include)
4. Follow the breadcrumbs deeper until you see what you need!

**Marketing copy:**
> "Stop battling with exclude patterns and workspace filters. Instead, lay a breadcrumb trail through your code. Start with your entry point, see what it calls, and iteratively expand until you can see exactly what you need. No noise. No confusion. Just follow the breadcrumbs."

---

## Example: Debugging Pizza Example

```bash
# Run 1: Just my code
$ breadcrumb run -t 60 python pizza.py
# 8 events captured

# What am I missing?
$ breadcrumb query --gaps
Untraced calls:
  - flock.orchestrator.publish
  - flock.orchestrator.run_until_idle
Suggestion: breadcrumb config edit pizza --add-include 'flock.orchestrator.*'

# Run 2: Add orchestrator
$ breadcrumb config edit pizza --add-include 'flock.orchestrator.*'
$ breadcrumb run -c pizza -t 60 python pizza.py
# 45 events captured

# Can I see Pizza ingredients yet?
$ breadcrumb query --call Pizza
{
  "function": "Pizza",
  "calls": [
    {
      "args": {
        "ingredients": ["tomato sauce", "mozzarella", "truffle oil"],
        "size": "large",
        "crust_type": "thin",
        "step_by_step_instructions": ["1. Preheat oven to 450°F", ...]
      }
    }
  ]
}

# SUCCESS! 🎉
```

---

## Implementation Notes

### Smart Query Engine
- Parse command-line args into structured queries
- Map to efficient SQL under the hood
- Return structured JSON (not raw SQL results)
- Include suggestions for next steps

### Gap Detection Algorithm
1. Track all function calls (PY_START events)
2. Mark which ones we actually captured events for
3. Diff: calls_seen - calls_traced = gaps
4. Suggest include patterns based on module names

### Include-Only Mode
1. Remove workspace_only filter entirely (or make it opt-in)
2. Default include: `['__main__']` only
3. Add `--gaps` command to discover what to include next
4. Make `--add-include` super easy to use
