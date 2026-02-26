# Implementation Plan: Agent Tool Use (Tavily Web Search)

**Branch**: `give-agents-tools` | **Date**: 2026-02-25 | **Spec**: `specs/009-tool-use/spec.md`

## Summary

Add Tavily web search as an optional LangChain tool available to each persona node in the hourly pipeline. The LLM autonomously decides whether to search, processes results, and writes grounded commentary. Tool use is pipeline-only — the chat endpoint remains unchanged.

## Technical Context

**Languages**: Python 3.12+
**New dependencies**: `tavily-python` (provides `TavilySearchResults` tool for LangChain)
**New env var**: `TAVILY_API_KEY`

**Files to modify**:
- `backend/app/graph/nodes.py` — Add tool binding, tool-calling loop, search instructions to prompts
- `backend/app/graph/state.py` — No changes needed (state shape unchanged — tools are internal to nodes)
- `backend/app/graph/workflow.py` — No changes needed (node signatures unchanged)
- `backend/app/services/pipeline.py` — No changes needed (graph invocation unchanged)
- `backend/requirements.txt` — Add `tavily-python`
- `backend/.env.example` — Add `TAVILY_API_KEY` placeholder
- `.specify/memory/constitution.md` — Amendment 1.5.0

**Files NOT modified**:
- `backend/app/routers/chat.py` — Chat remains tool-free
- All frontend files — No UI changes

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | Tool use happens within existing graph nodes; node signatures unchanged |
| II. Expert Persona Integrity | PASS | Same personas, same prompts; search is additive context only |
| III. Anti-AI-ism Voice | PASS | Prompt explicitly forbids search-summary style writing |
| IV. Idempotent Processing | N/A | No schema changes |
| V. Resilience | PASS | Tool failures fall back gracefully to tool-free generation |
| VI. Jina Reader | N/A | Tavily supplements article text, does not replace extraction |
| VII. Simplicity | PASS | One new dependency, changes confined to one file |
| Technology Stack | AMENDMENT 1.5.0 | Add Tavily as web search provider |

## Design

### Tool Setup

Create the Tavily tool once at module level in `nodes.py`, guarded by the presence of `TAVILY_API_KEY`:

```python
import os
from langchain_community.tools.tavily_search import TavilySearchResults

_tavily_tool = None

def _get_search_tool():
    global _tavily_tool
    if _tavily_tool is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return None
        _tavily_tool = TavilySearchResults(max_results=3)
    return _tavily_tool
```

If `TAVILY_API_KEY` is absent, `_get_search_tool()` returns `None` and all nodes operate exactly as they do today.

### Tool Binding

When the search tool is available, bind it to the LLM for pipeline calls:

```python
def _get_pipeline_llm():
    """LLM with tools bound for the hourly pipeline."""
    llm = _get_llm()
    tool = _get_search_tool()
    if tool:
        return llm.bind_tools([tool])
    return llm
```

The chat endpoint continues using `_get_llm()` directly (no tools bound).

### Tool-Calling Loop

Each persona node function needs to handle the iterative tool-calling loop. When the LLM responds with tool calls instead of text content, the node:

1. Executes the tool call(s)
2. Appends the tool results as `ToolMessage`s
3. Re-invokes the LLM with the updated message list
4. Repeats until the LLM produces a text response (or max 2 tool calls reached)

```python
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

def _invoke_with_tools(messages: list, max_tool_calls: int = 2) -> str:
    """Invoke LLM with optional tool-calling loop. Returns final text content."""
    llm = _get_pipeline_llm()
    tool = _get_search_tool()
    tool_calls_made = 0

    while True:
        response = llm.invoke(messages)

        # If no tool calls or no tool available, return the text
        if not response.tool_calls or not tool:
            return response.content

        # Enforce max tool calls
        messages.append(response)
        for tc in response.tool_calls:
            if tool_calls_made >= max_tool_calls:
                # Tell the LLM it's hit the limit
                messages.append(ToolMessage(
                    content="Tool call limit reached. Write your response now.",
                    tool_call_id=tc["id"],
                ))
                continue
            try:
                result = tool.invoke(tc["args"])
                messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tc["id"],
                ))
            except Exception as e:
                # Tavily failure — graceful degradation
                logger.warning("Tavily search failed: %s", e)
                messages.append(ToolMessage(
                    content="Search unavailable. Write your response based on the article alone.",
                    tool_call_id=tc["id"],
                ))
            tool_calls_made += 1

    return response.content
```

### Prompt Changes

Add a search instruction to `SYSTEM_RULES` (appended, does not replace existing rules):

```python
SEARCH_INSTRUCTIONS = (
    "You have access to a web search tool. Use it ONLY when specific facts, "
    "data, or context would genuinely strengthen your argument — for example, "
    "exact statistics, historical dates, or recent developments not in the article. "
    "Most articles will not require a search. When you do use search results, "
    "integrate the facts naturally into your prose. NEVER cite URLs. NEVER say "
    "'According to my search' or 'I found that.' Write as if you already knew the information."
)
```

This instruction is included only for pipeline calls (not chat). It can be appended to the system message conditionally.

### Node Function Changes

Each persona node function changes from:

```python
def historian_node(state: CommentaryState) -> dict:
    response = _get_llm().invoke([...])
    return {"historian_comment": response.content}
```

To:

```python
def historian_node(state: CommentaryState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + HISTORIAN_PROMPT),
        HumanMessage(content=_build_user_message(state, "historian") + _make_length_reminder()),
    ]
    content = _invoke_with_tools(messages)
    return {"historian_comment": content}
```

The node signature and return shape are identical — `workflow.py` and `pipeline.py` require zero changes.

### Chat Endpoint — No Changes

`routers/chat.py` already uses its own LLM instantiation with `ChatOpenAI.astream()`. It does not use `_get_pipeline_llm()` and does not bind tools. No changes needed.

### Environment Variable

Add `TAVILY_API_KEY` to `.env.example`:

```
TAVILY_API_KEY=tvly-...
```

If the key is absent, the pipeline operates identically to today (tool-free). A warning is logged at startup.

### Startup Warning

In `nodes.py`, log a warning at import time if the key is missing:

```python
import logging
logger = logging.getLogger(__name__)

if not os.environ.get("TAVILY_API_KEY"):
    logger.warning("TAVILY_API_KEY not set — personas will operate without web search")
```

### Constitution Update

1. Add Tavily to the Technology Stack table as "Web Search: Tavily".
2. Add amendment 1.5.0 to the log.
3. Bump version to 1.5.0.

## Cost & Latency Impact

- **Tavily API**: ~$0.01 per search call. Max 6 searches per pipeline run (2 per persona x 3 personas). Worst case: $0.06/article.
- **Latency**: Each Tavily call adds ~1-3 seconds. With max 2 calls per persona, worst case adds ~6 seconds to a persona's node execution. Since nodes execute sequentially, worst case total pipeline addition is ~18 seconds (unlikely — most personas won't search).
- **LLM tokens**: Tool call messages add ~200-500 tokens per search round-trip. Minimal cost impact given GPT-5.2 pricing.

## Dependency

`tavily-python` — Official Tavily Python SDK, used by LangChain's `TavilySearchResults` tool.

```
pip install tavily-python
```

Also available via `langchain-community`, but `tavily-python` is the lighter, more direct dependency. LangChain's `TavilySearchResults` imports from `tavily-python` under the hood.
