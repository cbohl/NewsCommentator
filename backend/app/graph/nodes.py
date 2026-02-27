import logging
import os
import random
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .state import CommentaryState

_PROMPT_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPT_DIR / name).read_text()

logger = logging.getLogger(__name__)

PERSONA_TEMPERATURES = {
    "historian": 1.2,
    "economist": 0.9,
    "philosopher": 0.8,
}

_llm_cache: dict[float, ChatOpenAI] = {}
_tavily_tool = None
_tavily_checked = False
_wikipedia_tool = None
_yahoo_finance_tool = None

# Tool name → display label for footnotes
TOOL_SOURCE_LABELS = {
    "tavily_search": "Web",
    "wikipedia": "Wikipedia",
    "yahoo_finance_news": "Yahoo Finance",
}


def _get_llm(temperature: float = 0.9) -> ChatOpenAI:
    if temperature not in _llm_cache:
        _llm_cache[temperature] = ChatOpenAI(model="gpt-5.2", temperature=temperature)
    return _llm_cache[temperature]


def _get_search_tool():
    global _tavily_tool, _tavily_checked
    if _tavily_checked:
        return _tavily_tool
    _tavily_checked = True
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY not set — personas will operate without web search")
        return None
    try:
        from langchain_tavily import TavilySearch
        _tavily_tool = TavilySearch(max_results=3)
    except Exception as e:
        logger.warning("Failed to initialize Tavily search: %s", e)
        return None
    return _tavily_tool


def _get_wikipedia_tool():
    global _wikipedia_tool
    if _wikipedia_tool is None:
        try:
            from langchain_community.tools import WikipediaQueryRun
            from langchain_community.utilities import WikipediaAPIWrapper
            _wikipedia_tool = WikipediaQueryRun(
                api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=2000)
            )
        except Exception as e:
            logger.warning("Failed to initialize Wikipedia tool: %s", e)
            return None
    return _wikipedia_tool


def _get_yahoo_finance_tool():
    global _yahoo_finance_tool
    if _yahoo_finance_tool is None:
        try:
            from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
            _yahoo_finance_tool = YahooFinanceNewsTool()
        except Exception as e:
            logger.warning("Failed to initialize Yahoo Finance tool: %s", e)
            return None
    return _yahoo_finance_tool


def _get_persona_tools(persona: str) -> list:
    if persona == "historian":
        wiki = _get_wikipedia_tool()
        return [wiki] if wiki else []
    elif persona == "economist":
        yf = _get_yahoo_finance_tool()
        return [yf] if yf else []
    else:  # philosopher
        tavily = _get_search_tool()
        return [tavily] if tavily else []


def _get_pipeline_llm(temperature: float = 0.9, persona: str = "philosopher"):
    llm = _get_llm(temperature)
    tools = _get_persona_tools(persona)
    if tools:
        return llm.bind_tools(tools), tools
    return llm, []


def _invoke_with_tools(messages: list, *, temperature: float = 0.9, persona: str, max_tool_calls: int = 2) -> tuple[str, list[dict]]:
    llm, tools = _get_pipeline_llm(temperature, persona)
    tools_by_name = {t.name: t for t in tools}
    tool_calls_made = 0
    search_queries: list[dict] = []

    while True:
        response = llm.invoke(messages)

        if not response.tool_calls or not tools:
            if tool_calls_made > 0:
                logger.info("Tool-calling loop complete — %d search(es) made", tool_calls_made)
            else:
                logger.info("No tool calls — LLM responded directly")
            return response.content, search_queries

        messages.append(response)
        for tc in response.tool_calls:
            tool_name = tc["name"]
            source_label = TOOL_SOURCE_LABELS.get(tool_name, tool_name)

            if tool_calls_made >= max_tool_calls:
                logger.info("Tool call limit reached (%d), forcing final response", max_tool_calls)
                messages.append(ToolMessage(
                    content="Tool call limit reached. Write your response now.",
                    tool_call_id=tc["id"],
                ))
                continue
            try:
                query = tc["args"].get("query", tc["args"])
                logger.info("%s search [%d/%d]: %s", source_label, tool_calls_made + 1, max_tool_calls, query)
                search_queries.append({"query": str(query), "source": source_label})
                tool = tools_by_name.get(tool_name)
                if tool is None:
                    raise ValueError(f"Unknown tool: {tool_name}")
                result = tool.invoke(tc["args"])
                logger.info("%s result: %s", source_label, str(result)[:500])
                messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tc["id"],
                ))
            except Exception as e:
                logger.warning("%s search failed: %s", source_label, e)
                messages.append(ToolMessage(
                    content="Search unavailable. Write your response based on the article alone.",
                    tool_call_id=tc["id"],
                ))
            tool_calls_made += 1

