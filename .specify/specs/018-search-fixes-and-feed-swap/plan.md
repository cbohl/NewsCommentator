# 018 — Search Fixes & Feed Swap: Implementation Plan

## Files to Modify

| File | Change |
|------|--------|
| `backend/app/graph/nodes.py` | Set Wikipedia User-Agent; add `_clean_response()` to strip leaked narration |
| `backend/app/graph/prompts/search_instructions.md` | Add "NEVER narrate your search process" rule |
| `backend/app/services/rss.py` | Replace `world` feed with `science` |
| `frontend/src/pages/Home.tsx` | Replace World tab with Science & Environment |

## Approach

1. **Wikipedia fix**: In `_get_wikipedia_tool()`, import `wikipedia` and call `set_user_agent()` with a descriptive string before creating the LangChain wrapper. This sets the User-Agent header on all subsequent requests.
2. **Response cleaning**: Add regex-based `_clean_response()` function that strips pseudo-JSON tool calls (`{"query":"..."}`) and search narration phrases (`Searching web for...`). Apply it to the return value of `_invoke_with_tools()`.
3. **Prompt guardrail**: Add a bullet to search_instructions.md explicitly forbidding search narration, JSON, and tool-call text in the response.
4. **Feed swap**: Change the `FEEDS` dict key from `world` to `science` with the BBC Science & Environment RSS URL. Update the frontend `FEEDS` array and `FEED_LABELS` map to match.
