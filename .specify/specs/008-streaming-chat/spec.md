# Feature Specification: Streaming Chat with the Panel

**Feature Branch**: `008-streaming-chat`
**Created**: 2026-02-24
**Status**: Draft
**Input**: User request: "Let users chat with the panel about a specific article via SSE streaming. Chat appears below the three comments on each article. Ongoing thread, ephemeral. If user mentions a persona by name, that persona responds first. All three respond each turn, one at a time, streaming token-by-token."

## Constitution Amendment Required

Article VII (API Contract) currently states: "No GraphQL, no WebSockets unless constitutionally amended." SSE (Server-Sent Events) is a distinct technology from WebSockets — it uses standard HTTP and is uni-directional. However, for clarity:

**Amendment 1.4.0**: Add SSE streaming as a permitted API transport for the chat feature. SSE is not WebSockets — it is uni-directional HTTP streaming compatible with the existing REST architecture. The chat feature is ephemeral (no database persistence) and does not alter the existing article commentary pipeline.

## User Scenarios & Testing

### User Story 1 — Chat with the Panel (Priority: P1)

A user can chat with the panel about a specific article. The chat appears inline below the three persona comments on that article.

**Why this priority**: The core feature.

**Acceptance Scenarios**:

1. **Given** a user viewing an article with comments, **When** they click "Chat with the panel about this article...", **Then** a chat input appears below the comments.
2. **Given** the chat is open, **When** they type a message and press Enter, **Then** the message appears in the chat thread.
2. **Given** a submitted message, **When** the backend processes it, **Then** three persona responses stream in one at a time, with tokens appearing incrementally.
3. **Given** a streaming response, **When** tokens arrive, **Then** each token appends to the current persona's response in real-time (no flicker, no re-render of completed text).

---

### User Story 2 — Persona Mention Routing (Priority: P1)

If a user mentions a persona by name, that persona responds first.

**Acceptance Scenarios**:

1. **Given** a message containing "Maggie" (case-insensitive), **When** the backend determines response order, **Then** the historian responds first, followed by the other two in random order.
2. **Given** a message containing "Tim", **When** determining order, **Then** the economist responds first.
3. **Given** a message containing "Sofia", **When** determining order, **Then** the philosopher responds first.
4. **Given** a message mentioning multiple personas (e.g., "Maggie and Tim"), **When** determining order, **Then** the first mentioned persona responds first, the second mentioned responds second, the remaining third.
5. **Given** a message mentioning no persona by name, **When** determining order, **Then** all three respond in random order.

---

### User Story 3 — Ongoing Thread (Priority: P1)

The chat maintains conversational context across multiple turns within a session.

**Acceptance Scenarios**:

1. **Given** a user has sent 3 messages with responses, **When** sending a 4th message, **Then** all prior messages and responses are included in the LLM context.
2. **Given** a page refresh, **When** the chat loads, **Then** the thread is empty (ephemeral — no DB persistence).

---

### User Story 4 — Ephemeral Storage (Priority: P1)

Chat messages are not stored in the database. They exist only in the frontend session state.

**Acceptance Scenarios**:

1. **Given** a chat conversation, **When** inspecting the database, **Then** no chat-related tables or rows exist.
2. **Given** a page refresh, **When** the chat loads, **Then** previous messages are gone.

---

### User Story 5 — Visual Integration (Priority: P2)

The chat panel integrates cleanly with the existing UI, using persona avatars and color coding.

**Acceptance Scenarios**:

1. **Given** a persona response in the chat, **When** rendered, **Then** it shows the persona's avatar, name, and color scheme matching the existing CommentBlock styling.
2. **Given** the chat panel, **When** viewing on desktop, **Then** it appears inline within the article card, below the persona comments.

### Edge Cases

- User sends empty message — ignore, do not submit.
- User sends message while a response is still streaming — queue it or disable input until current response completes.
- SSE connection drops mid-stream — display partial response, show error indicator, allow retry.
- Very long conversation history — truncate oldest messages from LLM context to stay within token limits (keep last ~10 exchanges).
- User mentions a persona name embedded in another word (e.g., "Timmy") — only match whole-word "Tim", "Maggie", "Sofia" or their full names.

## Requirements

### Functional Requirements

- **FR-001**: A `POST /chat/stream` endpoint MUST accept a JSON body with `article_id` and `messages` (array of `{role, content}`) and return an SSE stream. The article's title, full text, and original panel comments are included as LLM context.
- **FR-002**: The SSE stream MUST emit events with `event: token` and `data: {"persona": "...", "token": "..."}` for each token.
- **FR-003**: The SSE stream MUST emit `event: persona_start` with `data: {"persona": "..."}` before each persona begins responding.
- **FR-004**: The SSE stream MUST emit `event: persona_end` with `data: {"persona": "..."}` after each persona finishes.
- **FR-005**: The SSE stream MUST emit `event: done` when all three personas have responded.
- **FR-006**: Persona response order MUST be determined by name-mention detection in the user's latest message.
- **FR-007**: Each persona MUST receive the full conversation history plus their character prompt as context.
- **FR-008**: The chat MUST use the same persona prompts (SYSTEM_RULES + persona prompt) as the article commentary pipeline.
- **FR-009**: Chat data MUST NOT be persisted to the database.
- **FR-010**: The frontend MUST maintain the chat thread in React state (ephemeral).
- **FR-011**: The frontend MUST disable the input while a response is streaming.
- **FR-012**: Conversation context sent to the LLM MUST be truncated to the last 10 exchanges if the thread grows long.

### Key Entities

- **ChatMessage**: `{role: "user" | "assistant", persona?: string, content: string}` — frontend-only, not a DB model.
- **SSE Events**: `persona_start`, `token`, `persona_end`, `done` — the streaming protocol.

## Success Criteria

- **SC-001**: User can type a message and see three persona responses stream in token-by-token.
- **SC-002**: Mentioning "Maggie" causes the historian to respond first.
- **SC-003**: Conversation context is maintained across turns within a session.
- **SC-004**: Page refresh clears the chat (no DB persistence).
- **SC-005**: Streaming responses show persona avatar, name, and color scheme.
- **SC-006**: Input is disabled while streaming, re-enabled after `done` event.
