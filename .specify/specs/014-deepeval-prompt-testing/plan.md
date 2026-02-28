# Implementation Plan: DeepEval Prompt Testing

**Branch**: `deepeval-prompt-testing` | **Date**: 2026-02-28 | **Spec**: `specs/014-deepeval-prompt-testing/spec.md`

## Summary

Add a DeepEval-based test suite that evaluates persona commentary quality against the constitution's voice standards. Four deterministic metrics (word count, forbidden phrases, bullet points, tool usage rate) catch hard violations without LLM calls. Three GEval metrics (persona voice, no-fluff openers, tool grounding) use an LLM judge for subjective quality. Tests run via pytest against real pipeline output.

## Technical Context

**Languages**: Python 3.12+
**New dependencies**: `deepeval` (dev only — not added to requirements.txt)
**New env vars**: None (DeepEval uses existing OPENAI_API_KEY for GEval judge)

**Files to create**:
- `backend/tests/conftest.py` — Fixtures: sample articles, pipeline invocation helper
- `backend/tests/metrics.py` — Custom deterministic `BaseMetric` subclasses
- `backend/tests/test_prompts.py` — Pytest test cases using DeepEval's `assert_test`

**Files NOT modified**:
- All production code unchanged — this is a test-only addition

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LangGraph-First | PASS | Tests invoke the existing graph nodes |
| II. Expert Persona Integrity | PASS | Tests validate persona voice |
| III. Anti-AI-ism Voice | PASS | Tests enforce word count + forbidden phrases |
| VII. Simplicity | PASS | Three files, one dev dependency |

## Design

### 1. Custom Deterministic Metrics (`backend/tests/metrics.py`)

Four `BaseMetric` subclasses that don't need an LLM judge:

```python
class WordCountMetric(BaseMetric):
    """Fail if comment exceeds 150 words."""
    def measure(self, test_case):
        count = len(test_case.actual_output.split())
        self.score = 1.0 if count <= 150 else 0.0
        self.reason = f"Word count: {count}/150"
        return self.score

class ForbiddenPhraseMetric(BaseMetric):
    """Fail if comment contains any forbidden phrase from system_rules.md."""
    PHRASES = [
        "In conclusion,", "It is important to note,", "As an AI,",
        "It's worth noting,", "Let's delve into,", "In today's world,",
        "This raises questions about", "This highlights",
        "In the grand tapestry of history",
    ]

class NoBulletPointsMetric(BaseMetric):
    """Fail if comment contains bullet points or numbered lists."""
    # Regex: lines starting with "- ", "* ", or "1. " etc.

class ToolUsageRateMetric(BaseMetric):
    """Fail if a persona used their tool on fewer than 50% of articles in the batch."""
    # Evaluated per-persona across all articles, not per test case.
    # The generate_comment helper returns (comment, searches) so we can track this.
    threshold = 0.5
```

### 2. GEval Metrics (in `test_prompts.py`)

Three `GEval` instances with custom evaluation criteria:

- **Persona Voice**: criteria describes the expected personality, tone, and analytical lens for each persona. Parameterized per persona.
- **No Fluff Opener**: criteria checks that the comment jumps straight into analysis without summarizing the article or using filler preambles.
- **Tool Grounding**: criteria checks that when a persona used a tool, the comment actually incorporates information from the tool results. Uses `retrieval_context` to pass the tool results to the judge.

```python
persona_voice_metric = GEval(
    name="Persona Voice",
    criteria="...",  # persona-specific
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.7,
)

tool_grounding_metric = GEval(
    name="Tool Grounding",
    criteria="Evaluate whether the commentary incorporates specific facts, "
             "figures, or details from the provided retrieval context (tool "
             "results). A high score means the author clearly used the research "
             "results — citing numbers, dates, names, or facts that appear in "
             "the context. A low score means the tool was called but its results "
             "were ignored.",
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT,
    ],
    threshold=0.7,
)
```

### 3. Test Harness (`backend/tests/conftest.py`)

Fixtures provide:
- `sample_articles`: 2-3 hardcoded article stubs (title + truncated text) covering different domains (geopolitical, economic, philosophical)
- `generate_comment(persona, article)`: Calls the persona's node function directly with a minimal `CommentaryState`, returns `(comment_text, search_queries)` tuple so tests can evaluate both output quality and tool usage

### 4. Test Cases (`backend/tests/test_prompts.py`)

Parameterized across personas × articles:

```python
@pytest.mark.parametrize("persona", ["historian", "economist", "philosopher"])
@pytest.mark.parametrize("article", SAMPLE_ARTICLES)
def test_persona_output(persona, article):
    comment, searches = generate_comment(persona, article)
    test_case = LLMTestCase(input=article["title"], actual_output=comment)
    assert_test(test_case, metrics=[
        WordCountMetric(), ForbiddenPhraseMetric(),
        NoBulletPointsMetric(), persona_voice_metrics[persona],
        no_fluff_metric,
    ])

@pytest.mark.parametrize("persona", ["historian", "economist", "philosopher"])
def test_tool_usage_rate(persona, all_results):
    """Check that each persona uses their tool on >= 50% of articles."""
    results = all_results[persona]  # list of (comment, searches) tuples
    used = sum(1 for _, searches in results if searches)
    metric = ToolUsageRateMetric(total=len(results), used=used)
    # ...

@pytest.mark.parametrize("persona", ["historian", "economist", "philosopher"])
@pytest.mark.parametrize("article", SAMPLE_ARTICLES)
def test_tool_grounding(persona, article, all_results):
    """When a tool was used, check that the comment incorporates its results."""
    comment, searches = all_results[persona][article_idx]
    if not searches:
        pytest.skip("No tool used for this article")
    test_case = LLMTestCase(
        input=article["title"],
        actual_output=comment,
        retrieval_context=[str(s) for s in searches],  # tool results
    )
    assert_test(test_case, metrics=[tool_grounding_metric])
```

### 5. Running Tests

```bash
# All prompt tests
pytest backend/tests/test_prompts.py -v

# Deterministic only (no LLM judge cost)
pytest backend/tests/test_prompts.py -v -k "not geval"

# Single persona
pytest backend/tests/test_prompts.py -v -k "historian"
```

## Cost Considerations

- Deterministic metrics (word count, forbidden phrases, bullets): **$0** — pure string operations
- GEval metrics: **~$0.01–0.02 per test case** — one LLM judge call per metric per case
- Full suite (3 personas × 3 articles × 3 GEval metrics): **~27 judge calls ≈ $0.30–0.55**
- Pipeline calls to generate comments: **~$0.10–0.30 per persona** (same as normal pipeline)

## Backwards Compatibility

No impact — test-only addition. No production code changes.
