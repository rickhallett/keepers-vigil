# IMP-0006: Optimize API Response Times

**Priority:** HIGH
**Category:** performance
**Effort:** high
**Status:** complete

## Affected Files

- `backend/llm/intent.py`
- `backend/llm/narrative.py`
- `backend/api/routes.py`

## Problem Statement

Average response time is 7,801ms with max of 16,267ms. Target is < 3,000ms for good UX.

## Root Cause Analysis

Each command makes 2 sequential LLM calls:
1. Intent classification (~2-3s)
2. Narrative generation (~4-5s)

Both use `claude-sonnet-4-20250514` with no caching or optimization.

## Proposed Solution

### 1. Use Faster Model for Intent Classification

Intent classification is structured output - use Haiku:

```python
# backend/llm/intent.py
async def classify_intent(player_input: str, state: GameState) -> Intent:
    ...
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Was: claude-sonnet-4-20250514
        max_tokens=256,
        ...
    )
```

Expected savings: ~1.5-2s per request

### 2. Add Response Caching

Cache narrative responses for repeated examinations:

```python
# backend/llm/narrative.py
from functools import lru_cache
import hashlib

_narrative_cache: dict[str, str] = {}

def _cache_key(action: str, context: dict, flags: dict) -> str:
    """Generate cache key for narrative request."""
    key_data = f"{action}:{sorted(context.items())}:{sorted(flags.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()

async def generate_narrative(...) -> str:
    cache_key = _cache_key(action, result_context, flags_dict)

    if cache_key in _narrative_cache:
        return _narrative_cache[cache_key]

    # ... generate narrative ...

    _narrative_cache[cache_key] = result
    return result
```

### 3. Parallel LLM Calls (Future)

For non-dependent operations, call LLM in parallel:

```python
# backend/api/routes.py
async def process_command(request: CommandRequest) -> CommandResponse:
    ...
    # Start intent classification
    intent_task = asyncio.create_task(classify_intent(request.input, state))

    # Pre-generate context while waiting
    room = ROOMS.get(state.current_room.value, {})

    intent = await intent_task
    ...
```

### 4. Reduce Narrative Token Limits

```python
# backend/llm/narrative.py
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=512,  # Was: 1024 - most responses are < 300 tokens
    ...
)
```

## Implementation Steps

1. Switch intent classification to Haiku model
2. Add narrative caching for EXAMINE and LOOK actions
3. Reduce max_tokens for narrative generation
4. Add response time logging to identify bottlenecks
5. Re-run tests to measure improvement

## Success Criteria

- Average response time < 4,000ms
- 95th percentile response time < 6,000ms
- No degradation in narrative quality
