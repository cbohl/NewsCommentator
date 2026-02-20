# Feature Specification: Persona Interaction & Randomized Order

**Feature Branch**: `003-persona-interaction`
**Created**: 2026-02-20
**Status**: Draft
**Input**: User request: "I want the personas to respond to each other and randomize which one responds first."

## Constitution Amendment Required

The Data Flow Contract (Operational Standards) currently specifies:
> "Run Historian → Economist → Philosopher nodes sequentially against shared state."

This must be amended to:
> "Run all three persona nodes sequentially in a randomized order against shared state. Later nodes may reference earlier nodes' comments."

**Amendment**: Version 1.2.0 — Randomize persona execution order and enable inter-persona commentary.

## User Scenarios & Testing

### User Story 1 - Randomized Execution Order (Priority: P1)

Each time the pipeline processes an article, the three personas execute in a random order. Over multiple articles, the order varies.

**Why this priority**: Without this, the same persona always gets "first take" and the interaction pattern is always the same.

**Independent Test**: Process 3 articles and verify the persona order differs in at least 2 of the 3 runs.

**Acceptance Scenarios**:

1. **Given** an article is processed, **When** the LangGraph pipeline runs, **Then** the three nodes execute in a randomly shuffled order.
2. **Given** 5 articles are processed, **When** reviewing the execution logs, **Then** at least 2 different orderings appear.

---

### User Story 2 - Personas Respond to Each Other (Priority: P1)

The second and third personas to execute see the prior comment(s) in their prompt and can agree, disagree, or build on what was said.

**Why this priority**: This is what makes the commentary feel like a real panel discussion rather than three isolated takes.

**Independent Test**: Process an article, read the second and third comments, verify they reference or engage with what came before.

**Acceptance Scenarios**:

1. **Given** the Historian runs first and comments on an article, **When** the Economist runs second, **Then** the Economist's prompt includes the Historian's comment and the Economist may reference, challenge, or build on it.
2. **Given** two personas have already commented, **When** the third persona runs, **Then** it sees both prior comments and can engage with either or both.
3. **Given** a persona runs first, **When** it has no prior comments to reference, **Then** it comments solely on the article (same as current behavior).

---

### Edge Cases

- What if a prior persona's comment is empty due to an error? The next persona should proceed as if no prior comment exists.
- Should personas always reference each other? No — they should be free to engage or not. The prompt should say "you may respond to" not "you must respond to."

## Requirements

### Functional Requirements

- **FR-001**: The graph must compile a new random node order per article (not per pipeline run — each article gets its own shuffle).
- **FR-002**: Each node function must check the shared state for prior comments and include them in the prompt when present.
- **FR-003**: The prompt instruction for referencing prior comments must be optional ("you may agree, disagree, or build on") not mandatory.
- **FR-004**: The execution order for each article must be logged for observability.
- **FR-005**: The `CommentaryState` must be extended with a field to track execution order.

### Key Entities (changes)

- **CommentaryState**: Add `execution_order: list[str]` to track which persona ran in which position.

## Success Criteria

- **SC-001**: Over 5 articles, at least 2 different execution orders appear.
- **SC-002**: In articles where a persona runs second or third, at least half of those comments show awareness of prior commentary.
- **SC-003**: First-to-run persona comments remain high quality with no regression.
- **SC-004**: Execution order is logged per article for debugging.
