# 017 — Feed Categories: Implementation Plan

## Files to Modify

| File | Change |
|------|--------|
| `backend/app/services/rss.py` | Feed registry dict, `feed` param, tag articles |
| `backend/app/models.py` | Add `feed` column to Article |
| `backend/app/main.py` | Startup migration helper for `feed` column |
| `backend/app/services/pipeline.py` | Pass `feed` through, set `article.feed` |
| `backend/app/routers/articles.py` | Add `feed` query param to GET /articles and POST /trigger |
| `backend/app/schemas.py` | Add `feed` to ArticleOut |
| `frontend/src/api/client.ts` | Add `feed` to Article, update `fetchArticles` |
| `frontend/src/pages/Home.tsx` | Tab bar UI, feed state, re-fetch on tab change |

## Approach

1. RSS: FEEDS dict maps name→URL. `fetch_rss_articles(limit, feed=None)` fetches one or all feeds, returns dicts with `"feed"` key.
2. Model: `feed` column with default `"world"`, indexed.
3. Migration: On startup, check if column exists via SQLite pragma, ALTER TABLE if not.
4. Pipeline: `process_new_articles(limit=1, feed=None)` passes feed through to RSS and sets `article.feed`.
5. Scheduler: Calls `process_new_articles(limit=1, feed=None)` — 1 article per feed per hour.
6. API: Optional `feed` query param filters articles; trigger accepts `feed` to process specific feed.
7. Frontend: Tab bar with `activeFeed` state, default `"business"`. Clicking re-fetches with `?feed=`.
