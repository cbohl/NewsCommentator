# Implementation Plan: Persona-Specific Research Tools

**Branch**: `add-footnotes` | **Date**: 2026-02-26 | **Spec**: `specs/011-persona-tools/spec.md`

## Summary

Replace the single shared Tavily search tool with per-persona tool sets: historian gets Tavily + Wikipedia, economist gets Tavily + Arxiv, philosopher keeps Tavily only. Update the search metadata format from `list[str]` to `list[dict]` so footnotes show which tool was used for each query. Backwards-compatible with existing data.

## Technical Context

**Languages**: Python 3.12+, TypeScript
**New dependencies**: `langchain-community` (provides `WikipediaQueryRun`, `ArxivQueryRun`), `wikipedia` (underlying Wikipedia API lib), `arxiv` (underlying Arxiv API lib)
**New env vars**: None (Wikipedia and Arxiv APIs are free and keyless)

**Files to modify**:
- `backend/requirements.txt` — Add `langchain-community`, `wikipedia`, `arxiv`
- `backend/app/graph/nodes.py` — Per-persona tool registry, multi-tool dispatch, source tracking
- `backend/app/graph/state.py` — `list[str]` → `list[dict]` for search fields
- `backend/app/graph/prompts/search_instructions.md` — Generalize to cover multiple tool types
- `backend/app/schemas.py` — New `SearchQuery` model, backwards-compat validator
- `frontend/src/api/client.ts` — New `SearchQuery` interface, update `Comment`
- `frontend/src/components/CommentBlock.tsx` — Footnote shows source label
- `.specify/memory/constitution.md` — Amendment 1.6.0

**Files NOT modified**:
- `backend/app/routers/chat.py` — Chat is unchanged
- `frontend/src/components/ChatPanel.tsx` — Chat UI is unchanged
- `backend/app/models.py` — `search_queries` column already exists (nullable Text storing JSON); works for `list[dict]` same as `list[str]`
- `backend/app/services/pipeline.py` — Already does `json.dumps(searches)`, works for dicts too

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | Tool dispatch remains within graph nodes |
| II. Expert Persona Integrity | PASS | Same personas, specialized tools deepen their expertise |
| III. Anti-AI-ism Voice | PASS | Footnotes are UI-only, not in generated text |
| IV. Idempotent Processing | PASS | No schema changes; old data handled by validator |
| V. Resilience | PASS | Each tool failure falls back gracefully |
| VII. Simplicity | PASS | Minimal new code; tools are standard LangChain wrappers |
| Technology Stack | AMENDMENT 1.6.0 | Expand "Web Search: Tavily" → "Research Tools: Tavily, Wikipedia, Arxiv" |

## Design

### 1. Per-persona tool registry

Replace `_get_search_tool()` with `_get_persona_tools(persona)` returning a list of tools:

```python
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper

_wikipedia_tool = None
_arxiv_tool = None

def _get_wikipedia_tool():
    global _wikipedia_tool
    if _wikipedia_tool is None:
        _wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=2000))
    return _wikipedia_tool

def _get_arxiv_tool():
    global _arxiv_tool
    if _arxiv_tool is None:
        _arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=2000))
    return _arxiv_tool

# Tool name → source label mapping
TOOL_SOURCE_LABELS = {
    "tavily_search": "Web",
    "wikipedia": "Wikipedia",
    "arxiv": "Arxiv",
}

def _get_persona_tools(persona: str) -> list:
    tavily = _get_search_tool()  # existing function, returns None if no API key
    tools = []
    if tavily:
        tools.append(tavily)

    if persona == "historian":
        tools.append(_get_wikipedia_tool())
    elif persona == "economist":
        tools.append(_get_arxiv_tool())

    return tools
```

### 2. Updated LLM binding

`_get_pipeline_llm` now accepts a `persona` parameter:

```python
def _get_pipeline_llm(temperature: float = 0.9, persona: str = "philosopher"):
    llm = _get_llm(temperature)
    tools = _get_persona_tools(persona)
    if tools:
        return llm.bind_tools(tools), tools
    return llm, []
```

### 3. Multi-tool dispatch in `_invoke_with_tools`

The invoke loop now dispatches tool calls by name using a `tools_by_name` dict. Each search record is a dict with `query` and `source`:

