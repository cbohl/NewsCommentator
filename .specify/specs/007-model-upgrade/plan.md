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

### Server-Side Length Tier Selection

Instead of asking the LLM to self-select a tier (which it ignores), the server picks the tier via `random.choices` and injects a direct instruction.

**Implementation**:

1. Define a helper `select_length_tier()` that returns a tier string:
   ```python
   import random

   LENGTH_TIERS = {
       "SHORT": "YOUR ASSIGNED LENGTH: SHORT (15–40 words). Write one or two punchy sentences. Do NOT exceed 40 words.",
       "MEDIUM": "YOUR ASSIGNED LENGTH: MEDIUM (50–90 words). Write a focused paragraph. Do NOT exceed 90 words.",
       "LONG": "YOUR ASSIGNED LENGTH: LONG (100–150 words). Develop a full argument. Do NOT exceed 150 words.",
   }

   def select_length_tier() -> str:
       tier = random.choices(["SHORT", "MEDIUM", "LONG"], weights=[30, 50, 20], k=1)[0]
       return LENGTH_TIERS[tier]
   ```

2. Each node function calls `select_length_tier()` and appends the result to the system message.

3. SYSTEM_RULES is simplified — remove the tier self-selection block, keep only:
   - Hard cap of 150 words
   - "Do NOT default to long" as a general reminder

### Constitution Updates

1. Amend Article III voice standard to reference the 30-100 word target range.
2. Update Technology Stack table: GPT-5-nano → GPT-5.2.
3. Add amendment log entries for 1.3.1 and 1.3.2.
4. Bump version to 1.3.2.
