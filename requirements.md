# Project: News Commentator

## Core Stack

- Backend: FastAPI, LangGraph, SQLAlchemy (SQLite)
- Frontend: React (Vite) + Tailwind CSS
- Data: Reuters RSS + Jina AI Reader
- Orchestration: APScheduler (Hourly Heartbeat)

## 1. LangGraph Orchestration & State Spec

- **Shared State**: Define a `TypedDict` containing:
  - `article_title`: str
  - `article_text`: str
  - `article_url`: str
  - `historian_comment`: str
  - `economist_comment`: str
  - `philosopher_comment`: str
  - `error_flag`: bool

- **Node 1: Historian**
  - **Prompt**: Focus on historical precedents, 50-100 year cycles, and "The Great Man" vs. "Social Forces" theories.
  - **Negative Constraint**: Strictly avoid the phrase "In the grand tapestry of history."

- **Node 2: Economist**
  - **Prompt**: Focus on incentives, resource scarcity, market impacts, and game theory.
  - **Negative Constraint**: Avoid giving generic financial or investment advice.

- **Node 3: Philosopher**
  - **Prompt**: Focus on ethics, epistemology, and the human condition. Use a Socratic or Analytical style.

- **Global Expert Constraints**:
  - Each comment must be concise (max 150 words).
  - Avoid "AI-isms" like "In conclusion," "It is important to note," or "As an AI."
  - Jump directly into the analysis without introductory fluff.

## 2. Stability & Operational Specs (GitHub Spec Kit)

- **Idempotency**: Use RSS GUIDs/URLs to ensure no article is processed twice in the SQLite DB.
- **Resilience**: Wrap the LangGraph workflow in a try/except block. Log failures to an `error_log` table rather than crashing the FastAPI service.
- **Full-Text Extraction**: Must use `https://r.jina.ai/` prefixing for reliability.
- **Health Check**: Provide a `/health` endpoint showing the timestamp of the last successful processing.
