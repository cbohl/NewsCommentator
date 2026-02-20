# Feature Specification: Prompt Refinement

**Feature Branch**: `002-prompt-refinement`
**Created**: 2026-02-20
**Status**: Draft
**Input**: User feedback: "Responses are too similar and formulaic. Economist over-indexes on incentives, Historian over-indexes on Great Man theory. Language feels like structured AI output, not natural expert commentary."

## Problem Statement

The current prompts produce repetitive, formulaic output:
- **Historian** mentions "Great Man theory" and "Social Forces" in nearly every response, regardless of relevance.
- **Economist** defaults to "incentives" framing even when game theory, scarcity, or market dynamics would be more appropriate.
- **Philosopher** output is less formulaic but still feels structured rather than conversational.
- All three personas produce text that reads like AI-generated analysis rather than natural expert commentary you'd find quoted in a news article.
- Responses sometimes include colons and bullet-like structures instead of flowing prose.

## Constitution Check

This is an implementation refinement, not a persona identity change. Article II defines the *analytical lenses* each persona uses — it does not mandate that every response invoke every lens. The prompts should draw from their toolkit naturally, not mechanically cite every framework every time.

No constitutional amendment required.

## User Scenarios & Testing

### User Story 1 - Natural Expert Voice (Priority: P1)

Each persona's commentary should read like a quote from a real expert in a news article — conversational, opinionated, and varied in structure.

**Why this priority**: The entire value of the product depends on commentary that feels human and worth reading.

**Independent Test**: Process 3 different articles and verify no two responses from the same persona follow the same structural pattern.

**Acceptance Scenarios**:

1. **Given** an article about a trade dispute, **When** the Historian comments, **Then** the response does NOT mechanically name-drop "Great Man theory" or "Social Forces" — it draws on historical precedent naturally.
2. **Given** an article about a military conflict, **When** the Economist comments, **Then** the response does NOT lead with "incentives" — it picks the most relevant economic lens for that specific story.
3. **Given** any article, **When** any persona comments, **Then** the response is flowing prose with no colons, no bullet points, no numbered lists, and no structured headers.
4. **Given** 3 articles processed, **When** reading all 9 comments, **Then** each persona's comments vary in structure — different opening strategies, different rhetorical approaches.

### Edge Cases

- What if the article is genuinely about incentive design? The Economist should still discuss incentives — the fix is about not *defaulting* to it, not avoiding it.
- What if historical Great Man theory is directly relevant? Same — use it when it fits, don't shoehorn it.

## Requirements

### Functional Requirements

- **FR-001**: Historian prompt MUST NOT instruct the model to reference "Great Man" or "Social Forces" in every response. These should be available frameworks, not mandatory citations.
- **FR-002**: Economist prompt MUST NOT instruct the model to lead with incentives. The prompt should list the full range of economic lenses and instruct the model to pick the most relevant one.
- **FR-003**: All persona prompts MUST instruct the model to write in natural flowing prose — no colons as separators, no bullet points, no structured formatting.
- **FR-004**: All persona prompts MUST instruct the model to vary its opening and rhetorical structure across responses.
- **FR-005**: The global SYSTEM_RULES must prohibit structured formatting (colons as headers, lists, etc.).

## Success Criteria

- **SC-001**: Across 5 processed articles, no persona uses the same opening pattern more than once.
- **SC-002**: The word "incentives" appears in fewer than half of Economist responses.
- **SC-003**: The phrases "Great Man" and "Social Forces" appear in fewer than half of Historian responses.
- **SC-004**: Zero comments contain colons used as headers/separators, bullet points, or numbered lists.
- **SC-005**: A casual reader could not easily distinguish the output from a human expert quote.
