# LLM Integration Review

Focused review of Claude API integration patterns in The Last Vigil:

## Files to Review
- `backend/llm/intent.py` - Intent classification with Haiku
- `backend/llm/narrative.py` - Narrative generation with Sonnet
- `backend/llm/prompts.py` - System prompts

## Checklist

### 1. API Calls
- [ ] All LLM calls have timeout handling
- [ ] Blocking calls wrapped in `asyncio.to_thread()`
- [ ] Proper error handling for API failures
- [ ] Rate limit handling (429 responses)
- [ ] Fallback responses when LLM fails

### 2. Prompts (`prompts.py`)
- [ ] System prompts are clear and focused
- [ ] Context building includes necessary game state
- [ ] No prompt injection vulnerabilities
- [ ] Token usage is reasonable (check max_tokens)

### 3. Intent Classification (`intent.py`)
- [ ] JSON parsing handles malformed responses
- [ ] Confidence levels are used appropriately
- [ ] Unknown intents have graceful fallback
- [ ] Target resolution (aliases) works correctly

### 4. Narrative Generation (`narrative.py`)
- [ ] Caching is effective (check cache hit rate)
- [ ] Cache has size limits and expiration
- [ ] Fallback descriptions cover all cases
- [ ] Context includes visible objects/exits only

### 5. Performance
- [ ] Intent uses fast model (Haiku)
- [ ] Narrative uses quality model (Sonnet)
- [ ] Caching reduces redundant calls
- [ ] Response times are acceptable (<5s)

## Known Issues
1. `generate_opening_narrative()` is blocking (not wrapped in to_thread)
2. `generate_ending_narrative()` is blocking
3. Cache has no size limit or TTL
4. `print()` used instead of logger for errors
5. Model names hardcoded (should be env vars)
6. Duplicate `get_client()` in both files

## Metrics to Check
- Average intent classification time
- Average narrative generation time
- Cache hit rate
- Timeout frequency
- Error rate

## Output
Report on:
1. Correctness of async patterns
2. Robustness of error handling
3. Efficiency of caching
4. Quality of prompts
5. Specific code improvements needed
