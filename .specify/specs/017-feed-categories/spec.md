# 017 — Feed Categories with Tab Selector

## Problem

The app mixes BBC World and Business feeds together with no way to filter. Users want the option to avoid world news and browse by category.

## Solution

Separate articles into three BBC feeds (Business, Technology, World), add a `feed` column to the Article model, expose feed filtering via the API, and add a tab bar UI to switch between feeds.

## Requirements

1. **RSS Feed Registry** — Replace flat feed list with a dict mapping feed names (`business`, `technology`, `world`) to URLs
2. **Article.feed column** — New indexed string column, default `"world"` for backwards compat
3. **Startup migration** — SQLite ALTER TABLE to add column if missing (no Alembic)
4. **Pipeline** — Tag each article with its feed name during processing
5. **API filtering** — Optional `feed` query param on GET /articles and POST /trigger
6. **Schema** — Add `feed: str` to ArticleOut
7. **Frontend types** — Add `feed` to Article interface, update fetchArticles
8. **Tab bar UI** — Three tabs (Business, Technology, World) that filter articles by feed

## Backwards Compatibility

- Existing articles get `feed="world"` via column default
- API `feed` param is optional; omitting returns all articles
- Frontend change is purely additive
