# Feature Specification: Model Upgrade & Response Length Tuning

**Feature Branch**: `007-model-upgrade`
**Created**: 2026-02-23
**Status**: Complete (retroactive)
**Input**: User request: "Upgrade to GPT-5.2 for better prompt following and tune response lengths with explicit SHORT/MEDIUM/LONG tiers."

## Constitution Amendments Required

Two amendments to the constitution:

- **1.3.1**: Refined Article III (Anti-AI-ism Voice Standard) — added target range of 30-100 words with max 150, encouraging short punchy responses. Rationale: LLMs default to filling the word limit; explicit shorter targets produce more natural length variation.
- **1.3.2**: Upgraded LLM from GPT-5-nano to GPT-5.2. Rationale: larger model follows nuanced prompt instructions (length variation, personality, interaction rate) significantly better. Technology Stack table updated.

## User Scenarios & Testing

### User Story 1 — Better Prompt Following (Priority: P1)

The LLM reliably produces varied lengths, distinct personalities, and natural interaction between personas.

**Why this priority**: GPT-5-nano was not consistently following the nuanced persona prompts from 005-persona-identity.

**Acceptance Scenarios**:

1. **Given** the upgraded model (GPT-5.2), **When** processing 5 articles (15 comments), **Then** response lengths visibly vary — some under 40 words, some 50-90, some 100+.
2. **Given** the upgraded model, **When** personas have prior comments available, **Then** approximately 40% of later-position comments reference a colleague.

---

### User Story 2 — Explicit Length Tiers (Priority: P1)

SYSTEM_RULES includes explicit SHORT/MEDIUM/LONG tiers with target percentages to prevent the LLM from defaulting to maximum length.

**Acceptance Scenarios**:

1. **Given** the updated SYSTEM_RULES, **When** reading the prompt, **Then** three tiers are defined: SHORT (15-40 words, ~30%), MEDIUM (50-90 words, ~50%), LONG (100-150 words, ~20%).
2. **Given** the instruction "Decide your length BEFORE you start writing", **When** the LLM generates, **Then** responses don't all cluster at 100+ words.

## Requirements

### Functional Requirements

- **FR-001**: LLM model MUST be changed from `gpt-5-nano` to `gpt-5.2` in `_get_llm()`.
- **FR-002**: SYSTEM_RULES MUST define three explicit length tiers with percentage targets.
- **FR-003**: SYSTEM_RULES MUST instruct the model to choose length before writing.
- **FR-004**: Constitution MUST be amended to version 1.3.1 (length refinement) and 1.3.2 (model upgrade).
- **FR-005**: Technology Stack table in constitution MUST reflect GPT-5.2 as the locked LLM.

## Success Criteria

- **SC-001**: `_get_llm()` returns `ChatOpenAI(model="gpt-5.2")`.
- **SC-002**: SYSTEM_RULES contains SHORT/MEDIUM/LONG tier definitions with word ranges and percentages.
- **SC-003**: Constitution version is 1.3.2 with both amendments logged.
- **SC-004**: Across 5 articles, response lengths show clear variation matching the tier distribution.
