import json
import logging
import random
import re
from typing import AsyncGenerator

from ..graph.nodes import _clean_response

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from ..database import get_db
from ..graph.nodes import (
    ECONOMIST_PROMPT,
    HISTORIAN_PROMPT,
    PHILOSOPHER_PROMPT,
    SYSTEM_RULES,
    _get_llm,
    select_length_tier,
)
from ..models import Article

logger = logging.getLogger(__name__)

router = APIRouter()

# Name → persona mapping for mention detection
NAME_TO_PERSONA: dict[str, str] = {
    "maggie": "historian",
    "margaret": "historian",
    "chandrasekaran": "historian",
    "tim": "economist",
    "timothy": "economist",
    "brennan": "economist",
    "sofia": "philosopher",
    "reyes": "philosopher",
}

PERSONA_PROMPTS = {
    "historian": HISTORIAN_PROMPT,
    "economist": ECONOMIST_PROMPT,
    "philosopher": PHILOSOPHER_PROMPT,
}

PERSONA_LABELS = {
    "historian": "Maggie (Historian)",
    "economist": "Tim (Economist)",
    "philosopher": "Sofia (Philosopher)",
}

ALL_PERSONAS = ["historian", "economist", "philosopher"]

CHAT_SUFFIX = (
    "\n\nYou are in a live chat with a reader about a specific news article. "
    "Keep the same voice and personality you use on the panel. Be conversational "
    "— this is a dialogue, not a monologue. The reader may address you or your "
    "colleagues by name.\n\n"
    "IMPORTANT: You have NO tools in this chat. Do NOT output tool calls, JSON, "
    "search queries, or any text like 'Researched:', 'Searching...', or "
    "'{\"query\":...}'. Just respond naturally in plain text."
)


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    persona: str | None = None
    content: str


class ChatRequest(BaseModel):
    article_id: int
    messages: list[ChatMessage]


def detect_persona_order(text: str) -> list[str]:
    """Determine persona response order based on name mentions in text."""
    text_lower = text.lower()
    seen: set[str] = set()

    # Find all name matches with their positions
    matches: list[tuple[int, str]] = []
    for name, persona in NAME_TO_PERSONA.items():
        for match in re.finditer(rf"\b{re.escape(name)}\b", text_lower):
            if persona not in seen:
                matches.append((match.start(), persona))
                seen.add(persona)

    # Sort by position in text
    matches.sort(key=lambda x: x[0])
    mentioned = [persona for _, persona in matches]

    # Add remaining personas in random order
    remaining = [p for p in ALL_PERSONAS if p not in mentioned]
    random.shuffle(remaining)
    mentioned.extend(remaining)

    return mentioned


def build_chat_messages(
    persona: str,
    article_title: str,
    article_text: str,
    initial_comments: dict[str, str],
    conversation: list[ChatMessage],
) -> list[SystemMessage | HumanMessage | AIMessage]:
    """Build LLM message list for a persona in article-scoped chat."""
    system_content = SYSTEM_RULES + PERSONA_PROMPTS[persona] + CHAT_SUFFIX
    msgs: list[SystemMessage | HumanMessage | AIMessage] = [
        SystemMessage(content=system_content)
    ]

    # Provide article context + original panel comments as the opening context
    article_context = (
        f"Article: {article_title}\n\n"
        f"{article_text[:3000]}\n\n"
        "---\n"
        "The panel's original comments on this article:\n\n"
    )
    for p in ALL_PERSONAS:
        if p in initial_comments:
            label = PERSONA_LABELS[p]
            article_context += f"{label}: {_clean_response(initial_comments[p])}\n\n"

    msgs.append(HumanMessage(content=article_context))
    msgs.append(AIMessage(content="[Panel discussion ready. Waiting for reader questions.]"))

    # Truncate to last 10 user messages worth of context
    user_indices = [i for i, m in enumerate(conversation) if m.role == "user"]
    if len(user_indices) > 10:
        start_idx = user_indices[-10]
        conversation = conversation[start_idx:]

    for msg in conversation:
        if msg.role == "user":
            msgs.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            if msg.persona == persona:
                msgs.append(AIMessage(content=msg.content))
            else:
                label = PERSONA_LABELS.get(msg.persona, msg.persona or "Unknown")
                msgs.append(
                    HumanMessage(content=f"[{label} said]: {msg.content}")
                )

    # Append length tier as final instruction (recency bias)
    tier = select_length_tier()
    msgs.append(HumanMessage(content=f"[INSTRUCTION] {tier} Do NOT start your response with a colleague's name."))

    return msgs


async def stream_chat(
    article_title: str,
    article_text: str,
    initial_comments: dict[str, str],
    conversation: list[ChatMessage],
) -> AsyncGenerator[dict, None]:
    """Generate SSE events for a chat response from all three personas."""
    latest_user_msg = ""
    for msg in reversed(conversation):
        if msg.role == "user":
            latest_user_msg = msg.content
            break

    order = detect_persona_order(latest_user_msg)
    logger.info("Chat response order: %s", " → ".join(order))

    llm = _get_llm()

    for persona in order:
        yield {"event": "persona_start", "data": json.dumps({"persona": persona})}

        chat_msgs = build_chat_messages(
            persona, article_title, article_text, initial_comments, conversation
        )
        full_response = ""

        async for chunk in llm.astream(chat_msgs):
            token = chunk.content
            if token:
                full_response += token
                yield {
                    "event": "token",
                    "data": json.dumps({"persona": persona, "token": token}),
                }

        yield {"event": "persona_end", "data": json.dumps({"persona": persona})}

        # Add this persona's response to conversation for next persona's context
        conversation = list(conversation) + [
            ChatMessage(role="assistant", persona=persona, content=full_response)
        ]

    yield {"event": "done", "data": json.dumps({})}


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == request.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Gather the original panel comments keyed by persona
    initial_comments = {c.persona: c.text for c in article.comments}

    return EventSourceResponse(
        stream_chat(
            article_title=article.title,
            article_text=article.full_text,
            initial_comments=initial_comments,
            conversation=request.messages,
        )
    )
