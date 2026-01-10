# IMP-0009: Improve Guidance at Common Failure Points

**Priority:** MEDIUM
**Category:** ux_flow
**Effort:** medium
**Status:** proposed

## Affected Files

- `backend/llm/narrative.py`
- `backend/data/rooms.py`

## Problem Statement

Common failure points identified:
- `archive: go passage` (locked room, no guidance)
- `letter_room: help` (generic help, not contextual)
- `archive: ask companion about the player` (requires flag not set)
- `threshold: inventory` (empty inventory, unhelpful response)

## Proposed Solution

### 1. Contextual Failure Messages

```python
# backend/engine/validation.py
def validate_intent(intent: Intent, state: GameState) -> bool | str:
    ...
    # For "ask companion about the player" without required flag
    if intent.intent == IntentType.ASK_ABOUT:
        if intent.subject and "player" in intent.subject.lower():
            if not state.flags.found_keeper_logs:
                return "The companion tilts its head. 'You? There is much I could say, but... have you looked at the keeper's logs? In the cell. They might help you understand the question you're asking.'"
```

### 2. Improve Empty Inventory Response

```python
# backend/llm/narrative.py
if action == "INVENTORY":
    if not state.inventory:
        suggestions = []
        if not state.flags.found_technical_diagrams:
            suggestions.append("The archive might hold items worth carrying.")
        return "You carry nothing but your purpose here. The station provides what is needed." + (f" {suggestions[0]}" if suggestions else "")
```

### 3. Room-Specific Help

```python
# backend/engine/actions.py
def _execute_help(state: GameState) -> tuple[GameState, ActionResult]:
    room_id = state.current_room.value

    room_tips = {
        "archive": "The archive holds many secrets. Try examining the technical diagrams or the strange device on the shelves.",
        "letter_room": "Letters from travelers past fill this room. Some are old, very old.",
        "keeper_cell": "Your quarters. The desk holds a journal and logs that span countless vigils.",
        "threshold": "The traveler waits here. Speaking with them, or with the companion, may reveal much.",
        "passage": "The way forward. When you are ready, the light will welcome you.",
    }

    base_help = """..."""
    room_help = room_tips.get(room_id, "")

    return state, ActionResult(success=True, message=f"{base_help}\n\n{room_help}")
```

## Success Criteria

- Failure point actions provide actionable guidance
- Help command is contextual to current room and progress
- Repeated failures trigger progressive hints (see IMP-0008)
