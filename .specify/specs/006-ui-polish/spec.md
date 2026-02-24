# Feature Specification: UI Polish — Avatars, Display Order & Layout

**Feature Branch**: `006-ui-polish`
**Created**: 2026-02-23
**Status**: Complete (retroactive)
**Input**: User request: "Add avatar images for each persona, fix the comment display order, widen the page layout, and put avatars side-by-side with text."

## Overview

Bundle of UI improvements to make the commentary panel feel like a real discussion between recognizable people rather than anonymous text blocks. Four changes shipped together:

1. **Avatar images** — DALL-E generated portraits for Maggie, Tim, and Sofia, cropped into individual PNG files served from `/public/avatars/`.
2. **Comment display order** — Added `position` field to the Comment model so comments render in execution order (the randomized LangGraph sequence), not insertion order.
3. **Wider page layout** — Increased `max-w-4xl` to `max-w-6xl` on the main container to give avatars room to breathe.
4. **Side-by-side layout** — CommentBlock renders avatar image beside the text using flexbox.

## User Scenarios & Testing

### User Story 1 — Recognizable Personas (Priority: P1)

Each persona has a distinct visual identity via an avatar image displayed alongside their comment.

**Why this priority**: Avatars are the primary visual anchor for persona recognition.

**Acceptance Scenarios**:

1. **Given** any article with comments, **When** the page loads, **Then** each comment displays a 144px square avatar to the left of the text.
2. **Given** a persona with no avatar path configured, **When** rendering the comment, **Then** the avatar image is omitted gracefully (no broken image).

---

### User Story 2 — Correct Display Order (Priority: P1)

Comments display in the order they were generated (execution order), not database insertion order.

**Acceptance Scenarios**:

1. **Given** an article where the execution order was Philosopher → Historian → Economist, **When** viewing the article, **Then** Sofia's comment appears first, Maggie's second, Tim's third.
2. **Given** the `comments` relationship on Article, **When** SQLAlchemy loads comments, **Then** they are ordered by `Comment.position` ascending.

---

### User Story 3 — Wider Layout (Priority: P2)

The page container is wide enough to comfortably display avatar + text side-by-side without cramping.

**Acceptance Scenarios**:

1. **Given** the Layout component, **When** rendered on a desktop viewport, **Then** the main content area uses `max-w-6xl` (1152px).

---

### User Story 4 — Side-by-Side Avatar + Text (Priority: P1)

Avatar and comment text sit side-by-side in a flex row, not stacked.

**Acceptance Scenarios**:

1. **Given** a comment with an avatar, **When** rendered, **Then** the avatar and text are in a horizontal flex container with a gap.
2. **Given** the avatar, **When** rendered, **Then** it uses `object-cover` and `flex-shrink-0` to maintain its aspect ratio and not collapse.

## Requirements

### Functional Requirements

- **FR-001**: Each persona entry in `PERSONA_STYLES` MUST include an `avatar` path pointing to `/avatars/{name}.png`.
- **FR-002**: The Comment model MUST have a `position` integer column (default 0) representing execution order.
- **FR-003**: The CommentOut schema MUST expose the `position` field.
- **FR-004**: Pipeline MUST save `position` based on the randomized execution order index (0, 1, 2).
- **FR-005**: The Article model's `comments` relationship MUST be ordered by `Comment.position`.
- **FR-006**: Layout main container MUST use `max-w-6xl`.
- **FR-007**: CommentBlock MUST render avatar and text in a flex row with `gap-4`.

## Success Criteria

- **SC-001**: All three avatar images exist at `frontend/public/avatars/{maggie,tim,sofia}.png`.
- **SC-002**: Comments display in execution order on every article.
- **SC-003**: Page width is `max-w-6xl` (1152px max).
- **SC-004**: Avatar displays at 144px square with rounded corners alongside text.
