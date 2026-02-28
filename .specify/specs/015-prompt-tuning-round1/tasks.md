# Tasks: Prompt Tuning Round 1 — Voice & Tool Usage

**Input**: `specs/015-prompt-tuning-round1/plan.md`

## Phase 1: Round 1 Prompt Changes

- [x] T001 Add Analytical Toolkit to `philosopher.md` (Kant, Rawls, Foucault, utilitarianism, etc.)
- [x] T002 Add Research Tools section to `philosopher.md` with "search on EVERY article" instruction
- [x] T003 Add off-topic resilience to `historian.md` (tech → printing press, legal → landmark rulings)
- [x] T004 Strengthen tool usage in `historian.md` ("search it on EVERY article")
- [x] T005 Strengthen tool usage in `economist.md` ("search it on EVERY article" + ticker mappings)
- [x] T006 Rewrite `search_instructions.md` — "SHOULD" → "USE IT on every article", add grounding mandate

## Phase 2: Test Round 1

- [x] T007 Run full test suite — 48 passed, 6 failed (up from 42-44 baseline)
- [x] T008 Philosopher voice improved: 0/3 → 1/3
- [x] T009 Historian + philosopher tool usage: now passing

## Phase 3: Round 2 Prompt Changes

- [x] T010 Escalate `economist.md` to "MANDATORY" with "first action should always be a tool call"
- [x] T011 Add explicit citation instruction to `historian.md` ("MUST cite at least one specific detail")
- [x] T012 Replace `philosopher.md` examples with philosophy-grounded versions (Rawls, Foucault, Kant)

## Phase 4: Test Round 2

- [x] T013 Run full test suite — 48 passed, 6 failed
- [x] T014 Philosopher voice: 1/3 → 3/3 (fully fixed)
- [x] T015 Economist tool usage still 0/3 — identified as model behavior issue, not prompt issue
- [x] T016 Historian grounding still 0/3 — identified as Wikipedia relevance issue (generic results)

## Phase 5: Production Code

- [x] T017 Add `result_snippet` to search_queries dict in `_invoke_with_tools` (nodes.py)

## Phase Dependencies

- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 2 (informed by results)
- Phase 4 depends on Phase 3
- Phase 5 is independent (done alongside Phase 1)
