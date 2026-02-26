# Feature Specification: Agent Tool Use (Tavily Web Search)

**Feature Branch**: `give-agents-tools`
**Created**: 2026-02-25
**Status**: Draft
**Input**: User request: "Add LangChain tool use (Tavily web search) to the hourly pipeline so personas can look up real facts before writing commentary. Tools only in the pipeline, not in the live chat."

## Constitution Amendment Required

One amendment to the constitution:

- **1.5.0**: Add Tavily web search as a permitted tool within LangGraph persona nodes. Rationale: enabling personas to ground their commentary in real-world facts produces higher-quality, more credible analysis. Tavily is accessed through LangChain's tool-calling interface, which aligns with the existing LangGraph-first architecture. The tool is used only within the hourly pipeline — chat remains tool-free for latency reasons. Technology Stack table updated to include Tavily as the web search provider. New `TAVILY_API_KEY` environment variable required.

## User Scenarios & Testing

### User Story 1 — Fact-Grounded Commentary (Priority: P1)

Personas can optionally search the web for real facts, data, or historical context before writing their commentary. The LLM decides whether a search is useful based on the article content — not every article warrants a search.

**Why this priority**: The core feature. Without grounded facts, personas sometimes make vague claims or miss relevant context that a quick search would surface.

**Acceptance Scenarios**:

1. **Given** an article about an economic policy, **When** the economist persona processes it, **Then** Tim MAY search for relevant economic data (GDP figures, trade statistics, etc.) and reference it in his commentary.
2. **Given** an article about a well-known historical event, **When** the historian persona processes it, **Then** Maggie MAY search for specific dates, precedents, or parallel events to strengthen her argument.
3. **Given** a straightforward article that needs no external context, **When** any persona processes it, **Then** the persona writes commentary without making any tool calls (search is optional, not mandatory).
4. **Given** a persona makes a search, **When** the search results return, **Then** the persona incorporates relevant facts naturally into their commentary without citing URLs or sounding like a search summary.

---

### User Story 2 — Tool Use Within LangGraph Nodes (Priority: P1)

Each persona node uses LangChain's tool-calling interface to optionally invoke Tavily search. The node handles the full tool-calling loop (LLM decides to search, gets results, writes final response) internally.

**Why this priority**: Architectural foundation. The tool-calling loop must work correctly within the existing LangGraph StateGraph structure.

**Acceptance Scenarios**:

1. **Given** a persona node executes, **When** the LLM decides a search would help, **Then** the node calls Tavily, feeds results back to the LLM, and returns the final commentary.
2. **Given** a persona node executes, **When** the LLM decides no search is needed, **Then** the node produces commentary directly without any tool calls (same behavior as today).
3. **Given** a persona node executes, **When** the LLM makes a tool call, **Then** at most 2 searches are performed per persona per article (cost/latency control).
4. **Given** the tool-calling loop, **When** the LLM's final response is produced, **Then** the returned state update is identical in shape to the current output (`{"persona_comment": response.content}`).

---

### User Story 3 — Tavily Failure Resilience (Priority: P1)

If Tavily is unavailable, slow, or returns an error, the persona falls back to writing commentary without search results. Tool failures never prevent commentary generation.

**Why this priority**: Constitution Principle V (Resilience Over Availability) — failures must never crash the pipeline.

**Acceptance Scenarios**:

1. **Given** Tavily returns an error (rate limit, timeout, API key invalid), **When** the persona node handles the failure, **Then** it falls back to generating commentary without search results.
2. **Given** Tavily is slow (>10 seconds), **When** the timeout is reached, **Then** the node proceeds without search results.
3. **Given** a Tavily failure, **When** the fallback occurs, **Then** a warning is logged but no `ErrorLog` row is created (this is graceful degradation, not a pipeline failure).

---

### User Story 4 — Pipeline-Only Scope (Priority: P1)

Tool use is restricted to the hourly pipeline. The live chat endpoint (`POST /chat/stream`) does NOT use tools.

**Why this priority**: Chat requires low latency for token-by-token streaming. Adding tool calls would introduce unpredictable delays.

**Acceptance Scenarios**:

1. **Given** the chat endpoint processes a user message, **When** building the LLM call, **Then** no tools are bound to the model.
2. **Given** the hourly pipeline processes an article, **When** building persona node LLM calls, **Then** Tavily search is available as a bound tool.

### Edge Cases

- Tavily returns irrelevant results — the persona should ignore unhelpful search results and write based on the article alone. The prompt instructs the LLM to only use search results that genuinely strengthen the argument.
- Tavily returns very long results — search results are truncated to a reasonable size (e.g., `max_results=3`) to avoid blowing up the context window.
- Multiple personas search for similar things — this is acceptable. Each persona operates independently within its own node. No deduplication of searches across personas.
- `TAVILY_API_KEY` is not set — the pipeline falls back to tool-free commentary generation with a startup warning log.
- Article text is very short (< 100 chars) — persona may still choose to search for context, or may not. The LLM decides.

## Requirements

### Functional Requirements

- **FR-001**: Each persona node MUST bind a Tavily web search tool to the LLM via LangChain's `.bind_tools()` interface.
- **FR-002**: The LLM MUST decide autonomously whether to invoke the search tool based on the article content. Search is optional, not mandatory.
- **FR-003**: Each persona MUST be limited to at most 2 tool calls per article to control cost and latency.
- **FR-004**: If Tavily fails or times out (>10s), the node MUST fall back to generating commentary without search results.
- **FR-005**: The chat endpoint (`POST /chat/stream`) MUST NOT bind any tools to the LLM.
- **FR-006**: `langchain-tavily` MUST be added to `backend/requirements.txt`.
- **FR-007**: `TAVILY_API_KEY` MUST be read from the environment. If absent, the pipeline MUST operate without tools and log a warning at startup.
- **FR-008**: The system prompt MUST instruct the LLM to use search results naturally — no URL citations, no "According to my search" phrasing, no search-summary style.
- **FR-009**: Tavily search results MUST be limited to `max_results=3` per search call.
- **FR-010**: Constitution MUST be amended to version 1.5.0 with Tavily added to the Technology Stack.

### Key Entities

- **TavilySearch**: LangChain tool wrapper for the Tavily search API (from `langchain-tavily`). Configured with `max_results=3`.
- **Tool-calling loop**: An iterative loop within each persona node where the LLM can call tools, receive results, and then produce a final text response.

## Success Criteria

- **SC-001**: Persona nodes can optionally search the web and incorporate facts into commentary.
- **SC-002**: Commentary that uses search results reads naturally — no "search result" artifacts.
- **SC-003**: Personas that don't need to search produce commentary identically to today's behavior.
- **SC-004**: Tavily failures never prevent commentary generation.
- **SC-005**: Chat endpoint remains tool-free with no latency impact.
- **SC-006**: At most 2 search calls per persona per article (6 total max per pipeline run of 1 article).
- **SC-007**: Constitution version is 1.5.0 with amendment logged.
