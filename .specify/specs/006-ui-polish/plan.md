# Implementation Plan: UI Polish — Avatars, Display Order & Layout

**Branch**: `006-ui-polish` | **Date**: 2026-02-23 | **Spec**: `specs/006-ui-polish/spec.md`

## Summary

Add persona avatar images, fix comment display order via a `position` column, widen the page layout, and render avatars side-by-side with comment text.

## Technical Context

**Files affected**:
- `backend/app/models.py` — Add `position` column to Comment, add `order_by` to Article.comments relationship
- `backend/app/schemas.py` — Add `position` field to CommentOut
- `backend/app/services/pipeline.py` — Save `position` from execution order index
- `frontend/src/components/CommentBlock.tsx` — Add avatar rendering, flex layout
- `frontend/src/components/ArticleCard.tsx` — No changes needed (comments already mapped in order)
- `frontend/src/components/Layout.tsx` — Change `max-w-4xl` to `max-w-6xl`
- `frontend/public/avatars/` — Add `maggie.png`, `tim.png`, `sofia.png`

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | No orchestration changes |
| II. Expert Persona Integrity | PASS | Visual identity reinforces personas |
| III. Anti-AI-ism Voice | PASS | No prompt changes |
| VII. Simplicity | PASS | Minimal additions, no new dependencies |

No constitution amendment required.

## Design

### Avatar Strategy

1. Generate composite image via DALL-E with all three personas.
2. User replaces with custom art if desired.
3. Crop into individual files: `maggie.png`, `tim.png`, `sofia.png`.
4. Serve from Vite's `public/avatars/` directory (static assets).

### Position Column

Add `position: Mapped[int]` to Comment with `default=0`. In pipeline, `enumerate(order)` provides the position index. Article relationship uses `order_by="Comment.position"` to ensure consistent rendering.

### Layout Changes

- `CommentBlock`: Wrap content in `flex gap-4`, avatar as `img` with `w-36 h-36 rounded-lg object-cover flex-shrink-0`.
- `Layout`: Change `max-w-4xl` to `max-w-6xl` on the `<main>` element.
- `PERSONA_STYLES`: Add `avatar` key to each persona entry.
