# Tasks: Tool Simplification — One Specialized Tool Per Persona

**Input**: `specs/012-tool-simplification/plan.md`

## Phase 1: Code Changes

- [x] T001 Rewrite `_get_persona_tools()` in `backend/app/graph/nodes.py` — historian gets `[Wikipedia]` only, economist gets `[YahooFinance]` only, philosopher gets `[Tavily]` only
- [x] T002 Revert `historian_node` max_tool_calls from 3 to default 2
- [x] T003 Revert `economist_node` max_tool_calls from 3 to default 2

## Phase 2: Prompt Updates

- [x] T004 Update `backend/app/graph/prompts/historian.md` — remove "use web search for..." fallback language
- [x] T005 Update `backend/app/graph/prompts/economist.md` — remove "use web search for..." fallback language

## Phase 3: Validate

- [x] T006 Test: verify historian only has Wikipedia tool (no Tavily)
- [x] T007 Test: verify economist only has Yahoo Finance tool (no Tavily)
- [x] T008 Test: verify philosopher only has Tavily tool
- [x] T009 Test: verify historian footnotes show "(Wikipedia)" only, never "(Web)"
- [x] T010 Test: verify economist footnotes show "(Yahoo Finance)" only, never "(Web)"
- [x] T011 Test: verify philosopher footnotes show "(Web)" only (tool binding verified; Sofia didn't search in test run)
- [x] T012 Test: verify chat is unchanged

## Phase Dependencies

- Phase 1 and Phase 2 can run in parallel
- Phase 3 depends on Phases 1 and 2
- T006, T007, T008 are independent [P]
- T009, T010, T011, T012 are independent [P]
