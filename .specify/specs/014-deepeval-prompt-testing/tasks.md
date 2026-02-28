# Tasks: DeepEval Prompt Testing

**Input**: `specs/014-deepeval-prompt-testing/plan.md`

## Phase 1: Infrastructure

- [x] T001 Install `deepeval` into backend venv as dev dependency
- [x] T002 Create `backend/tests/conftest.py` with sample article fixtures and `generate_comment()` helper that returns `(comment, searches)` tuple

## Phase 2: Deterministic Metrics

- [x] T003 Create `backend/tests/metrics.py` with `WordCountMetric` (max 150 words)
- [x] T004 Add `ForbiddenPhraseMetric` to metrics.py (all phrases from system_rules.md)
- [x] T005 Add `NoBulletPointsMetric` to metrics.py (detect list markers in output)
- [x] T006 Add `ToolUsageRateMetric` to metrics.py (fail if tool used on < 50% of articles in batch)

## Phase 3: GEval Metrics

- [x] T007 Add persona voice GEval metric with per-persona criteria (historian=pessimistic/historical, economist=optimistic/market-oriented, philosopher=measured/ethical)
- [x] T008 Add no-fluff opener GEval metric (penalizes article-summarizing and throat-clearing openers)
- [x] T009 Add tool grounding GEval metric (checks comment incorporates facts from tool results via retrieval_context)

## Phase 4: Test Cases

- [x] T010 Create `backend/tests/test_prompts.py` with parameterized quality test cases (3 personas × sample articles)
- [x] T011 Add tool usage rate test (per-persona across all articles, >= 50% threshold)
- [x] T012 Add tool grounding test (per test case where tool was used, skips when no tool call)

## Phase 5: Validate

- [x] T013 Run deterministic-only tests — all 27/27 pass (word count, forbidden phrases, bullet points)
- [x] T014 Run full suite — 42-44 passed, 9 failed, 4-6 skipped. Failures are real prompt quality issues (see findings below)
- [x] T015 Verify test report output is human-readable — GEval reasons clearly explain each failure

## Phase Dependencies

- Phase 1 must complete before all others
- Phase 2 and Phase 3 can run in parallel
- Phase 4 depends on Phases 2 and 3
- Phase 5 depends on Phase 4
- T003, T004, T005, T006 are independent [P]
- T007, T008, T009 are independent [P]
- T010, T011, T012 are independent [P]

## Test Findings (Prompt Issues Detected)

These failures represent real prompt quality issues to address in future prompt iterations:

1. **Philosopher voice not distinctive** — Sofia fails persona voice on all 3 articles across both runs. Her output reads as generic punditry, not philosophical analysis.
2. **Tool usage unreliable** — No persona consistently uses their tool on >= 50% of articles. Tool usage is highly variable across runs.
3. **Tool grounding weak** — When tools are used, results are often not well-incorporated into the commentary. This is the Tim/Yahoo Finance problem at scale.
4. **Historian struggles off-topic** — Maggie's historical lens is weak on non-historical articles (e.g., AI copyright).

## Production Code Change

- `backend/app/graph/nodes.py`: Added `result_snippet` field to search_queries dict in `_invoke_with_tools`. This captures tool results (truncated to 500 chars) alongside queries, enabling the tool grounding test. Backwards-compatible — `SearchQuery` Pydantic model ignores extra fields.
