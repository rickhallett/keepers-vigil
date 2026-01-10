# IMP-0007: Add Timeout Handling for Slow Requests

**Priority:** MEDIUM
**Category:** error_handling
**Effort:** medium
**Status:** proposed

## Affected Files

- `backend/api/routes.py`
- `frontend/src/api/client.ts`

## Problem Statement

Maximum response time was 16,267ms. Users have no feedback during long waits.

## Proposed Solution

### 1. Add Backend Timeout

```python
# backend/llm/intent.py and narrative.py
import asyncio

async def classify_intent(...) -> Intent:
    try:
        result = await asyncio.wait_for(
            _classify_intent_impl(...),
            timeout=10.0  # 10 second timeout
        )
        return result
    except asyncio.TimeoutError:
        return Intent(intent=IntentType.UNKNOWN, confidence="low")
```

### 2. Add Frontend Timeout and Retry

```typescript
// frontend/src/api/client.ts
export async function sendCommand(sessionId: string, input: string): Promise<CommandResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);  // 15s timeout

  try {
    const response = await fetch(`${API_BASE}/api/command`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, input }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      return {
        narrative: "The station seems to pause, considering your words. Perhaps try again?",
        state_changed: false,
        // ... other fields preserved
      };
    }
    throw error;
  }
}
```

### 3. Add Loading State Feedback

```typescript
// frontend/src/hooks/useGameState.ts
const [loadingMessage, setLoadingMessage] = useState<string>("");

// Update loading message for long waits
useEffect(() => {
  if (loading) {
    const timer = setTimeout(() => {
      setLoadingMessage("The companion considers your words...");
    }, 3000);

    const timer2 = setTimeout(() => {
      setLoadingMessage("The station's ancient mechanisms stir...");
    }, 8000);

    return () => {
      clearTimeout(timer);
      clearTimeout(timer2);
    };
  }
}, [loading]);
```

## Success Criteria

- No requests hang indefinitely
- Users receive feedback for waits > 3s
- Graceful fallback narrative for timeouts
