# Implementation Plan: Tool Simplification — One Specialized Tool Per Persona

**Branch**: `give-additional-tools-to-agents` | **Date**: 2026-02-27 | **Spec**: `specs/012-tool-simplification/spec.md`

## Summary

Remove Tavily web search from historian and economist, giving each persona exactly one specialized tool: historian gets Wikipedia, economist gets Yahoo Finance, philosopher gets Tavily. Revert max_tool_calls to 2 for all personas since each has only one tool type.

## Technical Context

**Languages**: Python 3.12+
**New dependencies**: None
**New env vars**: None

**Files to modify**:
- `backend/app/graph/nodes.py` — Rewrite `_get_persona_tools()`, revert `max_tool_calls` to default 2
- `backend/app/graph/prompts/historian.md` — Remove "use web search for..." fallback language
- `backend/app/graph/prompts/economist.md` — Remove "use web search for..." fallback language

**Files NOT modified**:
- `backend/app/routers/chat.py` — Chat unchanged
- `backend/app/schemas.py` — Schema unchanged
- `frontend/` — Frontend unchanged
- `backend/app/services/pipeline.py` — Pipeline unchanged

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | Tool dispatch still within graph nodes |
| II. Expert Persona Integrity | PASS | Same personas, more focused tools |
| III. Anti-AI-ism Voice | PASS | No change to voice or output format |
| IV. Idempotent Processing | PASS | No schema changes |
| V. Resilience | PASS | Each tool failure still falls back gracefully |
| VII. Simplicity | PASS | Simpler — fewer tools per persona |

## Design

### 1. Rewrite `_get_persona_tools()`

Remove the shared Tavily step. Each persona gets exactly one tool:

```python
def _get_persona_tools(persona: str) -> list:
    if persona == "historian":
        wiki = _get_wikipedia_tool()
        return [wiki] if wiki else []
    elif persona == "economist":
        yf = _get_yahoo_finance_tool()
        return [yf] if yf else []
    else:  # philosopher
        tavily = _get_search_tool()
        return [tavily] if tavily else []
```

### 2. Revert max_tool_calls

Historian and economist were bumped to `max_tool_calls=3` when they had two tool types. Now that each has one, revert to the default of 2.

### 3. Update persona prompts

Remove "use web search for..." fallback language from historian and economist prompts since web search is no longer available to them.

## Backwards Compatibility

- No data format changes. Footnotes still use `list[dict]` with source labels.
- Old comments with "(Web)" labels from historian/economist remain valid.
- Pipeline output is the same shape — just different tool sources.
