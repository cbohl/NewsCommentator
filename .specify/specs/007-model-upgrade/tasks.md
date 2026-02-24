# Tasks: Model Upgrade & Response Length Tuning

**Input**: `specs/007-model-upgrade/plan.md`

## Phase 1: Backend Changes

- [x] T001 Change model from `gpt-5-nano` to `gpt-5.2` in `_get_llm()` in `backend/app/graph/nodes.py`
- [x] T002 Rewrite SYSTEM_RULES with explicit SHORT/MEDIUM/LONG length tiers and percentage targets in `backend/app/graph/nodes.py`

## Phase 2: Constitution Amendments

- [x] T003 Amend Article III in `.specify/memory/constitution.md` — add 30-100 word target range language
- [x] T004 Update Technology Stack table — GPT-5-nano → GPT-5.2 in `.specify/memory/constitution.md`
- [x] T005 Add amendment log entries for 1.3.1 and 1.3.2, bump version to 1.3.2 in `.specify/memory/constitution.md`

## Phase 3: Deploy & Validate

- [x] T006 Deploy and process 5 articles to validate length variation matches tier distribution and persona voices are more distinct with GPT-5.2
