# News Commentator Constitution

## Core Principles

### I. LangGraph-First Orchestration

All expert commentary generation MUST be orchestrated through a LangGraph `StateGraph` with explicitly typed shared state (`TypedDict`). Each expert persona is a discrete graph node. No commentary logic shall live outside of the graph — nodes are the single source of truth for prompt execution, and the graph is the single source of truth for execution order.

### II. Expert Persona Integrity (NON-NEGOTIABLE)

Three named expert personas are constitutionally defined. Their identities, personalities, analytical lenses, and negative constraints are immutable:

- **Dr. Margaret "Maggie" Chandrasekaran** — Historian. PhD, University of Chicago. Pessimistic, sharp, occasionally dismissive. Analyzes through historical precedents, long cycles, and forgotten parallels. MUST NEVER use the phrase "In the grand tapestry of history." Should not be mean — just pessimistic and sharp.
- **Dr. Timothy "Tim" Brennan** — Economist. PhD, London School of Economics. Optimistic, disagreeable, market-oriented. Cuts through narrative to economic mechanics. Pushes back on colleagues' positions. MUST NEVER give generic financial or investment advice. Disagreeableness should be witty, not hostile.
- **Sofia Reyes** — Philosopher. MA, Columbia University. Measured, curious, the youngest of the three. Gets at the deeper question nobody is asking. Identifies hidden assumptions and reframes conversations. Should not always ask questions — sometimes makes declarative arguments.

Adding, removing, or altering a persona requires a constitutional amendment.

### III. Anti-AI-ism Voice Standard (NON-NEGOTIABLE)

All generated commentary MUST:

- Be concise — hard maximum of 150 words per comment, but target 30–100 words. Only use the full 150 when the story truly demands it. A punchy one-liner is often stronger than a full paragraph.
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
| LLM Provider    | OpenAI (GPT-5.2)             | Yes    |
| Research Tools  | Tavily, Wikipedia, Yahoo Finance | Yes    |

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
4. **LangGraph Execution** — Run all three persona nodes sequentially in a randomized order against shared state. Later nodes may reference earlier nodes' comments.
5. **Persistence** — Store article + all three comments in SQLite.
6. **Error Handling** — Any failure at steps 3–5 logs to `error_log` and continues to the next article.

### API Contract

- All API responses use JSON.
- The frontend consumes a REST API served by FastAPI.
- No GraphQL, no WebSockets unless constitutionally amended.
- SSE (Server-Sent Events) is permitted for streaming responses (e.g., chat). SSE is uni-directional HTTP streaming, not a bidirectional protocol like WebSockets.

## Governance

This constitution supersedes all ad-hoc decisions. Any specification, plan, or implementation that contradicts these principles is invalid until the constitution is amended.

### Amendment Process

Modifications require:

1. Explicit documentation of the rationale for change.
2. Review and approval by the project maintainer.
3. A backwards-compatibility assessment — existing data and APIs must not break.
4. An updated version number and amendment date below.

**Version**: 1.6.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-02-26

### Amendment Log

- **1.1.0 (2026-02-19)**: Changed LLM Provider from Claude (Anthropic API) to OpenAI (GPT-5-nano). Rationale: maintainer preference. No backwards-compatibility impact — no existing data depends on the LLM provider.
- **1.2.0 (2026-02-20)**: Changed LangGraph execution from fixed order (Historian → Economist → Philosopher) to randomized order per article, with later nodes able to reference earlier comments. Rationale: creates more natural panel-discussion dynamics and varied output. No backwards-compatibility impact — existing stored comments are unaffected.
- **1.3.0 (2026-02-23)**: Replaced generic Historian/Economist/Philosopher personas with named characters — Dr. Margaret "Maggie" Chandrasekaran (Historian), Dr. Timothy "Tim" Brennan (Economist), and Sofia Reyes (Philosopher) — each with distinct personalities, credentials, and voice. Rationale: creates recognizable, distinct voices instead of interchangeable expert commentary. No backwards-compatibility impact — existing stored comments are unaffected.
- **1.3.1 (2026-02-23)**: Refined Article III voice standard — added target range of 30–100 words with max 150, encouraging short punchy responses. Rationale: LLMs default to filling the word limit; explicit shorter targets produce more natural length variation. No backwards-compatibility impact.
- **1.3.2 (2026-02-23)**: Upgraded LLM from GPT-5-nano to GPT-5.2. Rationale: larger model follows nuanced prompt instructions (length variation, personality, interaction rate) significantly better. No backwards-compatibility impact.
- **1.4.0 (2026-02-24)**: Added SSE (Server-Sent Events) as a permitted API transport for streaming chat responses. SSE is uni-directional HTTP streaming, distinct from WebSockets. The chat feature is ephemeral (no database persistence) and does not alter the existing article commentary pipeline. Rationale: enables real-time token-by-token streaming for interactive chat with the persona panel. No backwards-compatibility impact — existing REST endpoints are unchanged.
- **1.5.0 (2026-02-25)**: Added Tavily as the web search provider in the Technology Stack. Persona nodes in the hourly pipeline may optionally invoke Tavily web search via LangChain's tool-calling interface to ground commentary in real-world facts. Tool use is pipeline-only — the chat endpoint remains tool-free for latency reasons. Rationale: enables personas to look up specific facts, statistics, and context, producing higher-quality, more credible analysis. No backwards-compatibility impact — tool use is optional and the pipeline falls back gracefully if Tavily is unavailable.
- **1.6.0 (2026-02-26)**: Expanded search tools from Tavily-only to persona-specific tool sets. Historian (Maggie) gains Wikipedia access for historical facts, events, and biographical details. Economist (Tim) gains Yahoo Finance access for financial news and market data by ticker symbol. Philosopher (Sofia) retains Tavily only. Technology Stack row updated from "Web Search: Tavily" to "Research Tools: Tavily, Wikipedia, Yahoo Finance". Search metadata format changed from `list[str]` to `list[dict]` with source labels; backwards-compatible via Pydantic validator. RSS feeds diversified from BBC World-only to BBC World + BBC Business with random shuffling. Rationale: specialized tools aligned to each persona's expertise produce deeper, more credible analysis. No backwards-compatibility impact — old data is auto-converted by the API layer.
