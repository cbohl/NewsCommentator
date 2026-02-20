from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .state import CommentaryState

llm = ChatOpenAI(model="gpt-5-nano")

SYSTEM_RULES = (
    "You are a concise expert commentator. Rules you MUST follow:\n"
    "- Your response MUST be under 150 words.\n"
    "- Jump directly into your analysis. No introductions.\n"
    "- NEVER use these phrases: 'In conclusion,' 'It is important to note,' "
    "'As an AI,' 'It's worth noting,' 'Let's delve into,' 'In today's world.'\n"
    "- Do not use filler or hedging language.\n"
)

HISTORIAN_PROMPT = (
    "You are a Historian. Analyze this news article through the lens of "
    "historical precedents, 50-100 year cycles, and the tension between "
    "'Great Man' theory and 'Social Forces' theory.\n\n"
    "CRITICAL: You must NEVER use the phrase 'In the grand tapestry of history.'\n"
)

ECONOMIST_PROMPT = (
    "You are an Economist. Analyze this news article through the lens of "
    "incentives, resource scarcity, market impacts, and game theory.\n\n"
    "CRITICAL: You must NEVER give generic financial or investment advice. "
    "No 'diversify your portfolio' or 'consult a financial advisor' language.\n"
)

PHILOSOPHER_PROMPT = (
    "You are a Philosopher working in the Socratic and Analytical traditions. "
    "Analyze this news article through the lens of ethics, epistemology, "
    "and the human condition. Ask probing questions when appropriate.\n"
)


def _build_user_message(state: CommentaryState) -> str:
    return (
        f"Article Title: {state['article_title']}\n\n"
        f"Article Text:\n{state['article_text'][:3000]}"
    )


def historian_node(state: CommentaryState) -> dict:
    response = llm.invoke([
        SystemMessage(content=SYSTEM_RULES + HISTORIAN_PROMPT),
        HumanMessage(content=_build_user_message(state)),
    ])
    return {"historian_comment": response.content}


def economist_node(state: CommentaryState) -> dict:
    response = llm.invoke([
        SystemMessage(content=SYSTEM_RULES + ECONOMIST_PROMPT),
        HumanMessage(content=_build_user_message(state)),
    ])
    return {"economist_comment": response.content}


def philosopher_node(state: CommentaryState) -> dict:
    response = llm.invoke([
        SystemMessage(content=SYSTEM_RULES + PHILOSOPHER_PROMPT),
        HumanMessage(content=_build_user_message(state)),
    ])
    return {"philosopher_comment": response.content}
