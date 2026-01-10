# IMP-0008: Add Progressive Hints for Stuck Players

**Priority:** HIGH
**Category:** ux_flow
**Effort:** high
**Status:** proposed

## Affected Files

- `backend/engine/actions.py`
- `backend/llm/narrative.py`
- `backend/models/state.py`
- `backend/engine/hints.py` (new)

## Problem Statement

1 session got completely stuck. The speedrunner tried `go passage` 5 times consecutively, receiving the same unhelpful message each time: "The way forward is not yet open to you. Something must first be understood."

## Root Cause Analysis

The game provides no guidance when players:
1. Attempt locked actions repeatedly
2. Don't know what to explore next
3. Miss hidden objects or conversation topics

## Proposed Solution

### 1. Add Stuck Detection State

```python
# backend/models/state.py
class GameState(BaseModel):
    ...
    repeated_failures: dict[str, int] = {}  # Track repeated failed actions
    last_hint_turn: int = 0  # Prevent hint spam
```

### 2. Progressive Hint System

```python
# backend/engine/hints.py (new file)
from models.state import GameState

HINT_PROGRESSIONS = {
    "passage_locked": [
        "The passage remains closed. Perhaps speaking with others will reveal what you need.",
        "The companion may know more about what must be understood. Have you asked about the traveler?",
        "The archive holds secrets. The technical diagrams might reveal something important.",
        "Try: examine technical_diagrams in the archive, then ask the companion about them.",
    ],
    "no_progress": [
        "There is much to discover here. Have you explored all the rooms?",
        "The keeper's cell and archive both hold secrets. Try examining objects closely.",
        "Speaking with the companion about different topics may reveal new paths.",
    ],
    "stuck_in_room": [
        "Perhaps there's more to see here. Try 'look' to see what's around you.",
        "You might examine objects or talk to characters present.",
    ],
}

def get_progressive_hint(state: GameState, failure_type: str) -> str | None:
    """Get next hint in progression based on failure count."""
    count = state.repeated_failures.get(failure_type, 0)
    hints = HINT_PROGRESSIONS.get(failure_type, [])

    if count > 0 and count <= len(hints):
        return hints[count - 1]
    elif count > len(hints):
        return hints[-1]  # Repeat final hint

    return None

def should_show_hint(state: GameState) -> bool:
    """Check if enough turns have passed since last hint."""
    return state.turn_count - state.last_hint_turn >= 3
```

### 3. Integrate into Validation

```python
# backend/engine/validation.py
from engine.hints import get_progressive_hint, should_show_hint

def validate_intent(intent: Intent, state: GameState) -> bool | str:
    ...
    # Check locked rooms
    target_room = ROOMS.get(target)
    if target_room and "locked_until" in target_room:
        for required_flag in target_room["locked_until"]:
            if not flags_dict.get(required_flag, False):
                # Track failure
                failure_key = f"locked_{target}"
                state.repeated_failures[failure_key] = state.repeated_failures.get(failure_key, 0) + 1

                base_msg = "The way forward is not yet open to you."
                if should_show_hint(state):
                    hint = get_progressive_hint(state, "passage_locked")
                    if hint:
                        state.last_hint_turn = state.turn_count
                        return f"{base_msg} {hint}"

                return base_msg
```

### 4. Contextual Hints in Help

```python
# backend/engine/actions.py
def _execute_help(state: GameState) -> tuple[GameState, ActionResult]:
    """Show contextual help based on current progress."""
    base_help = """..."""

    # Add contextual suggestions
    suggestions = []
    flags = state.flags.model_dump()

    if not flags.get("found_technical_diagrams"):
        suggestions.append("Try exploring the archive and examining what you find there.")
    elif not flags.get("found_companion_origin"):
        suggestions.append("The archive may hold more secrets related to what you've discovered.")
    elif not flags.get("companion_admitted_recognition"):
        suggestions.append("Perhaps you should ask the companion about what you've found.")

    if suggestions:
        base_help += "\n\nSuggestions:\n" + "\n".join(f"- {s}" for s in suggestions)

    return state, ActionResult(success=True, message=base_help)
```

## Implementation Steps

1. Add `repeated_failures` and `last_hint_turn` to GameState
2. Create `backend/engine/hints.py` with hint progressions
3. Update validation to track and display hints
4. Update help command to show contextual suggestions
5. Test with confused_user persona to verify improvement

## Success Criteria

- Stuck sessions reduced to 0
- Players receive actionable guidance within 3 failed attempts
- Hint quality validates via manual review
