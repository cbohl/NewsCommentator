# Implementation Plan: Persona Interaction & Randomized Order

**Branch**: `003-persona-interaction` | **Date**: 2026-02-20 | **Spec**: `specs/003-persona-interaction/spec.md`
**Depends on**: 002-prompt-refinement (prompts should already be natural before adding interaction)

## Summary

Replace the fixed Historian → Economist → Philosopher graph with a dynamic graph that shuffles execution order per article. Modify node functions to include prior comments in their prompts so personas can engage with each other.

## Technical Context

**Files affected**:
- `backend/app/graph/state.py` — Add `execution_order` field
- `backend/app/graph/nodes.py` — Modify node functions to include prior comments in prompt
- `backend/app/graph/workflow.py` — Replace static graph with per-invocation dynamic ordering
- `backend/app/services/pipeline.py` — Pass shuffled order, log execution order
- `.specify/memory/constitution.md` — Amend Data Flow Contract + bump version

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | Still using StateGraph, just dynamic edge ordering |
| II. Expert Persona Integrity | PASS | Same three personas, same lenses, same constraints |
| III. Anti-AI-ism Voice | PASS | No change to voice rules |
| Data Flow Contract | AMENDMENT | Fixed order → randomized order per article |

## Design

### Dynamic Graph Compilation

Instead of one compiled graph at module level, create a function `build_commentary_graph(order: list[str])` that:
1. Takes a list like `["philosopher", "economist", "historian"]`
2. Builds a `StateGraph` with edges in that order
3. Compiles and returns it

Called per-article in `pipeline.py` with `random.shuffle()`.

### Prior Comment Injection

Each node function already receives the full `CommentaryState`. The change:
- Build a `prior_comments` string from any non-empty comment fields in state
- If `prior_comments` is non-empty, append to the user message:
  ```
  Previous commentary on this article:
  {prior_comments}

  You may agree, disagree, or build on what your colleagues have said — or ignore them entirely.
  ```

### State Extension

Add to `CommentaryState`:
```python
execution_order: list[str]
```

## Complexity Tracking

No constitution violations beyond the planned amendment.
