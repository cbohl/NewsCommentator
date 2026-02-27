# Feature Specification: Persona-Specific Research Tools

**Feature Branch**: `give-additional-tools-to-agents`
**Created**: 2026-02-26
**Status**: Implemented
**Input**: User request: "Give each persona specialized research tools aligned with their expertise. The historian gets Wikipedia, the economist gets Yahoo Finance. All tools must be free (no additional API keys beyond Tavily). Footnotes should show which tool was used."

## Constitution Amendment Required

One amendment to the constitution:

- **1.6.0**: Expand the search tool ecosystem from Tavily-only to Tavily + Wikipedia + Yahoo Finance. Historian (Maggie) gains Wikipedia access for historical facts, events, and biographical details. Economist (Tim) gains Yahoo Finance access for financial news and market data by ticker symbol. Philosopher (Sofia) retains Tavily only. All new tools are free and require no API keys. Technology Stack row updated: "Web Search: Tavily" → "Research Tools: Tavily, Wikipedia, Yahoo Finance". No backwards-compatibility impact — existing search data is migrated via a Pydantic validator that converts `list[str]` to `list[dict]` format.

## User Scenarios & Testing

### User Story 1 — Historian Uses Wikipedia (Priority: P1)

When writing pipeline commentary, Maggie can look up historical facts, events, and people on Wikipedia in addition to web search. The footnote shows which tool was used for each query.

**Why this priority**: Wikipedia is the natural research tool for a historian — it provides detailed, well-structured historical context that web search often lacks.

**Acceptance Scenarios**:

1. **Given** an article about a territorial dispute, **When** Maggie writes her comment, **Then** she MAY search Wikipedia for "Durand Line" and the footnote reads: *Researched: "Durand Line" (Wikipedia)*.
2. **Given** Maggie uses both Wikipedia and web search, **When** the article is displayed, **Then** the footnote lists both with sources: *Researched: "Durand Line" (Wikipedia), "Afghanistan Pakistan relations 2025" (Web)*.
3. **Given** Maggie writes without searching, **When** the article is displayed, **Then** no footnote appears.

---

### User Story 2 — Economist Uses Yahoo Finance (Priority: P1)

When writing pipeline commentary, Tim can look up financial news and market data on Yahoo Finance by ticker symbol, in addition to web search. The footnote shows which tool was used.

**Why this priority**: Yahoo Finance provides real-time financial news and market context that strengthens data-driven economic commentary.

**Acceptance Scenarios**:

1. **Given** an article about a tech company, **When** Tim writes his comment, **Then** he MAY search Yahoo Finance for "AAPL" and the footnote reads: *Researched: "AAPL" (Yahoo Finance)*.
2. **Given** Tim uses both Yahoo Finance and web search, **When** the article is displayed, **Then** the footnote lists both with sources: *Researched: "TSLA" (Yahoo Finance), "EV market share 2025" (Web)*.
3. **Given** Tim writes without searching, **When** the article is displayed, **Then** no footnote appears.

---

### User Story 3 — Philosopher Retains Tavily Only (Priority: P1)

Sofia continues to use Tavily web search only. No additional tools are added for her at this time.

**Why this priority**: No suitable free specialized tool exists for philosophy. Tavily web search is sufficient for Sofia's needs.

**Acceptance Scenarios**:

1. **Given** Sofia searches while writing, **When** the article is displayed, **Then** the footnote reads: *Researched: "free will determinism debate" (Web)* — same as current behavior but with the new source label format.
2. **Given** Sofia writes without searching, **When** the article is displayed, **Then** no footnote appears.

---

### User Story 4 — Footnotes Show Source Labels (Priority: P1)

All footnotes now include a parenthetical source label indicating which tool was used for each query. This replaces the plain query-only format from spec 010.

**Why this priority**: With multiple tool types, readers need to know whether a query went to Wikipedia, Yahoo Finance, or the web.

**Acceptance Scenarios**:

1. **Given** a comment with one web search, **When** displayed, **Then** the footnote reads: *Researched: "query" (Web)*.
2. **Given** a comment with mixed sources, **When** displayed, **Then** each query has its own label: *Researched: "query1" (Wikipedia), "query2" (Web)*.
3. **Given** old comments with `list[str]` format in the database, **When** loaded through the API, **Then** the Pydantic validator converts them to `list[dict]` with `"source": "Web"` (backwards-compatible default).

---

