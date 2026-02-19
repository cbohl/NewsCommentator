# Feature Specification: News Commentator MVP

**Feature Branch**: `001-news-commentator`
**Created**: 2026-02-19
**Status**: Draft
**Input**: User description: "Build a news commentary system with three expert AI personas analyzing Reuters articles on an hourly schedule."

## User Scenarios & Testing

### User Story 1 - View Expert Commentary on Latest News (Priority: P1)

A visitor opens the web app and sees a feed of recent Reuters articles, each accompanied by three expert commentaries (Historian, Economist, Philosopher). The comments are concise, opinionated, and free of AI filler language.

**Why this priority**: This is the core value proposition — without visible commentary, nothing else matters.

**Independent Test**: Load the frontend, verify at least one article displays with all three expert comments rendered beneath it.

**Acceptance Scenarios**:

1. **Given** the system has processed articles, **When** a visitor loads the homepage, **Then** they see articles listed in reverse-chronological order, each with three labeled expert comments.
2. **Given** an article has been processed, **When** a visitor reads the Historian comment, **Then** it is under 150 words, contains no AI-ism phrases, and never includes "In the grand tapestry of history."
3. **Given** an article has been processed, **When** a visitor reads the Economist comment, **Then** it contains no generic financial advice and focuses on incentives/game theory.
4. **Given** an article has been processed, **When** a visitor reads the Philosopher comment, **Then** it uses a Socratic or Analytical framing rooted in ethics or epistemology.

---

### User Story 2 - Automated Hourly Article Processing (Priority: P1)

The system automatically fetches new Reuters articles every hour, extracts full text via Jina AI Reader, generates three expert commentaries via LangGraph, and persists everything to SQLite — all without manual intervention.

**Why this priority**: Equal to US1 — the pipeline is what generates the content the frontend displays. Without automation, the system is dead.

**Independent Test**: Start the backend, wait for one scheduler tick (or trigger manually), verify a new article + 3 comments appear in the database.

**Acceptance Scenarios**:

1. **Given** the scheduler fires, **When** Reuters RSS returns new articles, **Then** each new article is extracted via Jina AI Reader and passed through the LangGraph pipeline.
2. **Given** an article URL already exists in the database, **When** the scheduler processes the same RSS feed again, **Then** the duplicate article is silently skipped.
3. **Given** Jina AI Reader fails for one article, **When** the pipeline encounters the error, **Then** it logs the failure to `error_log` and continues processing remaining articles.

---

### User Story 3 - System Health Monitoring (Priority: P2)

An operator can check the `/health` endpoint to confirm the system is alive and see when the last successful processing run occurred.

**Why this priority**: Important for operational confidence, but the system functions without it.

**Independent Test**: Call `GET /health` and verify it returns a JSON object with a `last_successful_run` timestamp.

**Acceptance Scenarios**:

1. **Given** the system has processed at least one batch, **When** an operator calls `GET /health`, **Then** the response includes `{"status": "ok", "last_successful_run": "<ISO timestamp>"}`.
2. **Given** the system has never processed anything, **When** an operator calls `GET /health`, **Then** the response includes `{"status": "ok", "last_successful_run": null}`.

---

### Edge Cases

- What happens when Reuters RSS is temporarily unreachable? The scheduler logs the failure and retries on the next hourly tick.
- What happens when Jina AI Reader returns truncated or empty text? The article is skipped with an error log entry; no empty comments are generated.
- What happens when the LLM returns a comment exceeding 150 words? The system logs a warning but stores the comment as-is (prompt engineering is the primary enforcement).
- What happens when all articles in a feed batch are duplicates? The pipeline completes successfully with zero new records.

## Requirements

### Functional Requirements

- **FR-001**: System MUST fetch articles from Reuters RSS feed on an hourly schedule via APScheduler.
- **FR-002**: System MUST extract full article text using `https://r.jina.ai/{url}` prefixing.
- **FR-003**: System MUST deduplicate articles by RSS GUID or canonical URL using a UNIQUE constraint in SQLite.
- **FR-004**: System MUST generate exactly three expert comments (Historian, Economist, Philosopher) per article via a LangGraph StateGraph.
- **FR-005**: Each expert comment MUST be constrained to a maximum of 150 words with no AI-ism filler.
- **FR-006**: System MUST log all processing failures to an `error_log` table with article URL, timestamp, and traceback.
- **FR-007**: System MUST expose a `GET /health` endpoint returning the last successful run timestamp.
- **FR-008**: System MUST serve a REST API for the frontend to retrieve articles and their comments.
- **FR-009**: Frontend MUST display articles with their three expert commentaries in a responsive layout.

### Key Entities

- **Article**: Represents a processed news article — title, full text, source URL, RSS GUID, created timestamp.
- **Comment**: Represents one expert's commentary — linked to an Article, persona label (historian/economist/philosopher), comment text, created timestamp.
- **ErrorLog**: Represents a processing failure — article URL (nullable), error message, traceback, timestamp.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The homepage displays at least one article with all three expert comments within 1 hour of first deployment.
- **SC-002**: Zero duplicate articles exist in the database after 24 hours of operation.
- **SC-003**: All expert comments are under 150 words and contain none of the banned AI-ism phrases.
- **SC-004**: A single article processing failure does not prevent remaining articles in the batch from being processed.
- **SC-005**: `GET /health` responds in under 200ms with the correct last-run timestamp.
