# Tasks: Agent Tool Use (Tavily Web Search)

**Input**: `specs/009-tool-use/plan.md`

## Phase 1: Constitution

- [ ] T001 Amend constitution to version 1.5.0 — add Tavily as web search provider in Technology Stack table, add amendment log entry with rationale

## Phase 2: Dependencies & Configuration

- [ ] T002 Add `tavily-python` to `backend/requirements.txt` and install
- [ ] T003 Add `TAVILY_API_KEY` placeholder to `backend/.env.example`
- [ ] T004 Add `TAVILY_API_KEY` to production environment (EC2 instance / `.env`)

## Phase 3: Tool Setup

- [ ] T005 Create `_get_search_tool()` in `backend/app/graph/nodes.py` — returns `TavilySearchResults(max_results=3)` if `TAVILY_API_KEY` is set, `None` otherwise
- [ ] T006 Create `_get_pipeline_llm()` in `backend/app/graph/nodes.py` — returns LLM with tools bound via `.bind_tools()` when search tool is available, plain LLM otherwise
- [ ] T007 Add startup warning log in `backend/app/graph/nodes.py` if `TAVILY_API_KEY` is not set

## Phase 4: Tool-Calling Loop

- [ ] T008 Create `_invoke_with_tools()` in `backend/app/graph/nodes.py` — iterative loop that handles LLM tool calls, executes Tavily search, appends `ToolMessage` results, and re-invokes until text response or max 2 tool calls reached
- [ ] T009 Add graceful fallback in `_invoke_with_tools()` — catch Tavily exceptions, return "search unavailable" `ToolMessage`, log warning

## Phase 5: Prompt & Node Updates

- [ ] T010 Add `SEARCH_INSTRUCTIONS` constant to `backend/app/graph/nodes.py` — instructs LLM when to search, how to use results naturally, forbids URL citations and "according to my search" phrasing
- [ ] T011 Update `historian_node()` to use `_invoke_with_tools()` with `SEARCH_INSTRUCTIONS` in system message
- [ ] T012 Update `economist_node()` to use `_invoke_with_tools()` with `SEARCH_INSTRUCTIONS` in system message
- [ ] T013 Update `philosopher_node()` to use `_invoke_with_tools()` with `SEARCH_INSTRUCTIONS` in system message

## Phase 6: Validate

- [ ] T014 Test: process an article with `TAVILY_API_KEY` set — verify at least one persona uses search when article content warrants it
- [ ] T015 Test: process an article and verify commentary reads naturally — no URL citations, no "search result" artifacts
- [ ] T016 Test: unset `TAVILY_API_KEY` and process an article — verify pipeline works identically to pre-tool behavior (graceful fallback)
- [ ] T017 Test: verify chat endpoint (`POST /chat/stream`) does NOT invoke any tools
- [ ] T018 Test: verify max 2 tool calls per persona is enforced

## Phase Dependencies

- Phase 2 blocks Phase 3 (need the dependency installed before importing)
- Phase 3 blocks Phase 4 (tool setup needed before loop can use it)
- Phase 4 blocks Phase 5 (loop function needed before nodes can call it)
- Phase 1 can run in parallel with Phases 2-5

## Parallel Opportunities

- T011, T012, T013 are independent (each persona node is a separate function) but depend on T008 and T010
- T014–T018 are independent validation tasks