### User Story 5 — Chat Remains Unchanged (Priority: P1)

The chat endpoint is completely unaffected. No tools, no search, no footnotes.

**Why this priority**: Chat is a separate feature with different latency requirements.

**Acceptance Scenarios**:

1. **Given** a user sends a chat message, **When** the backend processes it, **Then** no tools are bound and no searches occur.
2. **Given** a chat response is displayed, **Then** no footnote UI appears.

### Edge Cases

- Wikipedia or Yahoo Finance API is unavailable: The query is still recorded (search was attempted), tool failure returns a graceful fallback message. The footnote still shows the query with its source label.
- Old `list[str]` data in database: The Pydantic `field_validator` converts `["query"]` to `[{"query": "query", "source": "Web"}]`. No migration needed.
- `TAVILY_API_KEY` unset: Tavily tool unavailable for all personas. Wikipedia and Yahoo Finance still work (no API key required). Personas with only Tavily (Sofia) operate without tools.
- Persona calls a tool not assigned to them: Not possible — tools are bound per-persona via `_get_persona_tools(persona)`.
- Yahoo Finance returns no data for a ticker: The "No news found" response is passed back to the LLM, which proceeds without financial data. The query is still recorded in the footnote.

## Requirements

### Functional Requirements

- **FR-001**: `_get_persona_tools(persona)` MUST return a list of tools specific to each persona: historian gets `[TavilySearch, WikipediaQueryRun]`, economist gets `[TavilySearch, YahooFinanceNewsTool]`, philosopher gets `[TavilySearch]`.
- **FR-002**: `_get_pipeline_llm(temperature, persona)` MUST bind persona-specific tools to the LLM.
- **FR-003**: `_invoke_with_tools` MUST return `tuple[str, list[dict]]` where each dict is `{"query": str, "source": str}`.
- **FR-004**: Source labels MUST be: `"Web"` for Tavily, `"Wikipedia"` for Wikipedia, `"Yahoo Finance"` for Yahoo Finance.
- **FR-005**: `_invoke_with_tools` MUST dispatch tool calls by `tc["name"]` using a `tools_by_name` dict built from the persona's tool list.
- **FR-006**: `CommentaryState` search fields MUST change from `list[str]` to `list[dict]`.
- **FR-007**: `CommentOut.search_queries` MUST change from `list[str]` to `list[SearchQuery]` where `SearchQuery` has `query: str` and `source: str`.
- **FR-008**: The Pydantic `field_validator` MUST handle backwards compatibility: `null` → `[]`, `list[str]` → `[{"query": s, "source": "Web"}]`, `list[dict]` → passthrough.
- **FR-009**: The frontend `Comment` interface MUST use `SearchQuery` type with `query` and `source` fields.
- **FR-010**: `CommentBlock.tsx` MUST render footnotes as: *Researched: "query" (Source)*.
- **FR-011**: `max_tool_calls` MUST be bumped to 3 for historian and economist (who have 2 tool types available).
- **FR-012**: `search_instructions.md` MUST be generalized from "web search tool" to "search tools" to cover Wikipedia and Yahoo Finance.
- **FR-013**: `backend/requirements.txt` MUST add `langchain-community`, `wikipedia`, and `yfinance` packages.
- **FR-014**: `chat.py` MUST NOT be modified.

### Key Entities

- **`SearchQuery`**: A dict (or Pydantic model) with `query: str` and `source: str`. Source is one of `"Web"`, `"Wikipedia"`, `"Yahoo Finance"`.
- **`_get_persona_tools(persona)`**: Returns the list of LangChain tools available to a specific persona.
- **`tools_by_name`**: A dict mapping tool name strings to tool instances, used for dispatching tool calls in the invoke loop.

## Success Criteria

- **SC-001**: Historian can use both Tavily and Wikipedia; footnotes show "(Wikipedia)" or "(Web)".
- **SC-002**: Economist can use both Tavily and Yahoo Finance; footnotes show "(Yahoo Finance)" or "(Web)".
- **SC-003**: Philosopher uses only Tavily; footnotes show "(Web)".
- **SC-004**: Old comments with `list[str]` format render correctly with "(Web)" labels.
- **SC-005**: Chat is completely unchanged.
- **SC-006**: Pipeline works with `TAVILY_API_KEY` unset (Wikipedia/Yahoo Finance still work for historian/economist).
- **SC-007**: Constitution version is 1.6.0 with amendment logged.
