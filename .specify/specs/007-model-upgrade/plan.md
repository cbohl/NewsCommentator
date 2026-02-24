# Implementation Plan: Model Upgrade & Response Length Tuning

**Branch**: `007-model-upgrade` | **Date**: 2026-02-23 | **Spec**: `specs/007-model-upgrade/spec.md`

## Summary

Upgrade LLM from GPT-5-nano to GPT-5.2 and rewrite SYSTEM_RULES with explicit SHORT/MEDIUM/LONG length tiers to produce more natural response length variation.

## Technical Context

**Files affected**:
- `backend/app/graph/nodes.py` — Change model in `_get_llm()`, rewrite SYSTEM_RULES with length tiers
- `.specify/memory/constitution.md` — Amendments 1.3.1 (length refinement) and 1.3.2 (model upgrade), update Technology Stack table

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Anti-AI-ism Voice | AMENDMENT 1.3.1 | Add target 30-100 words, explicit tier percentages |
| Technology Stack | AMENDMENT 1.3.2 | GPT-5-nano → GPT-5.2 |

## Design

### Model Swap

Single-line change in `_get_llm()`:
```python
_llm = ChatOpenAI(model="gpt-5.2")  # was gpt-5-nano
```

### SYSTEM_RULES Rewrite

Replace the existing length guidance with explicit tiers:

```
CRITICAL — LENGTH RULES:
- You MUST vary your word count. Pick ONE of these lengths for each response:
  SHORT (15–40 words): A single sharp sentence or two. Use this ~30% of the time.
  MEDIUM (50–90 words): A focused paragraph. Use this ~50% of the time.
  LONG (100–150 words): A full argument. Use this only ~20% of the time.
- Decide your length BEFORE you start writing. Do NOT default to long.
```

### Constitution Updates

1. Amend Article III voice standard to reference the 30-100 word target range.
2. Update Technology Stack table: GPT-5-nano → GPT-5.2.
3. Add amendment log entries for 1.3.1 and 1.3.2.
4. Bump version to 1.3.2.
