# Tasks: UI Polish — Avatars, Display Order & Layout

**Input**: `specs/006-ui-polish/plan.md`

## Phase 1: Backend — Display Order

- [x] T001 Add `position` integer column (default 0) to Comment model in `backend/app/models.py`
- [x] T002 Add `order_by="Comment.position"` to Article.comments relationship in `backend/app/models.py`
- [x] T003 Add `position: int` field to CommentOut schema in `backend/app/schemas.py`
- [x] T004 Save `position` from `enumerate(order)` in pipeline comment creation in `backend/app/services/pipeline.py`

## Phase 2: Frontend — Avatars & Layout

- [x] T005 Add avatar images (`maggie.png`, `tim.png`, `sofia.png`) to `frontend/public/avatars/`
- [x] T006 Add `avatar` key to each entry in `PERSONA_STYLES` in `frontend/src/components/CommentBlock.tsx`
- [x] T007 Render avatar image side-by-side with text using flex layout in `frontend/src/components/CommentBlock.tsx`
- [x] T008 Widen main container from `max-w-4xl` to `max-w-6xl` in `frontend/src/components/Layout.tsx`

## Phase 3: Deploy & Validate

- [x] T009 Deploy and verify avatars render, comments display in execution order, and layout is wider
