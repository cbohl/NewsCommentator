# Tasks: Clickable Source Links in Footnotes

**Input**: `specs/016-clickable-source-links/plan.md`

## Phase 1: Backend URL Extraction

- [x] T001 Add Tavily URL extraction in `_invoke_with_tools` — iterate result list, collect `url` and `title` from each dict
- [x] T002 Add Wikipedia URL construction in `_invoke_with_tools` — parse `"Page: {title}"` lines, build `https://en.wikipedia.org/wiki/{title}` URLs
- [x] T003 Add Yahoo Finance URL recovery in `_invoke_with_tools` — match article titles against `yfinance.Ticker.news` to get canonical URLs
- [x] T004 Append `urls` list to search_queries dict for each tool call

## Phase 2: Schema Changes

- [x] T005 Add `SourceLink` model to `schemas.py` (url, title)
- [x] T006 Add `urls: list[SourceLink]` field to `SearchQuery` model
- [x] T007 Add `model_validator` for backwards compat — convert old single `url` string and plain-string lists to `list[SourceLink]`

## Phase 3: Frontend Types and Components

- [x] T008 Add `SourceLink` interface to `client.ts` (url, title)
- [x] T009 Add optional `urls` field to `SearchQuery` interface in `client.ts`
- [x] T010 Create `SourceLinkItem` component in `CommentBlock.tsx` — renders `<a>` with `target="_blank"` and `rel="noopener noreferrer"`
- [x] T011 Create `SearchFootnote` component in `CommentBlock.tsx` — conditional rendering for 0, 1, or multiple URLs
- [x] T012 Refactor footnotes to shared JSX variable, render in both mobile and desktop layouts

## Phase 4: Wikipedia Search Quality

- [x] T013 Add Wikipedia search tips to `historian.md` — coach short 2-4 word queries with good/bad examples
- [x] T014 Increase Wikipedia `top_k_results` from 2 to 3 in `_get_wikipedia_tool`

## Phase Dependencies

- Phase 2 depends on Phase 1 (schema must match data shape from extraction)
- Phase 3 depends on Phase 2 (frontend types must match backend schema)
- Phase 4 is independent of Phases 1-3
- T001, T002, T003 are independent [P]
- T008, T009 are independent of T010, T011, T012 [P]
- T013, T014 are independent [P]
