# Implementation Plan: Prompt Refinement

**Branch**: `002-prompt-refinement` | **Date**: 2026-02-20 | **Spec**: `specs/002-prompt-refinement/spec.md`

## Summary

Rewrite the three persona prompts and global system rules in `backend/app/graph/nodes.py` to produce natural, varied, prose-style commentary instead of formulaic AI-structured output.

## Technical Context

**Files affected**: 1 file — `backend/app/graph/nodes.py`
**Risk**: Low — prompt-only changes, no structural or API changes.

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| II. Expert Persona Integrity | PASS | Analytical lenses preserved; delivery style refined |
| III. Anti-AI-ism Voice | PASS | Strengthened — adding anti-formatting rules |

## Changes

### 1. SYSTEM_RULES — Add anti-formatting rules

Current rules prohibit certain phrases. Add:
- Write in natural flowing prose only. No colons as separators, no bullet points, no numbered lists.
- Vary your opening and rhetorical structure. Never start two responses the same way.

### 2. HISTORIAN_PROMPT — Loosen framework references

Current: "Focus on historical precedents, 50-100 year cycles, and the tension between 'Great Man' theory and 'Social Forces' theory."

Change to: Present the frameworks as a toolkit the historian *may* draw from when relevant, not a checklist to cite every time. Emphasize finding the most illuminating historical parallel for this specific story.

### 3. ECONOMIST_PROMPT — Broaden economic lens

Current: "Focus on incentives, resource scarcity, market impacts, and game theory."

Change to: List the full range of economic thinking (incentives, scarcity, game theory, externalities, moral hazard, comparative advantage, opportunity cost, market structure) and instruct the model to pick whichever lens best illuminates this particular story.

### 4. PHILOSOPHER_PROMPT — Strengthen natural voice

Current prompt is the least formulaic. Refine to emphasize conversational Socratic questioning over structured analysis.