```python
def _invoke_with_tools(messages: list, *, temperature: float = 0.9, persona: str, max_tool_calls: int = 2) -> tuple[str, list[dict]]:
    llm, tools = _get_pipeline_llm(temperature, persona)
    tools_by_name = {t.name: t for t in tools}
    tool_calls_made = 0
    search_queries: list[dict] = []

    while True:
        response = llm.invoke(messages)

        if not response.tool_calls or not tools:
            return response.content, search_queries

        messages.append(response)
        for tc in response.tool_calls:
            tool_name = tc["name"]
            source_label = TOOL_SOURCE_LABELS.get(tool_name, tool_name)

            if tool_calls_made >= max_tool_calls:
                messages.append(ToolMessage(
                    content="Tool call limit reached. Write your response now.",
                    tool_call_id=tc["id"],
                ))
                continue

            try:
                query = tc["args"].get("query", tc["args"])
                search_queries.append({"query": str(query), "source": source_label})
                tool = tools_by_name.get(tool_name)
                result = tool.invoke(tc["args"])
                messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tc["id"],
                ))
            except Exception as e:
                logger.warning("%s search failed: %s", source_label, e)
                messages.append(ToolMessage(
                    content="Search unavailable. Write your response based on the article alone.",
                    tool_call_id=tc["id"],
                ))
            tool_calls_made += 1

    return response.content, search_queries
```

### 4. Node functions pass `persona=`

Each node passes its persona to `_invoke_with_tools`. Historian and economist get `max_tool_calls=3` since they have two tool types:

```python
def historian_node(state: CommentaryState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + HISTORIAN_PROMPT),
        HumanMessage(content=_build_user_message(state, "historian") + _make_length_reminder()),
    ]
    content, searches = _invoke_with_tools(messages, temperature=PERSONA_TEMPERATURES["historian"], persona="historian", max_tool_calls=3)
    return {"historian_comment": content, "historian_searches": searches}
```

Same pattern for economist (max_tool_calls=3) and philosopher (max_tool_calls=2, default).

### 5. Graph state changes

In `state.py`, search fields change from `list[str]` to `list[dict]`:

```python
class CommentaryState(TypedDict):
    ...
    historian_searches: list[dict]
    economist_searches: list[dict]
    philosopher_searches: list[dict]
```

### 6. Schema changes with backwards compatibility

In `schemas.py`, add a `SearchQuery` model and update the validator:

```python
class SearchQuery(BaseModel):
    query: str
    source: str

class CommentOut(BaseModel):
    ...
    search_queries: list[SearchQuery] = []

    @field_validator("search_queries", mode="before")
    @classmethod
    def parse_search_queries(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            v = json.loads(v)
        # Backwards compat: convert old list[str] to list[dict]
        if v and isinstance(v[0], str):
            return [{"query": s, "source": "Web"} for s in v]
        return v
```

### 7. Frontend changes

In `client.ts`:
```typescript
export interface SearchQuery {
  query: string;
  source: string;
}

export interface Comment {
  ...
  search_queries: SearchQuery[];
}
```

In `CommentBlock.tsx`, footnotes show the source label:
```tsx
{comment.search_queries.length > 0 && (
  <p className="mt-1 text-xs italic opacity-60">
    Researched: {comment.search_queries.map((sq) => `"${sq.query}" (${sq.source})`).join(", ")}
  </p>
)}
```

### 8. Search instructions update

Generalize `search_instructions.md` from "web search tool" to "search tools":

```markdown
## Search Instructions

You have access to **search tools**. You SHOULD use them to look up specific facts...
```

Add tool-specific guidance per persona in the prompt or keep it generic (the LLM will see the tool names/descriptions and use them appropriately).

## Data Flow

```
_get_persona_tools("historian")  → [TavilySearch, WikipediaQueryRun]
  ↓
_get_pipeline_llm(1.2, "historian") → llm.bind_tools([tavily, wikipedia])
  ↓
_invoke_with_tools(..., persona="historian", max_tool_calls=3)
  ↓
  LLM calls "wikipedia" tool → {"query": "Durand Line", "source": "Wikipedia"}
  LLM calls "tavily_search"  → {"query": "GDP growth 2025", "source": "Web"}
  ↓
historian_node() → {"historian_comment": "...", "historian_searches": [{"query":..., "source":...}]}
  ↓
CommentaryState → historian_searches: [{"query": "Durand Line", "source": "Wikipedia"}, ...]
  ↓
pipeline.py → Comment(search_queries='[{"query":"Durand Line","source":"Wikipedia"}]')
  ↓
SQLite comments table → search_queries TEXT NULL (JSON)
  ↓
GET /articles → CommentOut(search_queries=[SearchQuery(query="Durand Line", source="Wikipedia")])
  ↓
CommentBlock.tsx → Researched: "Durand Line" (Wikipedia), "GDP growth 2025" (Web)
```

## Backwards Compatibility

- `search_queries` column is unchanged — already nullable Text storing JSON.
- Old data stores `list[str]` (e.g., `'["query1", "query2"]'`). The Pydantic `field_validator` detects `list[str]` and converts to `[{"query": s, "source": "Web"}]`.
- New data stores `list[dict]` (e.g., `'[{"query": "Durand Line", "source": "Wikipedia"}]'`).
- Null values continue to produce `[]` in the API response.
- No database migration required.
