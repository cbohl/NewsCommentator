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

### User Story 2 — Server-Side Length Tier Selection (Priority: P1)

The server randomly selects a length tier (SHORT/MEDIUM/LONG) per persona per article and injects it as a direct instruction into the prompt. The LLM is NOT asked to choose its own length — it is TOLD which length to use.

**Why this approach**: LLMs reliably ignore probabilistic self-selection instructions ("use SHORT ~30% of the time") and default to long. Selecting the tier server-side and injecting a direct command ("YOUR LENGTH: SHORT — write 15-40 words") produces reliable variation because the model only has to follow one clear instruction, not make a judgment call.

**Acceptance Scenarios**:

1. **Given** the server selects SHORT for a persona, **When** the prompt is built, **Then** it includes a direct instruction like "YOUR ASSIGNED LENGTH: SHORT (15–40 words). Write one or two punchy sentences."
2. **Given** the server selects MEDIUM, **When** the prompt is built, **Then** it includes "YOUR ASSIGNED LENGTH: MEDIUM (50–90 words). Write a focused paragraph."
3. **Given** the server selects LONG, **When** the prompt is built, **Then** it includes "YOUR ASSIGNED LENGTH: LONG (100–150 words). Develop a full argument."
4. **Given** 15 comments across 5 articles, **When** reviewing the tier assignments, **Then** roughly 30% are SHORT, 50% are MEDIUM, 20% are LONG (via `random.choices` with weights).

---

### User Story 3 — SYSTEM_RULES Simplification (Priority: P2)

SYSTEM_RULES no longer asks the model to pick its own length. The tier definitions are removed from SYSTEM_RULES since the server handles selection. SYSTEM_RULES retains the hard cap of 150 words as a safety net.

**Acceptance Scenarios**:

1. **Given** the updated SYSTEM_RULES, **When** reading the prompt, **Then** there are no tier selection instructions — only a hard cap reminder.

## Requirements

### Functional Requirements

- **FR-001**: LLM model MUST be changed from `gpt-5-nano` to `gpt-5.2` in `_get_llm()`.
- **FR-002**: Each persona node MUST randomly select a length tier using `random.choices(["SHORT", "MEDIUM", "LONG"], weights=[30, 50, 20])`.
- **FR-003**: The selected tier MUST be injected into the system prompt as a direct instruction with the word range (e.g., "YOUR ASSIGNED LENGTH: SHORT (15–40 words)").
- **FR-004**: SYSTEM_RULES MUST retain a hard cap of 150 words but MUST NOT contain tier self-selection instructions.
- **FR-005**: Constitution MUST be amended to version 1.3.1 (length refinement) and 1.3.2 (model upgrade).
- **FR-006**: Technology Stack table in constitution MUST reflect GPT-5.2 as the locked LLM.

## Success Criteria

- **SC-001**: `_get_llm()` returns `ChatOpenAI(model="gpt-5.2")`.
- **SC-002**: Server-side tier selection is implemented with correct weight distribution (30/50/20).
- **SC-003**: Each LLM call includes a direct length instruction matching the selected tier.
- **SC-004**: Constitution version is 1.3.2 with both amendments logged.
- **SC-005**: Across 5 articles (15 comments), response lengths match their assigned tiers — SHORT responses under 50 words, MEDIUM under 100, LONG under 150.
