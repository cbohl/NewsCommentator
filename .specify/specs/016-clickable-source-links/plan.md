# Implementation Plan: Clickable Source Links in Footnotes

**Branch**: `give-additional-tools-to-agents` | **Date**: 2026-02-28 | **Spec**: `specs/016-clickable-source-links/spec.md`

## Summary

Extract source URLs from each tool's raw output (Tavily, Wikipedia, Yahoo Finance), carry them through the schema as `urls: list[SourceLink]`, and render them as clickable links in the frontend footnotes. Additionally improve Wikipedia search quality via prompt coaching and increased `top_k_results`.

## Technical Context

**Languages**: Python 3.12+, TypeScript
**New dependencies**: None (yfinance already installed; used inline for URL recovery)
**New env vars**: None

**Files modified**:
- `backend/app/graph/nodes.py` — URL extraction logic, Wikipedia top_k_results bump
- `backend/app/schemas.py` — SourceLink model, SearchQuery.urls field, backwards-compat validator
- `backend/app/graph/prompts/historian.md` — Wikipedia search tips
- `frontend/src/api/client.ts` — SourceLink interface, SearchQuery.urls field
- `frontend/src/components/CommentBlock.tsx` — SearchFootnote and SourceLinkItem components

**Files NOT modified**:
- `backend/app/models.py` — JSON column stores arbitrary dicts, no schema change needed
- `backend/app/services/pipeline.py` — URL extraction lives in `_invoke_with_tools`, not the pipeline
- `backend/app/routers/` — API shape unchanged

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | URL extraction happens inside graph node helper `_invoke_with_tools` |
| II. Expert Persona Integrity | PASS | Personas unchanged — only search tips added to historian |
| III. Anti-AI-ism Voice | PASS | Footnotes are metadata, not commentary text |
| V. Resilience Over Availability | PASS | URL extraction failures caught with try/except, empty list fallback |
| VII. Simplicity | PASS | No new abstractions — URLs are dicts in existing search_queries JSON |

## Design

### 1. URL Extraction in `_invoke_with_tools` (nodes.py)

After each successful tool invocation, a `urls: list[dict]` is constructed using tool-specific logic:

- **Tavily**: The tool returns `list[dict]` where each dict has `url` and `title` keys. Iterate and collect directly.
- **Wikipedia**: The tool returns a string with `"Page: {title}"` lines. Parse each such line, construct `https://en.wikipedia.org/wiki/{title_with_underscores}`. This gives up to `top_k_results` (now 3) article links.
- **Yahoo Finance**: The tool returns a text blob with article titles. To recover URLs (which the tool doesn't return), import `yfinance` inline and call `Ticker(query).news`. Match article titles from the tool result against the news feed to find canonical URLs. Wrapped in try/except so failures produce an empty list.

The `urls` list is appended to the existing search_queries dict alongside `query`, `source`, and `result_snippet`.

### 2. Schema Changes (schemas.py)

New `SourceLink` model with `url: str` and `title: str`.

`SearchQuery` gains `urls: list[SourceLink] = []`. A `model_validator(mode="before")` handles two legacy formats:
- Old single `url` string field (no `urls`): convert to `[{url, title=query}]`
- Old `urls` as plain strings: convert each to `{url, title=url}`

This ensures the API layer handles data from before this feature was added.

### 3. Frontend Types (client.ts)

New `SourceLink` interface (`url: string`, `title: string`). `SearchQuery` gains optional `urls?: SourceLink[]`.

### 4. Frontend Components (CommentBlock.tsx)

Two new components:

- **`SourceLinkItem`**: Renders a single `<a>` tag with `target="_blank"`, `rel="noopener noreferrer"`, underline styling.
- **`SearchFootnote`**: Conditional rendering based on URL count:
  - 0 URLs: plain text `"query" (source)`
  - 1 URL: entire footnote wrapped as single link with title
  - 2+ URLs: `"query" (source: link1, link2, ...)` with comma-separated SourceLinkItems

A shared `footnotes` JSX variable is computed once and rendered in both the mobile (`sm:hidden`) and desktop (`hidden sm:flex`) layouts, eliminating the previous code duplication.

### 5. Wikipedia Search Quality (historian.md)

Added a "Wikipedia search tips" paragraph coaching the LLM to use short 2-4 word queries matching encyclopedia article titles. Two concrete good/bad examples demonstrate the pattern (e.g., search "Ofgem" not "Ofgem energy price cap April 2025 typical bill").

### 6. Wikipedia Depth (nodes.py)

Changed `WikipediaAPIWrapper(top_k_results=2)` to `top_k_results=3`, giving the historian more articles per query and more potential source links.

## Backwards Compatibility

No impact on existing data. The `search_queries` JSON column in SQLite stores arbitrary dicts. Old records without `urls` fields deserialize correctly via the model validator (defaulting to empty list). Old records with a single `url` string are auto-converted to the new format. The frontend handles the optional `urls` field gracefully with the `?? []` fallback.
