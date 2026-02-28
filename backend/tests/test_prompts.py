import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from .conftest import SAMPLE_ARTICLES
from .metrics import (
    ForbiddenPhraseMetric,
    NoBulletPointsMetric,
    ToolUsageRateMetric,
    WordCountMetric,
)

# ---------------------------------------------------------------------------
# GEval metric factories (deferred so OPENAI_API_KEY is loaded from .env first)
# ---------------------------------------------------------------------------

PERSONA_VOICE_CRITERIA = {
    "historian": (
        "The response should sound like a pessimistic, sharp historian who draws on "
        "historical precedents, long cycles, and forgotten parallels. She should "
        "reference specific historical events, eras, or figures. The tone should be "
        "intellectually dismissive or world-weary, never cheerful or optimistic. "
        "Score low if the response sounds generic, optimistic, or lacks any "
        "historical grounding."
    ),
    "economist": (
        "The response should sound like an optimistic, disagreeable economist who "
        "cuts through narrative to economic mechanics. He should reference market "
        "forces, incentive structures, or financial data. The tone should push back "
        "on other viewpoints with wit, not hostility. Score low if the response "
        "sounds generic, purely political, or lacks any economic analysis."
    ),
    "philosopher": (
        "The response should sound like a measured, curious young philosopher who "
        "gets at deeper questions others are not asking. She should identify hidden "
        "assumptions, reframe the debate, or draw on ethics and political philosophy. "
        "The tone should be thoughtful and probing. Score low if the response sounds "
        "like generic punditry without philosophical depth."
    ),
}

_geval_cache: dict[str, GEval] = {}


def _get_persona_voice_metric(persona: str) -> GEval:
    key = f"voice_{persona}"
    if key not in _geval_cache:
        _geval_cache[key] = GEval(
            name=f"PersonaVoice_{persona}",
            criteria=PERSONA_VOICE_CRITERIA[persona],
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=0.7,
        )
    return _geval_cache[key]


def _get_no_fluff_metric() -> GEval:
    if "no_fluff" not in _geval_cache:
        _geval_cache["no_fluff"] = GEval(
            name="NoFluffOpener",
            criteria=(
                "The response should jump straight into analysis or an argument. It must NOT "
                "open with a summary of the article, a restatement of the headline, or any "
                "throat-clearing phrase like 'This article shows...', 'The recent news about...', "
                "or 'It is clear that...'. The first sentence should contain an original claim, "
                "observation, or question. Score low if the opening is generic or summarizing."
            ),
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=0.7,
        )
    return _geval_cache["no_fluff"]


def _get_tool_grounding_metric() -> GEval:
    if "grounding" not in _geval_cache:
        _geval_cache["grounding"] = GEval(
            name="ToolGrounding",
            criteria=(
                "The response should incorporate specific facts, figures, or details from the "
                "provided retrieval context (research tool results). A high score means the "
                "author clearly used the research — citing numbers, dates, names, or facts "
                "that appear in the context. A low score means the tool was called but its "
                "results were ignored and the response contains no information traceable to "
                "the retrieval context."
            ),
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.RETRIEVAL_CONTEXT,
            ],
            threshold=0.7,
        )
    return _geval_cache["grounding"]


# ---------------------------------------------------------------------------
# Deterministic quality tests — parameterized across personas × articles
# ---------------------------------------------------------------------------

PERSONAS = ["historian", "economist", "philosopher"]


@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("article_idx", range(len(SAMPLE_ARTICLES)))
def test_word_count(persona, article_idx, all_results):
    comment, _ = all_results[persona][article_idx]
    article = SAMPLE_ARTICLES[article_idx]
    tc = LLMTestCase(
        input=article["title"],
        actual_output=comment,
        name=f"{persona}_{article['id']}_word_count",
    )
    assert_test(tc, [WordCountMetric()])


@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("article_idx", range(len(SAMPLE_ARTICLES)))
def test_forbidden_phrases(persona, article_idx, all_results):
    comment, _ = all_results[persona][article_idx]
    article = SAMPLE_ARTICLES[article_idx]
    tc = LLMTestCase(
        input=article["title"],
        actual_output=comment,
        name=f"{persona}_{article['id']}_forbidden",
    )
    assert_test(tc, [ForbiddenPhraseMetric()])


@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("article_idx", range(len(SAMPLE_ARTICLES)))
def test_no_bullet_points(persona, article_idx, all_results):
    comment, _ = all_results[persona][article_idx]
    article = SAMPLE_ARTICLES[article_idx]
    tc = LLMTestCase(
        input=article["title"],
        actual_output=comment,
        name=f"{persona}_{article['id']}_bullets",
    )
    assert_test(tc, [NoBulletPointsMetric()])


# ---------------------------------------------------------------------------
# GEval quality tests
# ---------------------------------------------------------------------------


@pytest.mark.geval
@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("article_idx", range(len(SAMPLE_ARTICLES)))
def test_persona_voice(persona, article_idx, all_results):
    comment, _ = all_results[persona][article_idx]
    article = SAMPLE_ARTICLES[article_idx]
    tc = LLMTestCase(
        input=article["title"],
        actual_output=comment,
        name=f"{persona}_{article['id']}_voice",
    )
    assert_test(tc, [_get_persona_voice_metric(persona)])


@pytest.mark.geval
@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("article_idx", range(len(SAMPLE_ARTICLES)))
def test_no_fluff_opener(persona, article_idx, all_results):
    comment, _ = all_results[persona][article_idx]
    article = SAMPLE_ARTICLES[article_idx]
    tc = LLMTestCase(
        input=article["title"],
        actual_output=comment,
        name=f"{persona}_{article['id']}_fluff",
    )
    assert_test(tc, [_get_no_fluff_metric()])


# ---------------------------------------------------------------------------
# Tool usage tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("persona", PERSONAS)
def test_tool_usage_rate(persona, all_results):
    """Each persona should use their tool on >= 50% of articles."""
    results = all_results[persona]
    total = len(results)
    used = sum(1 for _, searches in results if searches)
    tc = LLMTestCase(
        input=f"{persona} tool usage across {total} articles",
        actual_output=f"Used tool on {used}/{total} articles",
        name=f"{persona}_tool_usage_rate",
    )
    assert_test(tc, [ToolUsageRateMetric(total=total, used=used)])


@pytest.mark.geval
@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("article_idx", range(len(SAMPLE_ARTICLES)))
def test_tool_grounding(persona, article_idx, all_results):
    """When a tool was used, check that results are incorporated into the comment."""
    comment, searches = all_results[persona][article_idx]
    if not searches:
        pytest.skip(f"{persona} did not use a tool for article {article_idx}")
    article = SAMPLE_ARTICLES[article_idx]
    tc = LLMTestCase(
        input=article["title"],
        actual_output=comment,
        retrieval_context=[
            s.get("result_snippet", f"Query: {s['query']}") for s in searches
        ],
        name=f"{persona}_{article['id']}_grounding",
    )
    assert_test(tc, [_get_tool_grounding_metric()])
