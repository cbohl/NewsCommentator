# Feature Specification: DeepEval Prompt Testing

**Feature Branch**: `deepeval-prompt-testing`
**Created**: 2026-02-27
**Status**: Draft
**Input**: User request: "I want prompt testing to improve the output. DeepEval is the right tool since it's Python-native and doesn't need node/npm."

## Constitution Amendment Required

None. This adds a development-time testing tool — no changes to the runtime pipeline, data model, API, or technology stack.

## Rationale

Prompt quality is currently validated by manually reading commentary output after pipeline runs. This is slow, subjective, and doesn't scale. DeepEval provides automated, repeatable evaluation of LLM output against defined quality criteria. By writing metrics that encode the constitution's voice standards (Article III) and persona integrity requirements (Article II), prompt changes can be regression-tested before deployment.

## Requirements

```json
[
  {
    "name": "Install DeepEval as Dev Dependency",
    "description": "System must include deepeval as a development dependency, and it should be installable via the existing backend venv, so that prompt tests can run without affecting production dependencies",
    "type": "infrastructure",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given the backend venv is activated, When `pip install deepeval` is run, Then deepeval is available for import",
      "Given deepeval is installed, When the production server starts, Then deepeval is NOT imported at runtime"
    ]
  },
  {
    "name": "Word Count Metric",
    "description": "System must evaluate that each comment respects the constitutional word count constraints (max 150 words, target 30–100), and it should implement a deterministic custom BaseMetric that counts words and scores pass/fail, so that prompt changes that cause verbosity regressions are caught automatically",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a comment with 80 words, When the word count metric evaluates it, Then the score is 1.0 (pass)",
      "Given a comment with 160 words, When the word count metric evaluates it, Then the score is 0.0 (fail)",
      "Given a comment with exactly 150 words, When the word count metric evaluates it, Then the score is 1.0 (pass)"
    ]
  },
  {
    "name": "Forbidden Phrase Metric",
    "description": "System must detect forbidden phrases listed in system_rules.md (Article III), and it should implement a deterministic custom BaseMetric that scans for exact phrase matches, so that AI-sounding filler is caught without needing an LLM judge",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a comment containing 'It is important to note', When the forbidden phrase metric evaluates it, Then the score is 0.0 (fail) and the reason identifies the phrase",
      "Given a comment containing 'It's worth noting', When the forbidden phrase metric evaluates it, Then the score is 0.0 (fail)",
      "Given a comment with no forbidden phrases, When the forbidden phrase metric evaluates it, Then the score is 1.0 (pass)"
    ]
  },
  {
    "name": "No Bullet Points Metric",
    "description": "System must detect bullet points, numbered lists, and structured formatting forbidden by system_rules.md, and it should implement a deterministic custom BaseMetric that scans for list markers, so that formatting violations are caught automatically",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a comment containing '- item one\\n- item two', When the formatting metric evaluates it, Then the score is 0.0 (fail)",
      "Given a comment containing '1. First point\\n2. Second point', When the formatting metric evaluates it, Then the score is 0.0 (fail)",
      "Given a comment in flowing prose with no list markers, When the formatting metric evaluates it, Then the score is 1.0 (pass)"
    ]
  },
  {
    "name": "Persona Voice Metric (GEval)",
    "description": "System must evaluate whether a comment sounds like its assigned persona, and it should use DeepEval's GEval metric with persona-specific evaluation criteria, so that prompt changes that dilute persona distinctiveness are detected",
    "type": "business_logic",
    "confidence": 0.9,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a historian comment with historical references and a pessimistic tone, When the persona voice metric evaluates it, Then the score is >= 0.7",
      "Given an economist comment with market analysis and a disagreeable/optimistic tone, When the persona voice metric evaluates it, Then the score is >= 0.7",
      "Given a philosopher comment with ethical framing and Socratic questioning, When the persona voice metric evaluates it, Then the score is >= 0.7"
    ]
  },
  {
    "name": "No Fluff Opener Metric (GEval)",
    "description": "System must evaluate whether a comment jumps straight into analysis without throat-clearing openers, and it should use DeepEval's GEval metric to detect filler openings like summarizing the article or generic preambles, so that the 'jump straight into your take' rule is enforced",
    "type": "business_logic",
    "confidence": 0.9,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a comment that opens with 'This article shows that...', When the no-fluff metric evaluates it, Then the score is < 0.5",
      "Given a comment that opens with a direct analytical claim, When the no-fluff metric evaluates it, Then the score is >= 0.7"
    ]
  },
  {
    "name": "Tool Usage Rate Metric",
    "description": "System must track how often each persona actually invokes their research tool across a batch of test articles, and it should implement a deterministic metric that checks whether search_queries is non-empty, so that prompt changes that discourage tool use are caught",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a batch of 3+ articles per persona, When tool usage rate is calculated, Then the rate is reported as a percentage (e.g., '2/3 = 67%')",
      "Given a persona used their tool on 0 of 3 articles, When the tool usage metric evaluates the batch, Then the score is 0.0 (fail)",
      "Given a persona used their tool on 2 of 3 articles, When the tool usage metric evaluates the batch, Then the score is 1.0 (pass, threshold >= 50%)"
    ]
  },
  {
    "name": "Tool Grounding Metric (GEval)",
    "description": "System must evaluate whether a comment that used a research tool actually incorporates information from the tool results into its prose, and it should use DeepEval's GEval metric with the tool results as retrieval_context, so that 'searched but ignored the results' regressions are detected",
    "type": "business_logic",
    "confidence": 0.9,
    "source_lines": [],
    "acceptance_criteria": [
      "Given an economist comment where Yahoo Finance returned stock price data, When the grounding metric evaluates it, Then the score is >= 0.7 if the comment cites specific numbers from the results",
      "Given a historian comment where Wikipedia returned historical facts, When the grounding metric evaluates it, Then the score is >= 0.7 if the comment references facts from the results",
      "Given a comment where a tool was called but the output contains none of the returned information, When the grounding metric evaluates it, Then the score is < 0.5"
    ]
  },
  {
    "name": "Test Harness with Fixtures",
    "description": "System must provide a reusable test harness that loads sample articles and runs all personas through the pipeline to capture output for evaluation, and it should use pytest fixtures to generate test cases from real or synthetic articles, so that tests are easy to run and extend",
    "type": "infrastructure",
    "confidence": 0.9,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a sample article fixture, When the test suite runs, Then each persona generates a comment that is evaluated against all applicable metrics",
      "Given the test suite, When run with `pytest backend/tests/test_prompts.py`, Then all test cases execute and report pass/fail per metric"
    ]
  },
  {
    "name": "Aggregate Scoring Report",
    "description": "System must produce a human-readable summary of metric scores across all test cases, and it should leverage DeepEval's built-in test reporting, so that prompt engineers can quickly identify which personas or metrics are regressing",
    "type": "infrastructure",
    "confidence": 0.8,
    "source_lines": [],
    "acceptance_criteria": [
      "Given the test suite has run, When results are printed, Then each test case shows persona, article, and per-metric scores",
      "Given a failing test case, When the report is viewed, Then the failure reason is human-readable (e.g., 'Word count: 163 > 150')"
    ]
  }
]
```

## Files to Create

- `backend/tests/conftest.py` — Pytest fixtures (sample articles, pipeline runner)
- `backend/tests/test_prompts.py` — DeepEval test cases with all metrics
- `backend/tests/metrics.py` — Custom deterministic metrics (word count, forbidden phrases, formatting)

## Files NOT Modified

- `backend/app/graph/nodes.py` — Pipeline unchanged
- `backend/app/graph/prompts/` — Prompts unchanged (testing validates them, not modifies them)
- `backend/app/routers/` — API unchanged
- `backend/app/models.py` — Schema unchanged
- `frontend/` — Frontend unchanged
- `backend/requirements.txt` — DeepEval is a dev dependency, not production