SYSTEM_RULES = _load_prompt("system_rules.md")
SEARCH_INSTRUCTIONS = _load_prompt("search_instructions.md")
HISTORIAN_PROMPT = _load_prompt("historian.md")
ECONOMIST_PROMPT = _load_prompt("economist.md")
PHILOSOPHER_PROMPT = _load_prompt("philosopher.md")


LENGTH_TIERS = {
    "SHORT": (
        "\n\nYOUR ASSIGNED LENGTH: SHORT (15–40 words). "
        "Write one or two punchy sentences. Do NOT exceed 40 words."
    ),
    "MEDIUM": (
        "\n\nYOUR ASSIGNED LENGTH: MEDIUM (50–90 words). "
        "Write a focused paragraph. Do NOT exceed 90 words."
    ),
    "LONG": (
        "\n\nYOUR ASSIGNED LENGTH: LONG (100–150 words). "
        "Develop a full argument. Do NOT exceed 150 words."
    ),
}


def select_length_tier() -> str:
    tier = random.choices(["SHORT", "MEDIUM", "LONG"], weights=[30, 50, 20], k=1)[0]
    return LENGTH_TIERS[tier]


PERSONA_LABELS = {
    "historian": "Maggie (Historian)",
    "economist": "Tim (Economist)",
    "philosopher": "Sofia (Philosopher)",
}

PERSONA_PROMPTS = {
    "historian": HISTORIAN_PROMPT,
    "economist": ECONOMIST_PROMPT,
    "philosopher": PHILOSOPHER_PROMPT,
}


def _get_prior_comments(state: CommentaryState, current_persona: str) -> str:
    parts = []
    for persona in ("historian", "economist", "philosopher"):
        if persona == current_persona:
            continue
        comment = state.get(f"{persona}_comment", "")
        if comment:
            parts.append(f"{PERSONA_LABELS[persona]}: {comment}")
    return "\n\n".join(parts)


def _build_user_message(state: CommentaryState, current_persona: str) -> str:
    msg = (
        f"Article Title: {state['article_title']}\n\n"
        f"Article Text:\n{state['article_text'][:3000]}"
    )
    prior = _get_prior_comments(state, current_persona)
    if prior:
        msg += (
            f"\n\n---\nYour colleagues have already weighed in:\n\n{prior}\n\n"
            "You may agree, disagree, or build on what they said — or ignore them entirely "
            "and give your own independent take. "
            "Do NOT open with the same words or phrasing your colleagues used."
        )
    return msg


def _make_length_reminder() -> str:
    """Build a length + format reminder to append to the user message (recency bias)."""
    tier = select_length_tier()
    return (
        f"\n\n---\n{tier}\n"
        "IMPORTANT: Do NOT start your response with a colleague's name. "
        "Lead with your own idea."
    )


def historian_node(state: CommentaryState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + HISTORIAN_PROMPT),
        HumanMessage(content=_build_user_message(state, "historian") + _make_length_reminder()),
    ]
    content, searches = _invoke_with_tools(messages, temperature=PERSONA_TEMPERATURES["historian"], persona="historian")
    return {"historian_comment": content, "historian_searches": searches}


def economist_node(state: CommentaryState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + ECONOMIST_PROMPT),
        HumanMessage(content=_build_user_message(state, "economist") + _make_length_reminder()),
    ]
    content, searches = _invoke_with_tools(messages, temperature=PERSONA_TEMPERATURES["economist"], persona="economist")
    return {"economist_comment": content, "economist_searches": searches}


def philosopher_node(state: CommentaryState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + PHILOSOPHER_PROMPT),
        HumanMessage(content=_build_user_message(state, "philosopher") + _make_length_reminder()),
    ]
    content, searches = _invoke_with_tools(messages, temperature=PERSONA_TEMPERATURES["philosopher"], persona="philosopher")
    return {"philosopher_comment": content, "philosopher_searches": searches}
