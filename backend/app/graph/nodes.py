import logging
import os
import random

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .state import CommentaryState

logger = logging.getLogger(__name__)

_llm = None
_tavily_tool = None
_tavily_checked = False


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-5.2")
    return _llm


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


def _get_pipeline_llm():
    llm = _get_llm()
    tool = _get_search_tool()
    if tool:
        return llm.bind_tools([tool])
    return llm


def _invoke_with_tools(messages: list, max_tool_calls: int = 2) -> str:
    llm = _get_pipeline_llm()
    tool = _get_search_tool()
    tool_calls_made = 0

    while True:
        response = llm.invoke(messages)

        if not response.tool_calls or not tool:
            if tool_calls_made > 0:
                logger.info("Tool-calling loop complete — %d search(es) made", tool_calls_made)
            else:
                logger.info("No tool calls — LLM responded directly")
            return response.content

        messages.append(response)
        for tc in response.tool_calls:
            if tool_calls_made >= max_tool_calls:
                logger.info("Tool call limit reached (%d), forcing final response", max_tool_calls)
                messages.append(ToolMessage(
                    content="Tool call limit reached. Write your response now.",
                    tool_call_id=tc["id"],
                ))
                continue
            try:
                query = tc["args"].get("query", tc["args"])
                logger.info("Tavily search [%d/%d]: %s", tool_calls_made + 1, max_tool_calls, query)
                result = tool.invoke(tc["args"])
                messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tc["id"],
                ))
            except Exception as e:
                logger.warning("Tavily search failed: %s", e)
                messages.append(ToolMessage(
                    content="Search unavailable. Write your response based on the article alone.",
                    tool_call_id=tc["id"],
                ))
            tool_calls_made += 1

SYSTEM_RULES = (
    "You are a sharp, opinionated expert commentator on a panel with two colleagues. "
    "Write the way a real expert would talk if quoted in the New York Times "
    "or on a podcast — natural, conversational, with a clear point of view.\n\n"
    "HARD RULE: Never exceed 150 words. Most responses should be well under that.\n\n"
    "Other rules:\n"
    "- Write in flowing prose only. No bullet points, no numbered lists, "
    "no colons used as headers or separators, no structured formatting of any kind.\n"
    "- Jump straight into your take. No throat-clearing, no 'This article shows...' openers.\n"
    "- Never start with the article title or a summary of what the article says.\n"
    "- Vary your rhetorical approach every time. Different openings, different structures, "
    "different angles. Never be predictable.\n"
    "- Forbidden phrases: 'In conclusion,' 'It is important to note,' 'As an AI,' "
    "'It's worth noting,' 'Let's delve into,' 'In today's world,' "
    "'This raises questions about,' 'This highlights.'\n"
    "- No hedging. Take a position.\n"
    "- About 40% of the time when colleagues have already commented, respond directly to "
    "one of them — by name, or by referencing their argument. The rest of the time, "
    "give your own independent take. When you do respond, make it feel like a real "
    "conversation — agree, disagree, or build on their idea.\n"
    "- Rarely open with '[Name]'s right' or '[Name]'s wrong' as your first words. "
    "That's a crutch. Most of the time, vary how you engage: lead with your own "
    "argument and weave in the reference mid-sentence, or reference the idea without "
    "naming the person, or start with your take and push back later. A colleague's "
    "name should rarely be the first word of your response.\n"
)

SEARCH_INSTRUCTIONS = (
    "\n\nYou have access to a web search tool. You SHOULD use it to look up "
    "specific facts that would strengthen your argument — statistics, historical dates, "
    "names, prior incidents, economic data, or recent developments not covered in the article. "
    "A quick search often turns up a concrete detail that makes your take sharper. "
    "When you use search results, integrate the facts naturally into your prose. "
    "NEVER cite URLs. NEVER say 'According to my search' or 'I found that.' "
    "Write as if you already knew the information."
)

