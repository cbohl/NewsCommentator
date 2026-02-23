# Tasks: Persona Identity Overhaul

**Input**: `specs/005-persona-identity/plan.md`

## Phase 1: Constitution Amendment

- [ ] T001 Amend Article II in `.specify/memory/constitution.md` — replace generic personas with Maggie, Tim, Sofia definitions. Bump to version 1.3.0.

## Phase 2: Prompt Rewrite

- [ ] T002 Rewrite SYSTEM_RULES in `backend/app/graph/nodes.py` — add varied length instruction and 40% interaction rate guidance
- [ ] T003 Rewrite HISTORIAN_PROMPT — full Maggie identity, personality, 2-3 few-shot examples
- [ ] T004 Rewrite ECONOMIST_PROMPT — full Tim identity, personality, 2-3 few-shot examples
- [ ] T005 Rewrite PHILOSOPHER_PROMPT — full Sofia identity, personality, 2-3 few-shot examples

## Phase 3: Frontend

- [ ] T006 Update `frontend/src/components/CommentBlock.tsx` — persona labels show character names

## Phase 4: Deploy & Validate

- [ ] T007 Deploy to EC2 + S3 and trigger pipeline on 3 articles to validate distinct voices, varied lengths, and ~40% interaction rate
