# Implementation Plan: Prompt Tuning Round 1 — Voice & Tool Usage

**Branch**: `deepeval-prompt-testing` | **Date**: 2026-02-28 | **Spec**: `specs/015-prompt-tuning-round1/spec.md`

## Summary

Iterative prompt tuning driven by DeepEval test results. Two rounds of changes targeting philosopher voice distinctiveness, tool usage rates, tool result citation, and historian off-topic resilience.

## Technical Context

**Languages**: Python 3.12+
**New dependencies**: None
**New env vars**: None

**Files modified**:
- `backend/app/graph/prompts/philosopher.md`
- `backend/app/graph/prompts/historian.md`
- `backend/app/graph/prompts/economist.md`
- `backend/app/graph/prompts/search_instructions.md`
- `backend/app/graph/nodes.py` (minor: `result_snippet` field)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| II. Expert Persona Integrity | PASS | Personas unchanged — voice strengthened, not altered |
| III. Anti-AI-ism Voice | PASS | Prompts reinforce concise, opinionated style |
| VII. Simplicity | PASS | Prompt-only changes, no new abstractions |

## Design

### Round 1 Changes

1. **`philosopher.md`**: Added `Analytical Toolkit` section listing specific frameworks (Kantian ethics, utilitarianism, Rawlsian justice, social contract theory, Foucault, veil of ignorance). Added instruction to name concepts when they do real work. Added `Research Tools` section telling Sofia to search on every article for philosophical concepts.

2. **`historian.md`**: Added off-topic resilience sentence listing parallels by domain. Changed "use it!" to "search it on EVERY article" with explicit pre-writing question.

3. **`economist.md`**: Changed "use it!" to "search it on EVERY article" with ticker mappings by topic (defense → LMT, finance → JPM, etc.).

4. **`search_instructions.md`**: Rewrote from "You SHOULD use them" to "USE IT on every article." Added grounding mandate: "you MUST incorporate what you find into your prose." Removed per-tool descriptions since each persona only has one tool. Simplified to refer to "a research tool" singular.

### Round 2 Changes

5. **`economist.md`**: Escalated to "MANDATORY: Call your Yahoo Finance tool before writing." Added "Your first action should always be a tool call." Added copyright/legal ticker mapping.

6. **`historian.md`**: Added explicit citation instruction: "You MUST cite at least one specific detail from your search results" with Volcker example.

7. **`philosopher.md`**: Replaced generic examples with philosophy-grounded ones citing Rawls, Foucault, and Kant by name.

### Production Code Change

8. **`nodes.py`**: Added `result_snippet` (truncated to 500 chars) to the search_queries dict in `_invoke_with_tools`. This captures actual tool output for the tool grounding test. Backwards-compatible — `SearchQuery` Pydantic model ignores extra fields.

## Backwards Compatibility

No impact. Prompt changes affect future output only. The `result_snippet` field is ignored by the API schema and stored alongside existing search metadata in the DB JSON column.
