# 018 — Search Fixes & Feed Swap

## Problem

Two search-related bugs and one feed change:

1. **Wikipedia broken** — Wikipedia tightened their API to require a proper User-Agent header. The `wikipedia` 1.4.0 package doesn't set one, so every request returns 403. Maggie (historian) can no longer use Wikipedia.
2. **Search narration leaking into comments** — The LLM occasionally outputs "Searching web for..." text and pseudo-JSON tool calls as part of its response content instead of using proper tool-calling. This raw text appears in Sofia's published comments.
3. **Feed swap** — Replace the World news feed with BBC Science & Environment.

## Requirements

1. **Wikipedia User-Agent** — Set a proper User-Agent string on the `wikipedia` package before initializing the LangChain Wikipedia tool
2. **Response cleaning** — Strip leaked search narration and pseudo-JSON tool call objects from LLM output before storing
3. **Prompt guardrail** — Add explicit instruction in search_instructions.md telling the LLM to never narrate its search process
4. **Feed swap** — Replace `world` feed with `science` (BBC Science & Environment) in both backend RSS config and frontend tab labels
