# News Commentator

### **[View Live Site](https://d1b6dhneso8mh0.cloudfront.net)**

An AI-powered expert commentary panel that analyzes breaking news through three distinct perspectives — a historian, an economist, and a philosopher. Each persona has a real name, credentials, personality, and voice. They comment on articles from BBC World News every hour, and readers can chat with them in real-time via streaming responses.

Built with **[GitHub SpecKit](https://github.com/speckit/speckit)** for spec-driven development, **[LangChain](https://www.langchain.com/) / [LangGraph](https://langchain-ai.github.io/langgraph/)** for AI orchestration, and **[Terraform](https://www.terraform.io/)** for infrastructure-as-code deployment on AWS.

## The Panel

|                                                           | Name                                     | Role        | Credentials                     |
| --------------------------------------------------------- | ---------------------------------------- | ----------- | ------------------------------- |
| <img src="frontend/public/avatars/maggie.png" width="60"> | **Dr. Margaret "Maggie" Chandrasekaran** | Historian   | PhD, University of Chicago      |
| <img src="frontend/public/avatars/tim.png" width="60">    | **Dr. Timothy "Tim" Brennan**            | Economist   | PhD, London School of Economics |
| <img src="frontend/public/avatars/sofia.png" width="60">  | **Sofia Reyes**                          | Philosopher | MA, Columbia University         |

Maggie is pessimistic and sharp — she finds the historical parallel nobody remembers. Tim is optimistic and disagreeable — he cuts through narrative to the economic mechanics underneath. Sofia is measured and curious — she asks the question nobody in the article is asking.

They comment in a randomized order on each article. Later panelists can see (and respond to) earlier comments, creating natural panel dynamics.

## Features

- **Automated commentary pipeline** — fetches BBC World News via RSS every hour, extracts full text via Jina AI Reader, and generates three expert commentaries per article
- **Distinct AI personas** — each panelist has a unique voice, worldview, and interaction style, enforced through detailed character prompts with few-shot examples
- **Interactive chat** — readers can chat with the panel about any article via SSE streaming. Mention a panelist by name and they respond first
- **Server-side length control** — response length tiers (SHORT/MEDIUM/LONG) are selected randomly by the server and injected into prompts, producing natural variation instead of uniformly long responses
- **Spec-driven development** — every feature is specified, planned, and tracked through GitHub SpecKit before implementation

## Lessons Learned: Making AI Sound Human

Getting three AI personas to sound like real people instead of LLM outputs was an interesting challenge. A few techniques that made the biggest difference:

- **Server-side length control** — Early versions asked the LLM to self-regulate response length ("use SHORT ~30% of the time"). It didn't work — the model ignored probabilistic instructions and wrote long responses every time. The fix was structured generation: Python selects the tier via `random.choices`, then injects a direct command like `"YOUR ASSIGNED LENGTH: SHORT (15–40 words)"` at the end of the user message (exploiting recency bias). Length control moved from an unreliable prompt suggestion to a deterministic code decision.
- **Randomized execution order via LangGraph** — Each article's commentary runs through a LangGraph `StateGraph` where the three persona nodes execute sequentially, but the order is shuffled per article. Later nodes see earlier comments in the shared state, so the conversation dynamics change naturally — who responds to whom varies every time.
- **Anti-pattern rule** — The model fell into a rut of opening every response with "[Name]'s right, but..." which made the conversation feel templated. Adding "Do NOT start your response with a colleague's name" to the prompt broke the pattern and forced more varied rhetorical approaches.

## Architecture

```
BBC RSS ─→ Jina AI Reader ─→ LangGraph (3 persona nodes) ─→ SQLite
                                        │
                              FastAPI ←──┘
                                │
                    CloudFront (CDN) ─→ React + Tailwind
```

- **Backend**: FastAPI + LangGraph + SQLAlchemy + SQLite
- **Frontend**: React 19 + TypeScript + Tailwind CSS 4 + Vite 7
- **LLM**: OpenAI GPT-5.2
- **Infrastructure**: Terraform → AWS (EC2 + S3 + CloudFront)
- **Extraction**: Jina AI Reader
- **Scheduling**: APScheduler (hourly heartbeat)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env with your API key
echo "OPENAI_API_KEY=sk-..." > .env

# Start the server (auto-reloads on changes)
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. The pipeline triggers automatically every hour, or manually:

```bash
curl -X POST "http://localhost:8000/trigger?limit=3"
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

## Deployment

Infrastructure is managed with Terraform on AWS:

```bash
cd infra
terraform init
terraform apply -var="key_name=your-key" -var="openai_api_key=sk-..."
```

Deploy application code:

```bash
SSH_KEY_PATH=~/.ssh/your-key.pem ./deploy.sh
```

This rsyncs the backend to EC2, builds the frontend, uploads to S3, and invalidates the CloudFront cache.

## Spec-Driven Development

All features are developed through GitHub SpecKit's spec → plan → tasks workflow. Specifications live in `.specify/specs/`:

| Spec                    | Feature                                    | Status   |
| ----------------------- | ------------------------------------------ | -------- |
| 001-news-commentator    | MVP — pipeline + API + frontend            | Complete |
| 002-prompt-refinement   | Natural voice, anti-AI filler              | Complete |
| 003-persona-interaction | Randomized order, inter-persona commentary | Complete |
| 004-aws-terraform       | Infrastructure as Code                     | Complete |
| 005-persona-identity    | Named personas with distinct personalities | Complete |
| 006-ui-polish           | Avatars, display order, layout             | Complete |
| 007-model-upgrade       | GPT-5.2, server-side length tiers          | Complete |
| 008-streaming-chat      | Per-article SSE streaming chat             | Complete |

The project is governed by a [constitution](.specify/memory/constitution.md) that locks core architectural decisions and requires amendments for changes.

## License

MIT
