# Tasks: Persona-Specific Research Tools

**Input**: `specs/011-persona-tools/plan.md`

## Phase 1: Constitution & Dependencies

- [ ] T001 Amend constitution to version 1.6.0 — expand "Web Search: Tavily" to "Research Tools: Tavily, Wikipedia, Arxiv" in Technology Stack, add amendment log entry
- [ ] T002 Add `langchain-community`, `wikipedia`, `arxiv` to `backend/requirements.txt` and install

## Phase 2: Per-Persona Tool Registry

- [ ] T003 Create `_get_wikipedia_tool()` in `backend/app/graph/nodes.py` — returns `WikipediaQueryRun` with `top_k_results=2, doc_content_chars_max=2000`
- [ ] T004 Create `_get_arxiv_tool()` in `backend/app/graph/nodes.py` — returns `ArxivQueryRun` with `top_k_results=2, doc_content_chars_max=2000`
- [ ] T005 Create `TOOL_SOURCE_LABELS` dict mapping tool names to display labels: `"tavily_search"` → `"Web"`, `"wikipedia"` → `"Wikipedia"`, `"arxiv"` → `"Arxiv"`
- [ ] T006 Create `_get_persona_tools(persona)` in `backend/app/graph/nodes.py` — returns tool list: historian gets `[Tavily, Wikipedia]`, economist gets `[Tavily, Arxiv]`, philosopher gets `[Tavily]`
- [ ] T007 Update `_get_pipeline_llm(temperature, persona)` to bind persona-specific tools via `_get_persona_tools(persona)`

## Phase 3: Multi-Tool Dispatch

- [ ] T008 Update `_invoke_with_tools` to accept `persona` parameter and build `tools_by_name` dict from persona tools
- [ ] T009 Update `_invoke_with_tools` to dispatch tool calls by `tc["name"]` using `tools_by_name` dict instead of single `tool` variable
- [ ] T010 Change `search_queries` accumulator from `list[str]` to `list[dict]` with `{"query": str, "source": str}`, using `TOOL_SOURCE_LABELS` for source
- [ ] T011 Change `_invoke_with_tools` return type from `tuple[str, list[str]]` to `tuple[str, list[dict]]`

## Phase 4: Node & State Updates

- [ ] T012 Update `CommentaryState` search fields from `list[str]` to `list[dict]` in `backend/app/graph/state.py`
- [ ] T013 Update `historian_node` to pass `persona="historian"` and `max_tool_calls=3` to `_invoke_with_tools`
- [ ] T014 Update `economist_node` to pass `persona="economist"` and `max_tool_calls=3` to `_invoke_with_tools`
- [ ] T015 Update `philosopher_node` to pass `persona="philosopher"` to `_invoke_with_tools` (keep `max_tool_calls=2`)

## Phase 5: Prompt Update

- [ ] T016 Update `backend/app/graph/prompts/search_instructions.md` — generalize "web search tool" to "search tools" to cover Wikipedia and Arxiv

## Phase 6: API Schema

- [ ] T017 Add `SearchQuery` Pydantic model (`query: str`, `source: str`) to `backend/app/schemas.py`
- [ ] T018 Change `CommentOut.search_queries` from `list[str]` to `list[SearchQuery]`
- [ ] T019 Update `field_validator` for backwards compatibility: `list[str]` → `[{"query": s, "source": "Web"}]`

## Phase 7: Frontend

- [ ] T020 Add `SearchQuery` interface (`query: string`, `source: string`) to `frontend/src/api/client.ts`
- [ ] T021 Update `Comment` interface to use `search_queries: SearchQuery[]`
- [ ] T022 Update `CommentBlock.tsx` mobile footnote to show source labels: `"query" (Source)`
- [ ] T023 Update `CommentBlock.tsx` desktop footnote to show source labels: `"query" (Source)`

## Phase 8: Validate

- [ ] T024 Test: drop DB, restart server, trigger pipeline — verify historian footnotes show "(Wikipedia)" or "(Web)"
- [ ] T025 Test: verify economist footnotes show "(Arxiv)" or "(Web)"
- [ ] T026 Test: verify philosopher footnotes show "(Web)" only
- [ ] T027 Test: verify old `list[str]` data in DB renders with "(Web)" labels (backwards compat)
- [ ] T028 Test: verify chat is completely unchanged
- [ ] T029 Test: verify pipeline works with `TAVILY_API_KEY` unset — historian/economist still have Wikipedia/Arxiv

## Phase Dependencies

- Phase 1 can run in parallel with all other phases
- Phase 2 depends on Phase 1 T002 (need dependencies installed)
- Phase 3 depends on Phase 2 (need tool registry before dispatch)
- Phase 4 depends on Phase 3 (need updated `_invoke_with_tools` signature)
- Phase 5 can run in parallel with Phases 2-4
- Phase 6 can run in parallel with Phases 2-4 (schema is independent of tool code)
- Phase 7 depends on Phase 6 (need API types defined)
- Phase 8 depends on all prior phases

## Parallel Opportunities

- T003, T004 are independent [P]
- T013, T014, T015 are independent [P]
- T017, T018, T019 can be done together in one edit
- T020, T021 can be done together in one edit
- T022, T023 are independent [P]
- T024–T029 are independent validation tasks [P]
