# Tasks: Prompt Refinement

**Input**: `specs/002-prompt-refinement/plan.md`

## Phase 1: Prompt Rewrite

- [ ] T001 Rewrite SYSTEM_RULES in `backend/app/graph/nodes.py` — add anti-formatting rules (no colons as separators, no bullets, no lists, vary openings)
- [ ] T002 Rewrite HISTORIAN_PROMPT — frameworks as optional toolkit, emphasis on finding the best historical parallel
- [ ] T003 Rewrite ECONOMIST_PROMPT — broaden lens options, pick most relevant per article
- [ ] T004 Rewrite PHILOSOPHER_PROMPT — more conversational Socratic voice

## Phase 2: Validation

- [ ] T005 Trigger pipeline on 3 articles, review output against acceptance criteria (SC-001 through SC-005)
