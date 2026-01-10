# Backend Code Review

Perform a detailed code review of the backend focusing on these known patterns and concerns for The Last Vigil:

## Review Checklist

### 1. LLM Integration (Priority: High)
- [ ] Check `llm/intent.py` and `llm/narrative.py` for blocking calls in async functions
- [ ] Verify timeout handling with `asyncio.wait_for`
- [ ] Check for proper error recovery with fallback responses
- [ ] Ensure narrative caching is working (check `_narrative_cache` usage)
- [ ] Verify model names are not hardcoded (should be configurable)

### 2. API Routes (`api/routes.py`)
- [ ] Check error responses use consistent format
- [ ] Verify session validation on all endpoints
- [ ] Check for proper async/await usage
- [ ] Ensure CORS configuration is appropriate

### 3. Game Engine (`engine/`)
- [ ] Check `validation.py` doesn't mutate intent objects (known issue)
- [ ] Verify `actions.py` handles all IntentTypes
- [ ] Check `hints.py` progressive hint logic
- [ ] Verify `state_store.py` session cleanup (known issue: no expiration)

### 4. Data Layer (`data/`)
- [ ] Check `rooms.py` room definitions match objects
- [ ] Verify `objects.py` flag requirements are consistent
- [ ] Check `conversations.py` dialogue tree completeness
- [ ] Verify object aliases resolve correctly

### 5. Models (`models/`)
- [ ] Check Pydantic models have proper validation
- [ ] Verify `GameFlags` covers all game states
- [ ] Check `ending_chosen` type safety

## Known Issues to Check
1. `generate_opening_narrative()` and `generate_ending_narrative()` may be blocking
2. Session storage has no expiration/cleanup
3. `print()` statements should be `logger.error()`
4. Duplicate `get_client()` functions in intent.py and narrative.py
5. `classify_intent_sync()` uses deprecated `get_event_loop()`

## Output Format
Provide findings as:
- **Critical**: Must fix before deploy
- **High**: Should fix soon
- **Medium**: Improve when convenient
- **Low**: Nice to have

Include file paths and line numbers for all issues found.
