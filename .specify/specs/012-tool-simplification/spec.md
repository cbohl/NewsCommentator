# Feature Specification: Tool Simplification — One Specialized Tool Per Persona

**Feature Branch**: `give-additional-tools-to-agents`
**Created**: 2026-02-27
**Status**: Draft
**Input**: User request: "Limit each persona to one specialized tool — historian gets Wikipedia only, economist gets Yahoo Finance only, philosopher gets Tavily only. Web search is not productive enough to justify giving it to everyone."

## Constitution Amendment Required

One amendment to the constitution:

- **1.6.1**: Simplified tool assignments to one specialized tool per persona. Historian gets Wikipedia only, Economist gets Yahoo Finance only, Philosopher gets Tavily only. Removed shared Tavily access from historian and economist. Rationale: personas defaulted to Tavily instead of using specialized tools; one-tool-per-persona forces distinctive, expertise-aligned research.

## Rationale

Tavily web search returns broad but shallow results. In practice, personas default to web search even when specialized tools would produce better commentary. By removing web search from historian and economist, each persona is forced to use the tool best suited to their expertise.

## Requirements

```json
[
  {
    "name": "Restrict Historian to Wikipedia",
    "description": "System must limit the historian persona to Wikipedia as her only research tool, and it should bind only WikipediaQueryRun when building the historian's LLM tool list, so that Maggie is forced to research historical context rather than defaulting to generic web search",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [93, 94, 95],
    "acceptance_criteria": [
      "Given the historian persona is processing an article, When tools are bound to the LLM, Then only the Wikipedia tool is available",
      "Given the historian persona decides to search, When she invokes a tool, Then the tool name is 'wikipedia' and the footnote source label is 'Wikipedia'",
      "Given Tavily API key is set, When the historian's tools are built, Then Tavily is NOT included in her tool list"
    ]
  },
  {
    "name": "Restrict Economist to Yahoo Finance",
    "description": "System must limit the economist persona to Yahoo Finance as his only research tool, and it should bind only YahooFinanceNewsTool when building the economist's LLM tool list, so that Tim is forced to ground his analysis in financial data rather than defaulting to generic web search",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [96, 97, 98],
    "acceptance_criteria": [
      "Given the economist persona is processing an article, When tools are bound to the LLM, Then only the Yahoo Finance tool is available",
      "Given the economist persona decides to search, When he invokes a tool, Then the tool name is 'yahoo_finance_news' and the footnote source label is 'Yahoo Finance'",
      "Given Tavily API key is set, When the economist's tools are built, Then Tavily is NOT included in his tool list"
    ]
  },
  {
    "name": "Restrict Philosopher to Tavily",
    "description": "System must limit the philosopher persona to Tavily web search as her only research tool, and it should bind only TavilySearch when building the philosopher's LLM tool list, so that Sofia uses broad web search aligned with her generalist philosophical perspective",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [99, 100],
    "acceptance_criteria": [
      "Given the philosopher persona is processing an article, When tools are bound to the LLM, Then only the Tavily tool is available",
      "Given the philosopher persona decides to search, When she invokes a tool, Then the tool name is 'tavily_search' and the footnote source label is 'Web'",
      "Given Tavily API key is unset, When the philosopher's tools are built, Then the tool list is empty and she operates without search"
    ]
  },
  {
    "name": "Reduce Max Tool Calls for Single-Tool Personas",
    "description": "System must set max_tool_calls to 2 for all personas since each now has only one tool type, and it should enforce the limit in the _invoke_with_tools loop, so that cost and latency are controlled",
    "type": "control_flow",
    "confidence": 0.9,
    "source_lines": [107],
    "acceptance_criteria": [
      "Given any persona is processing an article, When the LLM makes tool calls, Then at most 2 tool calls are executed before forcing a final text response"
    ]
  },
  {
    "name": "Historian Operates Without Tavily Key",
    "description": "System must allow the historian to function with Wikipedia even when TAVILY_API_KEY is unset, and it should build the historian's tool list independently of Tavily availability, so that Maggie always has research capability",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [93, 94],
    "acceptance_criteria": [
      "Given TAVILY_API_KEY is not set, When the historian's tools are built, Then Wikipedia is still available",
      "Given TAVILY_API_KEY is not set, When the philosopher's tools are built, Then the tool list is empty"
    ]
  },
  {
    "name": "Chat Endpoint Unchanged",
    "description": "System must not bind any tools to the chat endpoint LLM, and it should continue using _get_llm() directly without tool binding, so that chat latency is unaffected",
    "type": "control_flow",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a user sends a chat message, When the backend processes it, Then no tools are bound and no search occurs"
    ]
  }
]
```

## Files to Modify

- `backend/app/graph/nodes.py` — Update `_get_persona_tools()` to remove Tavily from historian/economist
- `backend/app/graph/prompts/historian.md` — Remove any "use web search for..." fallback guidance
- `backend/app/graph/prompts/economist.md` — Remove any "use web search for..." fallback guidance

## Files NOT Modified

- `backend/app/routers/chat.py` — Chat unchanged
- `backend/app/schemas.py` — Schema unchanged
- `frontend/` — Frontend unchanged
- `backend/app/services/pipeline.py` — Pipeline unchanged
