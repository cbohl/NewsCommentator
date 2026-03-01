# Feature Specification: Clickable Source Links in Footnotes

**Feature Branch**: `give-additional-tools-to-agents`
**Created**: 2026-02-28
**Status**: Complete
**Input**: Footnotes previously showed plain-text search queries with source labels (e.g., `"Ofgem" (Wikipedia)`). Users wanted clickable links to the actual sources each persona read — Wikipedia articles, Yahoo Finance news, and Tavily search results.

## Constitution Amendment Required

None. This enhances the existing search footnotes UI and backend metadata. No changes to architecture, data model schema, API contract, or technology stack.

## Rationale

Search footnotes were introduced in spec 010 and refined through specs 011–012, but they only displayed the query string and source label — readers couldn't verify or explore the sources. Making footnotes clickable required: (1) extracting or constructing URLs from each tool's raw output, (2) supporting multiple URLs per search (Tavily and Yahoo Finance return several articles), (3) a schema change to carry `urls: list[SourceLink]` with backwards compatibility for old data, and (4) a frontend component to render single links, multi-links, or plain text conditionally. Additionally, the historian's Wikipedia searches were returning poor results because the LLM sent long natural-language queries; a prompt coaching fix and `top_k_results` increase from 2 to 3 improved search quality.

## Requirements

```json
[
  {
    "name": "URL Extraction per Tool Type",
    "description": "System must extract source URLs from each tool's raw result in _invoke_with_tools, and it should use tool-specific parsing (Tavily: url/title from result dicts; Wikipedia: construct URLs from 'Page: {title}' lines; Yahoo Finance: match article titles against yfinance.Ticker.news to recover canonical URLs), so that each search_query entry includes a urls list of {url, title} dicts",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a Tavily search that returns 3 results, When _invoke_with_tools processes the tool call, Then urls contains 3 entries each with a url and title from the Tavily response",
      "Given a Wikipedia search that returns a result containing 'Page: Volcker shock', When _invoke_with_tools processes the tool call, Then urls contains an entry with url 'https://en.wikipedia.org/wiki/Volcker_shock' and title 'Volcker shock'",
      "Given a Yahoo Finance search for 'AAPL' that returns 2 article titles, When _invoke_with_tools matches them against yfinance.Ticker('AAPL').news, Then urls contains entries with canonical URLs and titles for the matched articles",
      "Given a Yahoo Finance search where yfinance returns 'No news found', When _invoke_with_tools processes the result, Then urls is an empty list"
    ]
  },
  {
    "name": "SourceLink and SearchQuery Schema",
    "description": "System must define a SourceLink model (url, title) and add urls: list[SourceLink] to SearchQuery, and it should include a model_validator for backwards compatibility that converts old single 'url' string fields and old urls-as-plain-strings formats to the new list[SourceLink] structure, so that both new and legacy data deserializes correctly",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a SearchQuery with urls: [{url: 'https://...', title: 'Article'}], When serialized to JSON, Then the urls field contains the SourceLink objects",
      "Given legacy data with a single 'url' string field and no 'urls' field, When deserialized into SearchQuery, Then urls contains one SourceLink with the old url and query as title",
      "Given legacy data with urls as plain strings ['https://a.com', 'https://b.com'], When deserialized into SearchQuery, Then urls contains SourceLink objects with url as both url and title",
      "Given a SearchQuery with no urls field, When deserialized, Then urls defaults to an empty list"
    ]
  },
  {
    "name": "Frontend Clickable Footnotes",
    "description": "System must render search footnotes as clickable links using a SearchFootnote component, and it should conditionally render: plain text for zero URLs, a single wrapped link for one URL, or comma-separated titled links for multiple URLs, so that readers can click through to actual sources",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a search query with zero URLs, When the SearchFootnote component renders, Then it shows '\"query\" (source)' as plain text with no anchor tags",
      "Given a search query with one URL, When the SearchFootnote component renders, Then the entire footnote is a single clickable link showing '\"query\" (source: title)'",
      "Given a search query with 3 URLs, When the SearchFootnote component renders, Then it shows '\"query\" (source: link1, link2, link3)' with each link as a separate clickable anchor",
      "Given any rendered source link, When inspected in the DOM, Then it has target='_blank' and rel='noopener noreferrer' attributes"
    ]
  },
  {
    "name": "Frontend SourceLink TypeScript Types",
    "description": "System must define SourceLink interface (url, title) in client.ts and add optional urls field to SearchQuery interface, so that the frontend type system matches the backend schema",
    "type": "infrastructure",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given the client.ts file, When inspected, Then SourceLink interface has url: string and title: string fields",
      "Given the SearchQuery interface, When inspected, Then it has an optional urls?: SourceLink[] field"
    ]
  },
  {
    "name": "Wikipedia Search Quality Coaching",
    "description": "System must coach the historian to use short 2-4 word Wikipedia queries matching encyclopedia article titles, and it should add explicit search tips with good/bad examples to historian.md, so that Wikipedia lookups return relevant articles instead of missing or off-topic results",
    "type": "business_logic",
    "confidence": 0.9,
    "source_lines": [],
    "acceptance_criteria": [
      "Given the historian.md prompt, When read by a developer, Then it contains search tips instructing short 2-4 word queries",
      "Given the historian.md prompt, When read by a developer, Then it contains at least two examples contrasting good queries (e.g., 'Ofgem') with bad queries (e.g., 'Ofgem energy price cap April 2025 typical bill')"
    ]
  },
  {
    "name": "Wikipedia Depth Increase",
    "description": "System must return 3 Wikipedia articles per query instead of 2, and it should change top_k_results from 2 to 3 in the WikipediaAPIWrapper initialization, so that the historian has more material to draw from and more source links to display",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given the _get_wikipedia_tool function in nodes.py, When inspected, Then WikipediaAPIWrapper is initialized with top_k_results=3",
      "Given a Wikipedia search that matches 3 articles, When _invoke_with_tools parses the result, Then up to 3 Page titles are extracted into the urls list"
    ]
  }
]
```

## Files Modified

- `backend/app/graph/nodes.py` — Added URL extraction logic per tool type in `_invoke_with_tools`; changed Wikipedia `top_k_results` from 2 to 3; added `urls` field to search_queries dicts
- `backend/app/schemas.py` — Added `SourceLink` model; added `urls: list[SourceLink]` to `SearchQuery`; added `model_validator` for backwards compat with old `url` string and plain-string list formats
- `backend/app/graph/prompts/historian.md` — Added Wikipedia search tips section coaching short 2-4 word queries with good/bad examples
- `frontend/src/api/client.ts` — Added `SourceLink` interface; added optional `urls` field to `SearchQuery`
- `frontend/src/components/CommentBlock.tsx` — Added `SourceLinkItem` and `SearchFootnote` components; refactored footnotes to use shared `footnotes` variable rendered in both mobile and desktop layouts

## Files NOT Modified

- `backend/app/models.py` — DB model unchanged; `search_queries` is a JSON column that stores arbitrary dicts
- `backend/app/services/pipeline.py` — Pipeline unchanged; URL extraction happens inside `_invoke_with_tools`
- `backend/app/routers/` — API endpoints unchanged
- `backend/app/graph/prompts/economist.md` — Economist prompt unchanged
- `backend/app/graph/prompts/philosopher.md` — Philosopher prompt unchanged
- `backend/app/graph/state.py` — Graph state unchanged
