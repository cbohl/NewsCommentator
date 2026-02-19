# Tasks: News Commentator MVP

**Input**: Design documents from `.specify/specs/001-news-commentator/`
**Prerequisites**: plan.md (required), spec.md (required)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = View Commentary, US2 = Automated Processing, US3 = Health Monitoring

---

## Phase 1: Setup

**Purpose**: Project scaffolding and dependency installation

- [ ] T001 Create `backend/` directory structure per plan (`app/`, `app/graph/`, `app/services/`, `app/routers/`)
- [ ] T002 [P] Create `backend/requirements.txt` with pinned dependencies: fastapi, uvicorn, sqlalchemy, apscheduler, httpx, feedparser, langgraph, langchain-anthropic, python-dotenv
- [ ] T003 [P] Create `backend/.env.example` with `ANTHROPIC_API_KEY=` placeholder
- [ ] T004 [P] Scaffold `frontend/` with Vite + React + TypeScript (`npm create vite@latest`)
- [ ] T005 [P] Install Tailwind CSS in frontend and configure `tailwind.config.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database, FastAPI app shell, and shared state — blocks all user stories

- [ ] T006 [US2] Implement `backend/app/database.py` — SQLAlchemy engine, `SessionLocal`, `Base`, `create_all()` for SQLite
- [ ] T007 [US2] Implement `backend/app/models.py` — `Article` (id, guid UNIQUE, url UNIQUE, title, full_text, created_at), `Comment` (id, article_id FK, persona, text, created_at), `ErrorLog` (id, article_url, error_message, traceback, created_at)
- [ ] T008 [US2] Implement `backend/app/graph/state.py` — `CommentaryState` TypedDict with all 7 fields
- [ ] T009 Implement `backend/app/main.py` — FastAPI app with lifespan, include routers, call `create_all()` on startup

**Checkpoint**: Backend starts with `uvicorn backend.app.main:app`, database tables created, no routes yet

---

## Phase 3: User Story 2 — Automated Hourly Processing (Priority: P1)

**Goal**: The full pipeline: RSS → dedup → extract → LangGraph → persist → error handling

**Independent Test**: Trigger the pipeline manually; verify articles + comments appear in SQLite

### Implementation

- [ ] T010 [US2] Implement `backend/app/services/rss.py` — fetch and parse Reuters RSS feed via `feedparser`, return list of dicts with `guid`, `url`, `title`
- [ ] T011 [US2] Implement `backend/app/services/extractor.py` — fetch full text via `https://r.jina.ai/{url}` using `httpx`, return extracted text
- [ ] T012 [US2] Implement `backend/app/graph/nodes.py` — three node functions (`historian_node`, `economist_node`, `philosopher_node`), each calling Anthropic API with persona prompt + negative constraints + Anti-AI-ism rules
- [ ] T013 [US2] Implement `backend/app/graph/workflow.py` — assemble `StateGraph` with three nodes in sequence, compile graph
- [ ] T014 [US2] Implement `backend/app/services/pipeline.py` — `process_new_articles()`: fetch RSS → check DB for duplicates → extract text → run graph → persist Article + 3 Comments → catch exceptions to `error_log`
- [ ] T015 [US2] Add APScheduler to `backend/app/main.py` lifespan — `BackgroundScheduler` calling `process_new_articles()` every 60 minutes
- [ ] T016 [US2] Add `POST /trigger` dev endpoint in `backend/app/routers/articles.py` for manual pipeline runs

**Checkpoint**: Start backend, call `POST /trigger`, verify articles and comments in SQLite, verify duplicate skip on re-trigger, verify error_log on simulated failure

---

## Phase 4: User Story 1 — View Expert Commentary (Priority: P1)

**Goal**: REST API serving articles + comments, and the frontend to display them

**Independent Test**: Load the frontend in a browser, see articles with three expert comments each

### Backend API

- [ ] T017 [US1] Implement `backend/app/schemas.py` — Pydantic models: `CommentOut`, `ArticleOut` (with nested list of `CommentOut`), `ArticleListOut`
- [ ] T018 [US1] Implement `backend/app/routers/articles.py` — `GET /articles` (paginated, reverse-chronological), `GET /articles/{id}` (single article with comments)
- [ ] T019 [US1] Add CORS middleware to `backend/app/main.py` for frontend dev server

### Frontend

- [ ] T020 [P] [US1] Implement `frontend/src/api/client.ts` — fetch wrapper for `GET /articles`
- [ ] T021 [P] [US1] Implement `frontend/src/components/Layout.tsx` — page shell with header ("News Commentator"), container
- [ ] T022 [US1] Implement `frontend/src/components/CommentBlock.tsx` — renders persona label + comment text, styled per persona
- [ ] T023 [US1] Implement `frontend/src/components/ArticleCard.tsx` — renders article title, source link, and three `CommentBlock` components
- [ ] T024 [US1] Implement `frontend/src/pages/Home.tsx` — fetches articles from API, renders list of `ArticleCard`
- [ ] T025 [US1] Wire `App.tsx` and `main.tsx` — mount `Home` page inside `Layout`

**Checkpoint**: Run backend + frontend, homepage shows articles with Historian/Economist/Philosopher comments

---

## Phase 5: User Story 3 — Health Monitoring (Priority: P2)

**Goal**: `/health` endpoint for operational monitoring

- [ ] T026 [US3] Implement `backend/app/routers/health.py` — `GET /health` returns `{"status": "ok", "last_successful_run": "<ISO timestamp or null>"}`
- [ ] T027 [US3] Ensure `pipeline.py` updates a `last_successful_run` timestamp on successful batch completion (can use a simple module-level variable or a metadata table)

**Checkpoint**: Call `GET /health`, see correct timestamp after a pipeline run

---

## Phase 6: Polish

- [ ] T028 [P] Verify all three persona prompts comply with Constitution II and III (review negative constraints, word limits)
- [ ] T029 [P] Test idempotency: run pipeline twice with same RSS data, confirm zero duplicates
- [ ] T030 [P] Test resilience: simulate Jina extraction failure, confirm error_log entry and remaining articles still process
- [ ] T031 Verify frontend responsive layout on mobile viewport

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US2 - Pipeline)**: Depends on Phase 2
- **Phase 4 (US1 - Frontend + API)**: Depends on Phase 2; enhanced by Phase 3 having data in DB
- **Phase 5 (US3 - Health)**: Depends on Phase 2; references pipeline from Phase 3
- **Phase 6 (Polish)**: Depends on Phases 3, 4, 5

### Parallel Opportunities

- T002, T003, T004, T005 all run in parallel (Phase 1)
- T020, T021 run in parallel (different frontend files)
- T028, T029, T030 run in parallel (independent validation checks)
- Phase 3 and Phase 4 backend API (T017-T019) can overlap once Phase 2 is done

### Implementation Strategy

1. Complete Phase 1 + 2 → Backend boots, DB ready
2. Complete Phase 3 → Pipeline populates data
3. Complete Phase 4 → Full stack working end-to-end
4. Complete Phase 5 → Operational endpoint
5. Complete Phase 6 → Verification pass
