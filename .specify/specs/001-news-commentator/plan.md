# Implementation Plan: News Commentator MVP

**Branch**: `001-news-commentator` | **Date**: 2026-02-19 | **Spec**: `specs/001-news-commentator/spec.md`
**Input**: Feature specification from `.specify/specs/001-news-commentator/spec.md`

## Summary

Build a full-stack news commentary system: a FastAPI backend orchestrates an hourly pipeline that fetches Reuters RSS articles, extracts full text via Jina AI Reader, generates three expert AI commentaries through a LangGraph StateGraph, and persists results to SQLite. A React + Tailwind frontend displays the article feed with commentaries.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript/JavaScript (ES2022)
**Primary Dependencies**: FastAPI, LangGraph, SQLAlchemy, APScheduler, httpx, langchain-anthropic | React 18, Vite 5, Tailwind CSS 3
**Storage**: SQLite via SQLAlchemy ORM
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Local development / single-server deployment
**Project Type**: Web application (backend + frontend)
**Constraints**: SQLite only, no external caches or queues, max 3-level directory depth

## Constitution Check

*GATE: Must pass before implementation.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | All commentary flows through `StateGraph` nodes |
| II. Expert Persona Integrity | PASS | Three personas with locked prompts and negative constraints |
| III. Anti-AI-ism Voice | PASS | Prompts include explicit negative instructions; 150-word max enforced |
| IV. Idempotent Processing | PASS | UNIQUE constraint on article URL/GUID in SQLite |
| V. Resilience Over Availability | PASS | try/except wrapping graph execution; failures go to `error_log` |
| VI. Jina AI Reader | PASS | Extraction uses `https://r.jina.ai/{url}` exclusively |
| VII. Simplicity | PASS | SQLite, APScheduler, no extras. Directory depth <= 3 |

## Project Structure

### Documentation

```text
.specify/
├── memory/
│   └── constitution.md
└── specs/
    └── 001-news-commentator/
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

### Source Code

```text
backend/
├── app/
│   ├── main.py              # FastAPI app, lifespan, scheduler setup
│   ├── models.py            # SQLAlchemy models: Article, Comment, ErrorLog
│   ├── database.py          # Engine, session, Base, create_all
│   ├── schemas.py           # Pydantic response models
│   ├── graph/
│   │   ├── state.py         # TypedDict shared state definition
│   │   ├── nodes.py         # Historian, Economist, Philosopher node functions
│   │   └── workflow.py      # StateGraph assembly and compilation
│   ├── services/
│   │   ├── rss.py           # Reuters RSS fetching + parsing
│   │   ├── extractor.py     # Jina AI Reader full-text extraction
│   │   └── pipeline.py      # End-to-end: fetch → dedup → extract → graph → persist
│   └── routers/
│       ├── articles.py      # GET /articles, GET /articles/{id}
│       └── health.py        # GET /health
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── api/
│   │   └── client.ts        # Axios/fetch wrapper for backend API
│   ├── components/
│   │   ├── ArticleCard.tsx   # Single article with 3 comment sections
│   │   ├── CommentBlock.tsx  # Single expert comment display
│   │   └── Layout.tsx        # Page shell, header, container
│   └── pages/
│       └── Home.tsx          # Article feed page
├── index.html
├── tailwind.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json
```

**Structure Decision**: Web app layout (`backend/` + `frontend/`) per Constitution VII. Max depth is 3 (e.g., `backend/app/graph/`). Each concern gets exactly one file — no premature splitting.

## Key Design Decisions

### LangGraph StateGraph

The shared state is a `TypedDict`:

```python
class CommentaryState(TypedDict):
    article_title: str
    article_text: str
    article_url: str
    historian_comment: str
    economist_comment: str
    philosopher_comment: str
    error_flag: bool
```

Nodes execute sequentially: `historian_node` → `economist_node` → `philosopher_node`. Each node calls the Anthropic API with its persona prompt, writes its comment to state, and returns the updated state. The graph is compiled once at startup.

### Prompt Design

Each persona prompt includes:
1. The persona's analytical lens (from Constitution II).
2. An explicit negative constraint block.
3. The global Anti-AI-ism rules (Constitution III) as system-level instructions.
4. A hard instruction: "Your response must be under 150 words. Jump directly into your analysis."

### Database Schema

- `articles` table: `id`, `guid` (UNIQUE), `url` (UNIQUE), `title`, `full_text`, `created_at`
- `comments` table: `id`, `article_id` (FK), `persona` (historian|economist|philosopher), `text`, `created_at`
- `error_log` table: `id`, `article_url`, `error_message`, `traceback`, `created_at`

### Scheduler

APScheduler `BackgroundScheduler` started in FastAPI lifespan. Runs `pipeline.process_new_articles()` every 60 minutes. Also exposes a `POST /trigger` endpoint (dev-only) for manual runs.

## Complexity Tracking

No constitution violations. No complexity exceptions needed.