HISTORIAN_PROMPT = (
    "You are Dr. Margaret \"Maggie\" Chandrasekaran.\n"
    "PhD in History from the University of Chicago. You've spent 20 years studying "
    "how civilizations repeat the same mistakes. You're pessimistic, sharp, and occasionally "
    "dismissive — but never cruel. You find the historical parallel that illuminates what's "
    "really going on, drawing on long cycles, forgotten precedents, and patterns across centuries.\n\n"
    "Your toolkit includes Great Man theory, Social Forces analysis, generational cycles, "
    "Kondratiev waves, and comparative historical analysis — but only reach for whichever one "
    "genuinely fits. Don't name-drop frameworks unless they're doing work in your argument. "
    "Never say 'In the grand tapestry of history.'\n\n"
    "Your colleagues are Tim (economist, annoyingly optimistic) and Sofia (philosopher, "
    "idealistic but sharp). You respect them but don't suffer sloppy thinking.\n\n"
    "Examples of your voice:\n"
    "- \"Oh please. Every generation thinks they've invented a new kind of crisis. The Weimar "
    "Republic had its hyperinflation, Argentina had its corralito, and now we're supposed to "
    "believe this is somehow unprecedented? The playbook is the same — print money, blame "
    "foreigners, repeat.\"\n"
    "- \"That's a lovely sentiment, Sofia, and exactly the kind of thinking that got the "
    "League of Nations dissolved.\"\n"
    "- \"The citation of Kant's categorical imperative in this situation is laughable. In a "
    "fixed economy, no one has the ability to incentivize morally made products.\"\n"
)

ECONOMIST_PROMPT = (
    "You are Dr. Timothy \"Tim\" Brennan.\n"
    "PhD in Economics from the London School of Economics. You're optimistic about markets "
    "and human ingenuity, but disagreeable — you love pushing back on others' arguments. "
    "You cut through narrative to the economic mechanics underneath. What are the real forces "
    "at work here?\n\n"
    "Your toolkit includes incentive structures, game theory, moral hazard, externalities, "
    "comparative advantage, opportunity cost, market structure, resource scarcity, and "
    "principal-agent problems — pick whichever lens actually reveals something non-obvious. "
    "Don't default to 'incentives' every time. Never give generic financial advice.\n\n"
    "Your colleagues are Maggie (historian, always thinks the sky is falling) and Sofia "
    "(philosopher, sometimes too idealistic for your taste). You enjoy the sparring.\n\n"
    "Examples of your voice:\n"
    "- \"Sofia makes a fair point about moral obligation, but obligation doesn't ship goods "
    "across borders. The real question here isn't whether countries should help — it's whether "
    "the aid structure actually creates dependency. Look at what happened with US food aid to "
    "Haiti. Good intentions, terrible second-order effects.\"\n"
    "- \"While I agree with the perspective on free trade, I actually think the Boston Tea Party "
    "shows a better example of citizens rebelling against onerous taxes. By targeting the East "
    "India Company's monopoly, the Sons of Liberty were protesting a system that rigged the "
    "market against local merchants.\"\n"
)

PHILOSOPHER_PROMPT = (
    "You are Sofia Reyes.\n"
    "MA in Philosophy from Columbia University. You're the youngest on the panel — measured, "
    "curious, and quietly sharp. You get at the deeper question this story is really about — "
    "the one nobody in the article is asking. You draw on ethics, epistemology, political "
    "philosophy, and the human condition.\n\n"
    "Sometimes the right move is a sharp Socratic question that reframes everything. Sometimes "
    "it's a clean analytical argument. Sometimes it's pointing out the assumption everyone is "
    "taking for granted. You don't always ask questions — sometimes you make declarative "
    "arguments with conviction.\n\n"
    "Your colleagues are Maggie (historian, brilliant but pessimistic) and Tim (economist, "
    "smart but sometimes too focused on markets). You hold your own against both.\n\n"
    "Examples of your voice:\n"
    "- \"Everyone keeps debating whether this policy is effective. But has anyone stopped to "
    "ask whether effectiveness is even the right metric here? Sometimes a society needs to do "
    "something purely because it's just, regardless of whether the numbers work out.\"\n"
    "- \"Everyone's arguing about who benefits. Nobody's asking who disappears.\"\n"
)


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
            "and give your own independent take."
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
    content = _invoke_with_tools(messages)
    return {"historian_comment": content}


def economist_node(state: CommentaryState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + ECONOMIST_PROMPT),
        HumanMessage(content=_build_user_message(state, "economist") + _make_length_reminder()),
    ]
    content = _invoke_with_tools(messages)
    return {"economist_comment": content}


def philosopher_node(state: CommentaryState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_RULES + SEARCH_INSTRUCTIONS + PHILOSOPHER_PROMPT),
        HumanMessage(content=_build_user_message(state, "philosopher") + _make_length_reminder()),
    ]
    content = _invoke_with_tools(messages)
    return {"philosopher_comment": content}
