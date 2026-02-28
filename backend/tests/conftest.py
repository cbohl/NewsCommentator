import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env from backend/ so OPENAI_API_KEY and TAVILY_API_KEY are available
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Ensure backend/app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.graph.nodes import (  # noqa: E402
    ECONOMIST_PROMPT,
    HISTORIAN_PROMPT,
    PHILOSOPHER_PROMPT,
    PERSONA_TEMPERATURES,
    SEARCH_INSTRUCTIONS,
    SYSTEM_RULES,
    _invoke_with_tools,
    _make_length_reminder,
)

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402

PERSONA_PROMPTS = {
    "historian": HISTORIAN_PROMPT,
    "economist": ECONOMIST_PROMPT,
    "philosopher": PHILOSOPHER_PROMPT,
}

SAMPLE_ARTICLES = [
    {
        "id": "geopolitical",
        "title": "NATO Allies Agree to Boost Defence Spending Amid Rising Tensions with Russia",
        "text": (
            "NATO member states have unanimously agreed to increase their defence "
            "budgets to at least 3% of GDP by 2030, up from the previous 2% target "
            "set in 2014. The decision comes after months of heightened tensions along "
            "NATO's eastern border, with Russian military exercises near the Baltic "
            "states and increased naval activity in the North Sea. US Secretary of "
            "Defence announced that Washington would deploy an additional 5,000 troops "
            "to Poland as part of the alliance's enhanced forward presence. European "
            "leaders emphasized that the spending increase would focus on joint "
            "procurement of advanced weapons systems and cyber defence capabilities. "
            "Critics argue the spending hike could divert resources from social "
            "programmes at a time of economic uncertainty across Europe."
        ),
    },
    {
        "id": "economic",
        "title": "Federal Reserve Holds Interest Rates Steady as Inflation Cools to 2.3%",
        "text": (
            "The Federal Reserve voted to keep the benchmark interest rate unchanged "
            "at 4.25-4.50% at its latest meeting, citing progress on inflation that "
            "has cooled from a peak of 9.1% in June 2022 to 2.3% in the most recent "
            "reading. Fed Chair Jerome Powell signalled that rate cuts could begin in "
            "the second half of the year if inflation continues its downward trajectory. "
            "Markets rallied on the news, with the S&P 500 gaining 1.2% and the Nasdaq "
            "climbing 1.8%. However, Powell cautioned that the labour market remains "
            "tight, with unemployment at 3.7%, and that wage growth of 4.1% year-over-year "
            "could keep services inflation elevated. Bond yields fell as traders priced "
            "in a greater probability of a September rate cut."
        ),
    },
    {
        "id": "philosophical",
        "title": "Supreme Court Rules AI-Generated Art Cannot Be Copyrighted",
        "text": (
            "In a landmark 6-3 decision, the Supreme Court ruled that works generated "
            "entirely by artificial intelligence without meaningful human creative input "
            "cannot receive copyright protection under US law. The majority opinion, "
            "written by Justice Roberts, held that copyright law's requirement of human "
            "authorship is a constitutional prerequisite, not merely a statutory one. "
            "The case arose when an AI company sought to copyright a series of images "
            "created by its generative model with minimal human prompting. Dissenting "
            "justices argued the ruling could stifle innovation in AI-assisted creative "
            "industries. Tech companies warned the decision creates uncertainty about "
            "ownership of AI-assisted works where humans and machines collaborate. "
            "Legal scholars say the ruling could push Congress to create new legislation "
            "specifically addressing AI-generated content."
        ),
    },
]


def generate_comment(persona: str, article: dict) -> tuple[str, list[dict]]:
    """Run a single persona node against an article, return (comment, searches)."""
    prompt = PERSONA_PROMPTS[persona]
    temperature = PERSONA_TEMPERATURES[persona]

    user_msg = (
        f"Article Title: {article['title']}\n\n"
        f"Article Text:\n{article['text'][:3000]}"
    )

    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + prompt),
        HumanMessage(content=user_msg + _make_length_reminder()),
    ]

    comment, searches = _invoke_with_tools(
        messages, temperature=temperature, persona=persona
    )
    return comment, searches


@pytest.fixture(scope="session")
def all_results() -> dict[str, list[tuple[str, list[dict]]]]:
    """Generate comments for all personas × articles once per test session.

    Returns: {persona: [(comment, searches), ...]} with one entry per article.
    """
    results: dict[str, list[tuple[str, list[dict]]]] = {}
    for persona in ("historian", "economist", "philosopher"):
        results[persona] = []
        for article in SAMPLE_ARTICLES:
            comment, searches = generate_comment(persona, article)
            results[persona].append((comment, searches))
    return results
