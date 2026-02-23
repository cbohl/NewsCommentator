# Implementation Plan: Persona Identity Overhaul

**Branch**: `005-persona-identity` | **Date**: 2026-02-23 | **Spec**: `specs/005-persona-identity/spec.md`

## Summary

Replace generic Historian/Economist/Philosopher prompts with fully realized characters — Dr. Margaret "Maggie" Chandrasekaran, Dr. Timothy "Tim" Brennan, and Sofia Reyes — each with distinct personalities, credentials, few-shot examples, and varied interaction/length behavior.

## Technical Context

**Files affected**:
- `.specify/memory/constitution.md` — Amend Article II, bump version
- `backend/app/graph/nodes.py` — Rewrite all prompts
- `frontend/src/components/CommentBlock.tsx` — Update persona labels

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| II. Expert Persona Integrity | AMENDMENT | Generic personas → named characters |
| III. Anti-AI-ism Voice | PASS | Strengthened by few-shot examples and personality |

## Design

### Prompt Structure (per persona)

Each persona prompt will include:
1. **Identity block** — Name, degree, university, role
2. **Personality** — Worldview, temperament, how they argue
3. **Few-shot examples** (2-3) — Actual example responses showing the voice
4. **Interaction rule** — "About 40% of the time, respond directly to a colleague by name. Otherwise give your independent take."
5. **Length rule** — "Vary your length naturally. Sometimes one sharp sentence is enough. Sometimes you need the full 150 words. Match the weight of the story."

### System Rules Update

Add to SYSTEM_RULES:
- Varied length instruction
- 40% interaction rate guidance

### Frontend Labels

Update `PERSONA_STYLES` in CommentBlock.tsx:
- `historian` → "Dr. Maggie Chandrasekaran — Historian"
- `economist` → "Dr. Tim Brennan — Economist"
- `philosopher` → "Sofia Reyes — Philosopher"
