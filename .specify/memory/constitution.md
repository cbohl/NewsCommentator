# News Commentator Constitution

## Core Principles

### I. LangGraph-First Orchestration

All expert commentary generation MUST be orchestrated through a LangGraph `StateGraph` with explicitly typed shared state (`TypedDict`). Each expert persona is a discrete graph node. No commentary logic shall live outside of the graph — nodes are the single source of truth for prompt execution, and the graph is the single source of truth for execution order.

### II. Expert Persona Integrity (NON-NEGOTIABLE)

Three expert personas are constitutionally defined. Their identities, analytical lenses, and negative constraints are immutable:

- **Historian**: Analyzes through historical precedents, 50–100 year cycles, and "Great Man" vs. "Social Forces" frameworks. MUST NEVER use the phrase "In the grand tapestry of history."
- **Economist**: Analyzes through incentives, resource scarcity, market impacts, and game theory. MUST NEVER give generic financial or investment advice.
- **Philosopher**: Analyzes through ethics, epistemology, and the human condition using a Socratic or Analytical style.

Adding, removing, or altering a persona requires a constitutional amendment.

### III. Anti-AI-ism Voice Standard (NON-NEGOTIABLE)

All generated commentary MUST:

- Be concise — hard maximum of 150 words per comment.
- Jump directly into analysis with zero introductory fluff.
- Never contain phrases: "In conclusion," "It is important to note," "As an AI," "It's worth noting," "Let's delve into," or equivalent filler.

Violation of these constraints is a build-quality failure. Prompt engineering must include explicit negative instructions enforcing this standard.

### IV. Idempotent Processing

Every article MUST be uniquely identified by its RSS GUID or canonical URL. The system SHALL check the SQLite database before processing and silently skip duplicates. No article may be commented on twice. This is enforced at the database layer via a UNIQUE constraint, not application logic alone.

### V. Resilience Over Availability

The LangGraph workflow MUST be wrapped in structured error handling. Failures during commentary generation SHALL be logged to a dedicated `error_log` table with full context (article URL, timestamp, error traceback) rather than crashing the FastAPI service. The system degrades gracefully — a single article failure never halts the hourly heartbeat.

### VI. Jina AI Reader for Extraction

Full-text article extraction MUST use the `https://r.jina.ai/{url}` prefixing method. No alternative scraping, headless browser, or ad-hoc HTML parsing is permitted. Jina Reader is the single sanctioned extraction mechanism.

### VII. Simplicity & Minimal Footprint

- SQLite is the only permitted database. No PostgreSQL, no external caches.
- APScheduler manages the hourly heartbeat. No Celery, no external task queues.
- The frontend is a single React (Vite) + Tailwind CSS application. No SSR frameworks, no additional CSS libraries.
- Maximum initial directory depth: 3 levels (e.g., `backend/app/nodes/`).
- YAGNI: do not build features, endpoints, or abstractions not explicitly required.

## Technology Stack (Locked)

| Layer           | Technology                   | Locked |
| --------------- | ---------------------------- | ------ |
| Backend API     | FastAPI                      | Yes    |
| Orchestration   | LangGraph (StateGraph)       | Yes    |
| ORM / Database  | SQLAlchemy + SQLite          | Yes    |
| Scheduling      | APScheduler                  | Yes    |
| Text Extraction | Jina AI Reader (`r.jina.ai`) | Yes    |
| Data Source     | Reuters RSS                  | Yes    |
| Frontend        | React (Vite) + Tailwind CSS  | Yes    |
| LLM Provider    | OpenAI (GPT-5-nano)          | Yes    |

Stack changes require a constitutional amendment with explicit rationale.

## Operational Standards

### Health & Observability

- A `/health` endpoint MUST exist and return the timestamp of the last successful processing run.
- All LangGraph node executions MUST be logged with structured metadata (article URL, node name, duration).
- The `error_log` table serves as the canonical failure audit trail.

### Data Flow Contract

The processing pipeline follows this immutable sequence:

1. **RSS Fetch** — Pull latest items from Reuters RSS feed.
2. **Deduplication** — Check each GUID/URL against SQLite; skip known articles.
3. **Extraction** — Retrieve full text via Jina AI Reader.
4. **LangGraph Execution** — Run Historian → Economist → Philosopher nodes sequentially against shared state.
5. **Persistence** — Store article + all three comments in SQLite.
6. **Error Handling** — Any failure at steps 3–5 logs to `error_log` and continues to the next article.

### API Contract

- All API responses use JSON.
- The frontend consumes a REST API served by FastAPI.
- No GraphQL, no WebSockets unless constitutionally amended.

## Governance

This constitution supersedes all ad-hoc decisions. Any specification, plan, or implementation that contradicts these principles is invalid until the constitution is amended.

### Amendment Process

Modifications require:

1. Explicit documentation of the rationale for change.
2. Review and approval by the project maintainer.
3. A backwards-compatibility assessment — existing data and APIs must not break.
4. An updated version number and amendment date below.

**Version**: 1.1.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-02-19

### Amendment Log

- **1.1.0 (2026-02-19)**: Changed LLM Provider from Claude (Anthropic API) to OpenAI (GPT-5-nano). Rationale: maintainer preference. No backwards-compatibility impact — no existing data depends on the LLM provider.
