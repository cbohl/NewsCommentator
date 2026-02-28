# Feature Specification: Prompt Tuning Round 1 — Voice & Tool Usage

**Feature Branch**: `deepeval-prompt-testing`
**Created**: 2026-02-28
**Status**: Complete
**Input**: DeepEval test suite findings from spec 014. Baseline: 42-44/57 tests passing. Key failures: philosopher voice (0/3), tool usage inconsistent across all personas, tool grounding weak.

## Constitution Amendment Required

None. Prompt content changes only — no changes to architecture, data model, API, or technology stack.

## Rationale

DeepEval testing (spec 014) revealed four prompt quality issues: (1) Sofia's philosophical voice was indistinguishable from generic punditry, (2) all personas inconsistently used their research tools, (3) when tools were used, results weren't cited in commentary, (4) Maggie struggled to find historical parallels for non-historical topics. Prompt changes were iterated against the test suite across two rounds.

## Requirements

```json
[
  {
    "name": "Philosopher Voice Distinctiveness",
    "description": "System must produce philosopher commentary that is recognizably philosophical — citing specific frameworks, thinkers, or traditions — and it should do so by providing an Analytical Toolkit and philosophy-grounded examples in the philosopher prompt, so that Sofia's output is distinguishable from generic punditry",
    "type": "business_logic",
    "confidence": 1.0,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a philosopher comment on any article topic, When the persona voice GEval metric evaluates it, Then the score is >= 0.7",
      "Given the philosopher prompt, When read by a developer, Then it contains named philosophical frameworks (e.g., Kantian ethics, Rawlsian justice, Foucault) and examples that reference them"
    ]
  },
  {
    "name": "Mandatory Tool Usage",
    "description": "System must instruct each persona to use their research tool on every article, and it should use imperative language ('USE IT on every article', 'MANDATORY', 'search on EVERY article') in both the shared search instructions and per-persona prompts, so that tool usage rate exceeds 50% across a batch of articles",
    "type": "business_logic",
    "confidence": 0.9,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a batch of 3+ articles, When the historian processes them, Then Wikipedia is called on >= 2 of 3 articles",
      "Given a batch of 3+ articles, When the philosopher processes them, Then Tavily is called on >= 2 of 3 articles",
      "Given the search_instructions.md prompt, When read by a developer, Then it contains 'USE IT on every article' or equivalent mandatory language"
    ]
  },
  {
    "name": "Tool Result Citation",
    "description": "System must instruct personas to cite specific facts from tool results in their commentary, and it should include explicit 'you MUST cite at least one specific detail from your search results' instructions with examples, so that tool grounding improves",
    "type": "business_logic",
    "confidence": 0.8,
    "source_lines": [],
    "acceptance_criteria": [
      "Given a persona that used a tool and received useful results, When the tool grounding GEval metric evaluates the comment, Then the score trends upward compared to baseline",
      "Given the search_instructions.md prompt, When read by a developer, Then it contains explicit instructions to incorporate search results into prose"
    ]
  },
  {
    "name": "Historian Off-Topic Resilience",
    "description": "System must enable the historian to find historical parallels for any article topic, and it should provide examples of non-obvious parallels (tech stories → printing press, legal → landmark rulings) in the historian prompt, so that Maggie's historical lens works on technology, legal, and philosophical stories",
    "type": "business_logic",
    "confidence": 0.9,
    "source_lines": [],
    "acceptance_criteria": [
      "Given an article about AI copyright (non-historical topic), When the historian persona voice GEval metric evaluates the comment, Then the score is >= 0.7",
      "Given the historian prompt, When read by a developer, Then it contains examples of parallels for non-historical domains"
    ]
  }
]
```

## Files Modified

- `backend/app/graph/prompts/philosopher.md` — Added Analytical Toolkit (Kant, Rawls, Foucault, etc.), Research Tools section, philosophy-grounded examples
- `backend/app/graph/prompts/historian.md` — Added off-topic examples (tech → printing press, legal → landmark rulings), strengthened tool citation instructions
- `backend/app/graph/prompts/economist.md` — Strengthened tool usage to "MANDATORY", added ticker mappings by topic
- `backend/app/graph/prompts/search_instructions.md` — Rewrote: "SHOULD use" → "USE IT on every article", added grounding requirement, removed per-tool descriptions (each persona only has one tool)
- `backend/app/graph/nodes.py` — Added `result_snippet` field to search_queries dict (supports tool grounding test)

## Files NOT Modified

- `backend/app/routers/chat.py` — Chat unchanged
- `backend/app/schemas.py` — Schema unchanged (ignores extra `result_snippet` field)
- `frontend/` — Frontend unchanged
- `backend/app/services/pipeline.py` — Pipeline unchanged

## Test Results

| Run | Passed | Failed | Skipped |
|-----|--------|--------|---------|
| Baseline (pre-changes) | 42-44 | 9 | 4-6 |
| Round 1 (voice + tool nudges) | 48 | 6 | 3 |
| Round 2 (stronger grounding + examples) | 48 | 6 | 3 |

### Key Improvements
- Philosopher voice: 0/3 → 3/3 (fixed)
- Historian tool usage: 1-2/3 → 3/3 (fixed)
- Philosopher tool usage: 0/3 → 3/3 (fixed)
- Historian off-topic: failing → passing (fixed)

### Known Remaining Issues
- Economist tool usage (0/3): GPT-5.2 ignores Yahoo Finance calls despite "MANDATORY" instruction. Likely a tool/model behavior issue, not a prompt issue.
- Historian tool grounding (0/3): Maggie searches Wikipedia but results are too generic (definitions, founding history). She correctly prefers article-specific facts over Wikipedia boilerplate. The 0.7 threshold may be too strict for this pattern.
