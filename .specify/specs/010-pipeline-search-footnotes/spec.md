# Feature Specification: Pipeline Search Footnotes

**Feature Branch**: `give-agents-tools`
**Created**: 2026-02-26
**Status**: Draft
**Input**: User request: "Add footnotes below each pipeline-generated comment showing what the persona searched for. Searches only happen in the pipeline, never in chat."

## Constitution Amendment Required

None. Tool use in the pipeline is already permitted under amendment 1.5.0. This feature surfaces existing search metadata through the data layer to the frontend — no new capabilities are introduced.

## User Scenarios & Testing

### User Story 1 — Search Footnotes on Pipeline Comments (Priority: P1)

When a persona uses Tavily web search during the hourly pipeline, a subtle footnote appears below their comment showing what they searched for. This gives readers transparency into what research informed each comment.

**Why this priority**: Core feature. Without footnotes, readers have no visibility into whether a comment was informed by real research.

**Acceptance Scenarios**:

1. **Given** a persona searched for "Greece GDP 2025" while writing their comment, **When** the article is displayed in the frontend, **Then** a footnote below the comment reads: *Researched: "Greece GDP 2025"*.
2. **Given** a persona made two searches ("Durand Line history", "Afghanistan Pakistan border disputes"), **When** the article is displayed, **Then** the footnote lists both: *Researched: "Durand Line history", "Afghanistan Pakistan border disputes"*.
3. **Given** a persona wrote their comment without searching, **When** the article is displayed, **Then** no footnote appears below that comment.
4. **Given** all three personas wrote without searching, **When** the article is displayed, **Then** no footnotes appear on any comment.

---

### User Story 2 — Search Queries Persisted to Database (Priority: P1)

Search queries are stored alongside each comment in the database so they survive server restarts and are available to the API.

**Why this priority**: Without persistence, footnotes would only work for articles processed in the current session.

**Acceptance Scenarios**:

1. **Given** a persona searched while writing a comment, **When** the comment is saved to SQLite, **Then** the search queries are stored as a JSON string in a `search_queries` column on the `comments` table.
2. **Given** a persona did not search, **When** the comment is saved, **Then** the `search_queries` column is `null`.
3. **Given** an article was processed before this feature was deployed, **When** old comments are loaded, **Then** `search_queries` is `null` and no footnote renders (backwards-compatible).

---

### User Story 3 — Chat Remains Unchanged (Priority: P1)

The chat endpoint is completely unaffected. No tools, no search, no footnotes.

**Why this priority**: Chat is a separate feature with different latency requirements. It must not be modified.

**Acceptance Scenarios**:

1. **Given** a user sends a chat message, **When** the backend processes it, **Then** no tools are bound and no searches occur.
2. **Given** a chat response is displayed, **Then** no footnote UI appears.

### Edge Cases

- Persona searches but Tavily fails: The query is still recorded (the search was attempted), but results were unavailable. The footnote still shows the query.
- `search_queries` column is `null` for old data: The API returns `[]` and the frontend renders no footnote. No migration needed.
- Tavily is not configured (`TAVILY_API_KEY` unset): No searches ever occur, all `search_queries` are `null`, no footnotes appear. Identical to current behavior.

## Requirements

### Functional Requirements

- **FR-001**: `_invoke_with_tools` MUST return `tuple[str, list[str]]` — the response content and a list of search query strings.
- **FR-002**: Each search query MUST be appended to the list when a tool call is processed, including failed tool calls (the search was attempted).
- **FR-003**: `CommentaryState` MUST include `historian_searches`, `economist_searches`, `philosopher_searches` fields (each `list[str]`).
- **FR-004**: Each persona node MUST return its search queries in state alongside its comment.
- **FR-005**: The `Comment` model MUST have a nullable `search_queries` Text column storing JSON-serialized `list[str]`.
- **FR-006**: The pipeline MUST store search queries when creating `Comment` rows.
- **FR-007**: The `CommentOut` schema MUST expose `search_queries` as `list[str]`, defaulting to `[]` for null values.
- **FR-008**: The frontend `Comment` interface MUST include `search_queries: string[]`.
- **FR-009**: `CommentBlock.tsx` MUST render a footnote below the comment text when `search_queries` is non-empty.
- **FR-010**: `chat.py` MUST NOT be modified.

### Key Entities

- **`search_queries`**: A JSON-serialized `list[str]` stored on the `Comment` model. Each string is a Tavily search query that the persona executed (or attempted) while generating the comment.

## Success Criteria

- **SC-001**: Comments generated with search show footnotes listing search queries.
- **SC-002**: Comments generated without search show no footnotes.
- **SC-003**: Old comments (pre-feature) render without errors and without footnotes.
- **SC-004**: Chat is completely unchanged — no tools, no footnotes, no code changes.
- **SC-005**: Dropping and recreating the DB produces comments with footnotes on the next pipeline run (if Tavily is configured).
