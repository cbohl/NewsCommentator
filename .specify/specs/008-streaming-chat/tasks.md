# Tasks: Streaming Chat with the Panel

**Input**: `specs/008-streaming-chat/plan.md`

## Phase 1: Constitution

- [ ] T001 Amend constitution to version 1.4.0 — permit SSE streaming for chat in API Contract section, add amendment log entry

## Phase 2: Backend

- [ ] T002 Install `sse-starlette` dependency and add to `backend/requirements.txt`
- [ ] T003 Create `backend/app/routers/chat.py` with `POST /chat/stream` SSE endpoint accepting `article_id` + `messages`
- [ ] T004 Implement persona mention detection (case-insensitive whole-word match for names)
- [ ] T005 Implement streaming response generation using `ChatOpenAI.astream()` with same persona prompts, article context, and original panel comments
- [ ] T006 Implement conversation history formatting and truncation (last 10 exchanges)
- [ ] T007 Register chat router in `backend/app/main.py`

## Phase 3: Frontend

- [ ] T008 Add ChatMessage types to `frontend/src/api/client.ts`
- [ ] T009 Create `frontend/src/components/ChatPanel.tsx` — inline chat UI scoped to an article, with input, message display, SSE consumption
- [ ] T010 Implement SSE stream consumption via fetch + ReadableStream (POST-based, not EventSource)
- [ ] T011 Render persona responses with avatar, name, and color scheme (reuse PERSONA_STYLES)
- [ ] T012 Disable input during streaming, re-enable on `done` event
- [ ] T013 Integrate ChatPanel into `frontend/src/components/ArticleCard.tsx` below comments

## Phase 4: Validate

- [ ] T014 Test: send message with no persona mention → all three respond in random order, streaming
- [ ] T015 Test: send message mentioning "Maggie" → historian responds first
- [ ] T016 Test: multi-turn conversation maintains context
- [ ] T017 Test: page refresh clears chat thread
