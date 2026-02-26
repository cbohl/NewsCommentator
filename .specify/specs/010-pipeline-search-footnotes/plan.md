# Implementation Plan: Pipeline Search Footnotes

**Branch**: `give-agents-tools` | **Date**: 2026-02-26 | **Spec**: `specs/010-pipeline-search-footnotes/spec.md`

## Summary

Thread search query metadata from `_invoke_with_tools` through the LangGraph state, into the database, out through the API, and into the frontend as footnotes below pipeline-generated comments. Chat is untouched.

## Technical Context

**Languages**: Python 3.12+, TypeScript
**New dependencies**: None
**New env vars**: None (Tavily already configured via 009)

**Files to modify**:
- `backend/app/graph/nodes.py` — Change `_invoke_with_tools` return type, update node functions
- `backend/app/graph/state.py` — Add `*_searches` fields
- `backend/app/models.py` — Add `search_queries` column to `Comment`
- `backend/app/services/pipeline.py` — Pass search queries when creating `Comment` rows
- `backend/app/schemas.py` — Expose `search_queries` in `CommentOut`
- `frontend/src/api/client.ts` — Add `search_queries` to `Comment` interface
- `frontend/src/components/CommentBlock.tsx` — Render footnote

**Files NOT modified**:
- `backend/app/routers/chat.py` — Chat is unchanged
- `frontend/src/components/ChatPanel.tsx` — Chat UI is unchanged
- `.specify/memory/constitution.md` — No amendment needed

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | Search metadata flows through graph state like comments |
| II. Expert Persona Integrity | PASS | Same personas, same prompts |
| III. Anti-AI-ism Voice | PASS | Footnotes are UI-only, not in generated text |
| IV. Idempotent Processing | PASS | New column is nullable; old data unaffected |
| V. Resilience | PASS | Null search_queries is the default; nothing breaks |
| VII. Simplicity | PASS | One new column, minimal code across 7 files |

## Design

### 1. `_invoke_with_tools` returns search queries

**Current signature**: `_invoke_with_tools(messages, *, temperature, max_tool_calls) -> str`
**New signature**: `_invoke_with_tools(messages, *, temperature, max_tool_calls) -> tuple[str, list[str]]`

Add a `search_queries: list[str]` accumulator. Each time a tool call is processed (including failures), append `str(query)`. Return `(response.content, search_queries)`.

```python
def _invoke_with_tools(messages, *, temperature=0.9, max_tool_calls=2) -> tuple[str, list[str]]:
    ...
    search_queries: list[str] = []
    ...
            search_queries.append(str(query))
    ...
        return response.content, search_queries
```

### 2. Graph state tracks searches

Add three new fields to `CommentaryState`:

```python
class CommentaryState(TypedDict):
    ...
    historian_searches: list[str]
    economist_searches: list[str]
    philosopher_searches: list[str]
```

### 3. Node functions store searches in state

Each node unpacks the tuple and returns both:

```python
def historian_node(state: CommentaryState) -> dict:
    ...
    content, searches = _invoke_with_tools(messages, temperature=...)
    return {"historian_comment": content, "historian_searches": searches}
```

Same pattern for economist and philosopher.

### 4. `Comment` model gets `search_queries` column

```python
import json

class Comment(Base):
    ...
    search_queries: Mapped[str | None] = mapped_column(Text, nullable=True)
```

Stored as a JSON string (e.g., `'["Greece GDP 2025", "EU fiscal policy"]'`). Null when no searches were made.

### 5. Pipeline stores search queries

In `pipeline.py`, when creating `Comment` rows:

```python
searches = result.get(f"{persona}_searches", [])
comment = Comment(
    article_id=article.id,
    persona=persona,
    position=position,
    text=result[f"{persona}_comment"],
    search_queries=json.dumps(searches) if searches else None,
)
```

### 6. API schema exposes search queries

In `schemas.py`, add a computed field:

```python
from pydantic import BaseModel, field_validator

class CommentOut(BaseModel):
    ...
    search_queries: list[str] = []

    @field_validator("search_queries", mode="before")
    @classmethod
    def parse_search_queries(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return json.loads(v)
        return v
```

This handles null (old data), JSON strings (new data), and already-parsed lists.

### 7. Frontend renders footnotes

In `client.ts`:
```typescript
export interface Comment {
  ...
  search_queries: string[];
}
```

In `CommentBlock.tsx`, after the comment text (both mobile and desktop layouts):

```tsx
{comment.search_queries.length > 0 && (
  <p className="mt-1 text-xs italic opacity-60">
    Researched: {comment.search_queries.map((q) => `"${q}"`).join(", ")}
  </p>
)}
```

## Data Flow

```
_invoke_with_tools()          → (content, ["query1", "query2"])
  ↓
historian_node()              → {"historian_comment": content, "historian_searches": [...]}
  ↓
CommentaryState               → historian_searches: ["query1", "query2"]
  ↓
pipeline.py                   → Comment(search_queries='["query1","query2"]')
  ↓
SQLite comments table          → search_queries TEXT NULL
  ↓
GET /articles                  → CommentOut(search_queries=["query1","query2"])
  ↓
CommentBlock.tsx              → Researched: "query1", "query2"
```

## Backwards Compatibility

- `search_queries` column is nullable — old rows have `null`.
- The Pydantic `field_validator` converts `null` → `[]`.
- The frontend checks `search_queries.length > 0` before rendering.
- No migration needed — SQLite adds nullable columns without issues.
