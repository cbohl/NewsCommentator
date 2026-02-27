# Tasks: Persona-Specific Research Tools

**Input**: `specs/011-persona-tools/plan.md`

## Phase 1: Constitution & Dependencies

- [x] T001 Amend constitution to version 1.6.0 — expand "Web Search: Tavily" to "Research Tools: Tavily, Wikipedia, Yahoo Finance" in Technology Stack, add amendment log entry
- [x] T002 Add `langchain-community`, `wikipedia`, `yfinance` to `backend/requirements.txt` and install

## Phase 2: Per-Persona Tool Registry

- [x] T003 Create `_get_wikipedia_tool()` in `backend/app/graph/nodes.py` — returns `WikipediaQueryRun` with `top_k_results=2, doc_content_chars_max=2000`
- [x] T004 Create `_get_yahoo_finance_tool()` in `backend/app/graph/nodes.py` — returns `YahooFinanceNewsTool`
- [x] T005 Create `TOOL_SOURCE_LABELS` dict mapping tool names to display labels: `"tavily_search"` → `"Web"`, `"wikipedia"` → `"Wikipedia"`, `"yahoo_finance_news"` → `"Yahoo Finance"`
- [x] T006 Create `_get_persona_tools(persona)` in `backend/app/graph/nodes.py` — returns tool list: historian gets `[Tavily, Wikipedia]`, economist gets `[Tavily, YahooFinance]`, philosopher gets `[Tavily]`
- [x] T007 Update `_get_pipeline_llm(temperature, persona)` to bind persona-specific tools via `_get_persona_tools(persona)`

## Phase 3: Multi-Tool Dispatch

- [x] T008 Update `_invoke_with_tools` to accept `persona` parameter and build `tools_by_name` dict from persona tools
- [x] T009 Update `_invoke_with_tools` to dispatch tool calls by `tc["name"]` using `tools_by_name` dict instead of single `tool` variable
- [x] T010 Change `search_queries` accumulator from `list[str]` to `list[dict]` with `{"query": str, "source": str}`, using `TOOL_SOURCE_LABELS` for source
- [x] T011 Change `_invoke_with_tools` return type from `tuple[str, list[str]]` to `tuple[str, list[dict]]`

## Phase 4: Node & State Updates

- [x] T012 Update `CommentaryState` search fields from `list[str]` to `list[dict]` in `backend/app/graph/state.py`
- [x] T013 Update `historian_node` to pass `persona="historian"` and `max_tool_calls=3` to `_invoke_with_tools`
- [x] T014 Update `economist_node` to pass `persona="economist"` and `max_tool_calls=3` to `_invoke_with_tools`
- [x] T015 Update `philosopher_node` to pass `persona="philosopher"` to `_invoke_with_tools` (keep `max_tool_calls=2`)

## Phase 5: Prompt Updates

- [x] T016 Update `backend/app/graph/prompts/search_instructions.md` — generalize "web search tool" to "search tools" with per-tool guidance
- [x] T017 Add Wikipedia research tool guidance to `backend/app/graph/prompts/historian.md`
- [x] T018 Add Yahoo Finance research tool guidance to `backend/app/graph/prompts/economist.md`

## Phase 6: API Schema

- [x] T019 Add `SearchQuery` Pydantic model (`query: str`, `source: str`) to `backend/app/schemas.py`
- [x] T020 Change `CommentOut.search_queries` from `list[str]` to `list[SearchQuery]`
- [x] T021 Update `field_validator` for backwards compatibility: `list[str]` → `[{"query": s, "source": "Web"}]`

## Phase 7: Frontend

- [x] T022 Add `SearchQuery` interface (`query: string`, `source: string`) to `frontend/src/api/client.ts`
- [x] T023 Update `Comment` interface to use `search_queries: SearchQuery[]`
- [x] T024 Update `CommentBlock.tsx` mobile footnote to show source labels: `"query" (Source)`
- [x] T025 Update `CommentBlock.tsx` desktop footnote to show source labels: `"query" (Source)`

## Phase 8: RSS Feed Diversification

- [x] T026 Update `backend/app/services/rss.py` to pull from BBC World + BBC Business feeds
- [x] T027 Shuffle combined feed entries randomly before selecting `limit` articles
- [x] T028 Filter out non-article URLs (podcasts, audio, video)

## Phase 9: Validate

- [x] T029 Test: drop DB, restart server, trigger pipeline — verify historian footnotes show "(Wikipedia)" or "(Web)"
- [x] T030 Test: verify economist footnotes show "(Yahoo Finance)" or "(Web)"
- [x] T031 Test: verify philosopher footnotes show "(Web)" only
- [ ] T032 Test: verify old `list[str]` data in DB renders with "(Web)" labels (backwards compat)
- [x] T033 Test: verify chat is completely unchanged
- [ ] T034 Test: verify pipeline works with `TAVILY_API_KEY` unset — historian/economist still have Wikipedia/Yahoo Finance
