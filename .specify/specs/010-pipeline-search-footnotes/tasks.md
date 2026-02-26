# Tasks: Pipeline Search Footnotes

**Input**: `specs/010-pipeline-search-footnotes/plan.md`

## Phase 1: Backend — `_invoke_with_tools` return type

- [ ] T001 Add `search_queries: list[str]` accumulator to `_invoke_with_tools` in `backend/app/graph/nodes.py`
- [ ] T002 Append `str(query)` to `search_queries` on each tool call (including failed ones)
- [ ] T003 Change return from `response.content` to `(response.content, search_queries)`
- [ ] T004 Update `historian_node` to unpack tuple and return `historian_searches` in state
- [ ] T005 Update `economist_node` to unpack tuple and return `economist_searches` in state
- [ ] T006 Update `philosopher_node` to unpack tuple and return `philosopher_searches` in state

## Phase 2: Graph State

- [ ] T007 Add `historian_searches`, `economist_searches`, `philosopher_searches` fields to `CommentaryState` in `backend/app/graph/state.py`

## Phase 3: Database & Pipeline

- [ ] T008 Add nullable `search_queries` Text column to `Comment` model in `backend/app/models.py`
- [ ] T009 Update pipeline in `backend/app/services/pipeline.py` to pass `search_queries=json.dumps(searches)` when creating `Comment` rows
- [ ] T010 Update initial graph state in pipeline to include empty `*_searches` lists

## Phase 4: API Schema

- [ ] T011 Add `search_queries: list[str]` field to `CommentOut` in `backend/app/schemas.py`
- [ ] T012 Add `field_validator` to parse JSON string or null into `list[str]`

## Phase 5: Frontend

- [ ] T013 Add `search_queries: string[]` to `Comment` interface in `frontend/src/api/client.ts`
- [ ] T014 Render footnote in `CommentBlock.tsx` mobile layout when `search_queries` is non-empty
- [ ] T015 Render footnote in `CommentBlock.tsx` desktop layout when `search_queries` is non-empty

## Phase 6: Validate

- [ ] T016 Test: drop DB, restart server, trigger pipeline — verify comments with searches have footnotes
- [ ] T017 Test: verify comments without searches have no footnotes
- [ ] T018 Test: verify chat is completely unchanged (no tools, no footnotes)
- [ ] T019 Test: verify pipeline works with `TAVILY_API_KEY` unset (no searches, no footnotes, no errors)

## Phase Dependencies

- Phase 1 and Phase 2 can run in parallel
- Phase 3 depends on Phase 1 (need tuple return) and Phase 2 (need state fields)
- Phase 4 depends on Phase 3 (need DB column)
- Phase 5 depends on Phase 4 (need API field)
- T004, T005, T006 are independent [P]
- T014, T015 are independent [P]
- T016–T019 are independent validation tasks [P]
