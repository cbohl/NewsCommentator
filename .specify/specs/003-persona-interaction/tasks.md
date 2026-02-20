# Tasks: Persona Interaction & Randomized Order

**Input**: `specs/003-persona-interaction/plan.md`
**Depends on**: 002-prompt-refinement must be complete first

## Phase 1: Constitution Amendment

- [ ] T001 Amend Data Flow Contract in `.specify/memory/constitution.md` — replace fixed order with randomized order, bump to version 1.2.0

## Phase 2: State & Graph Changes

- [ ] T002 Update `backend/app/graph/state.py` — add `execution_order: list[str]` to `CommentaryState`
- [ ] T003 Update `backend/app/graph/nodes.py` — modify each node function to check state for prior non-empty comments, include them in prompt with "you may respond to your colleagues" instruction
- [ ] T004 Rewrite `backend/app/graph/workflow.py` — replace static compiled graph with `build_commentary_graph(order: list[str])` function that builds and compiles a graph in the given order

## Phase 3: Pipeline Integration

- [ ] T005 Update `backend/app/services/pipeline.py` — shuffle persona order per article, call `build_commentary_graph(order)`, set `execution_order` in initial state, log the order

## Phase 4: Validation

- [ ] T006 Trigger pipeline on 3 articles, verify at least 2 different execution orders and that later personas reference earlier comments
