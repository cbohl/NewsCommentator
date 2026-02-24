# Implementation Plan: Streaming Chat with the Panel

**Branch**: `008-streaming-chat` | **Date**: 2026-02-24 | **Spec**: `specs/008-streaming-chat/spec.md`

## Summary

Add a per-article chat feature where users can converse with the three-persona panel about a specific article via SSE streaming. The chat appears inline below the persona comments on each article card. All three personas respond to each user message, one at a time, streaming token-by-token. The backend looks up the article by ID and includes its title, full text, and original panel comments as LLM context. Chat is ephemeral (frontend state only, no DB). Persona mention in the user message determines who responds first.

## Technical Context

**Languages**: Python 3.12+, TypeScript 5.9
**New dependencies**: `sse-starlette` (Python — SSE response helper for FastAPI)
**Files to create**:
- `backend/app/routers/chat.py` — SSE streaming endpoint
- `frontend/src/components/ChatPanel.tsx` — Chat UI component

**Files to modify**:
- `backend/app/main.py` — Register chat router
- `frontend/src/components/ArticleCard.tsx` — Add ChatPanel below comments
- `frontend/src/api/client.ts` — Add chat API types
- `.specify/memory/constitution.md` — Amendment 1.4.0

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | Chat uses the same persona prompts; direct LLM streaming (LangGraph not required for non-graph chat) |
| II. Expert Persona Integrity | PASS | Same personas, same prompts, same voices |
| III. Anti-AI-ism Voice | PASS | Same SYSTEM_RULES applied to chat responses |
| IV. Idempotent Processing | N/A | Chat is ephemeral, no persistence |
| V. Resilience | PASS | SSE errors handled gracefully, partial responses displayed |
| VII. Simplicity | PASS | One new endpoint, one new component, one small dependency |
| API Contract | AMENDMENT 1.4.0 | SSE streaming permitted for chat |

## Design

### Backend: SSE Streaming Endpoint

**Endpoint**: `POST /chat/stream`

**Request body**:
```json
{
  "article_id": 42,
  "messages": [
    {"role": "user", "content": "What do you think about..."},
    {"role": "assistant", "persona": "historian", "content": "..."},
    {"role": "assistant", "persona": "economist", "content": "..."},
    {"role": "assistant", "persona": "philosopher", "content": "..."},
    {"role": "user", "content": "But Maggie, don't you think..."}
  ]
}
```

**Processing flow**:
1. Look up article by ID — fetch title, full_text, and original panel comments from DB.
2. Parse the latest user message.
3. Detect persona mentions → determine response order.
4. For each persona in order:
   a. Build message list: system prompt (SYSTEM_RULES + persona prompt) + conversation history + current user message.
   b. Stream tokens via `ChatOpenAI.astream()`.
   c. Emit SSE events: `persona_start` → `token` (per chunk) → `persona_end`.
4. Emit `done` event.

**Persona mention detection**:
- Case-insensitive whole-word match for: "maggie", "tim", "sofia", "margaret", "timothy", "brennan", "chandrasekaran", "reyes"
- Map: maggie/margaret/chandrasekaran → historian, tim/timothy/brennan → economist, sofia/reyes → philosopher
- First mentioned gets position 0, second gets position 1, unmentioned gets position 2 (randomized among unmentioned if multiple).

**Context truncation**:
- If conversation exceeds 10 user messages, truncate to last 10 exchanges (user + all 3 assistant responses = 1 exchange).

### Frontend: ChatPanel Component

**State**:
- `messages: ChatMessage[]` — the full thread
- `isStreaming: boolean` — disables input during streaming
- `streamingResponses: Record<string, string>` — accumulates tokens per persona during streaming

**Rendering**:
- Chat appears inline within each ArticleCard, below the persona comments
- Collapsed by default — "Chat with the panel about this article..." link expands it
- User messages right-aligned, gray bubble
- Persona responses left-aligned with avatar, name label, persona color (reuse PERSONA_STYLES)
- Input bar at bottom with send button, disabled during streaming
- Auto-scroll to bottom on new content

**SSE consumption**:
- Use `fetch()` with `ReadableStream` to consume SSE (not EventSource, since we need POST)
- Parse SSE events from the stream
- On `persona_start`: add placeholder for new persona response
- On `token`: append to current persona's streaming response
- On `persona_end`: finalize persona response into messages array
- On `done`: re-enable input

### Conversation History Format for LLM

Each persona sees the conversation differently:
- System message: SYSTEM_RULES + their persona prompt + "You are in a live chat with a reader about a specific news article."
- First HumanMessage contains article title, truncated full text, and the panel's original comments as grounding context
- User messages map to HumanMessage
- Their own prior responses map to AIMessage (so the LLM sees its own continuity)
- Other personas' responses are included as context in the human message (similar to how prior comments work in article pipeline)

## Dependency

`sse-starlette` — lightweight SSE helper for Starlette/FastAPI. Provides `EventSourceResponse` that handles SSE formatting and keep-alive.

```
pip install sse-starlette
```
