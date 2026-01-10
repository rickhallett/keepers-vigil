# IMP-0005: Reduce Difficulty of Reaching Endings

**Priority:** HIGH
**Category:** balance
**Effort:** high
**Status:** complete

## Affected Files

- `backend/engine/actions.py`
- `backend/llm/narrative.py`
- `backend/data/conversations.py`
- `backend/data/rooms.py`

## Problem Statement

6/6 test sessions (100%) failed to reach any ending. The `passage` room was never visited, and critical flags (`found_creator_journal`, `found_companion_origin`, `found_old_letter`) were never discovered.

## Root Cause Analysis

The current flag progression chain is too long and opaque:

```
traveler_spoke_initial
    └─> traveler_spoke_confused
            └─> found_technical_diagrams (archive)
                    └─> traveler_spoke_remembering
                    └─> found_companion_origin (archive, requires found_technical_diagrams)
                            └─> companion_admitted_recognition (ask companion about recognition)
                                    └─> found_keeper_logs (keeper_cell, requires companion_admitted_recognition)
                                            └─> player_identity_revealed (ask companion about the_player)
                                    └─> companion_revealed_purpose (ask companion about purpose)
                            └─> found_creator_journal (archive, hidden, requires found_companion_origin)
                                    └─> found_old_letter (letter_room, hidden, requires found_creator_journal)
                                            └─> little_light topic unlocked
                                    └─> traveler_spoke_remembering + companion_revealed_purpose
                                            └─> traveler_identity_revealed
                                                    └─> passage room unlocked
                                                    └─> endings available
```

Players must:
1. Talk to traveler multiple times
2. Find and examine technical_diagrams in archive
3. Find and examine companion_origin_record (requires #2)
4. Ask companion about recognition (requires #3)
5. Ask companion about purpose (requires #4)
6. Find creator_journal (hidden, requires #3)
7. Visit letter_room and find old_letter (hidden, requires #6)
8. Have all conversations complete to unlock passage

This is a 12+ step critical path with no guidance.

## Proposed Solution

### Option A: Shorten Critical Path (Recommended)

Reduce required flags for passage to core revelations only:

```python
# backend/data/rooms.py
"passage": {
    ...
    "locked_until": ["companion_revealed_purpose"],  # Was: traveler_identity_revealed
}
```

Make `traveler_identity_revealed` set automatically when passage conditions are met:

```python
# backend/engine/actions.py - in _execute_move for passage
if target == "passage" and not state.flags.traveler_identity_revealed:
    state.flags.traveler_identity_revealed = True
```

### Option B: Add Alternative Path

Allow passage access through multiple flag combinations:

```python
# backend/data/rooms.py
"passage": {
    ...
    "locked_until_any": [  # New field: any condition unlocks
        ["traveler_identity_revealed"],
        ["companion_revealed_purpose", "found_technical_diagrams"],
        ["found_old_letter"],  # Finding the letter is enough
    ]
}
```

Update `backend/engine/validation.py` to check `locked_until_any`.

### Option C: Reduce Hidden Object Requirements

Make `creator_journal` and `old_letter` visible earlier:

```python
# backend/data/objects.py
"creator_journal": {
    ...
    "requires_flag": "found_technical_diagrams",  # Was: found_companion_origin
    "hidden": False,  # Was: True
}
"old_letter": {
    ...
    "requires_flag": "found_companion_origin",  # Was: found_creator_journal
    "hidden": False,  # Was: True
}
```

## Implementation Steps

1. Choose approach (recommend Option A + C combined)
2. Update `backend/data/rooms.py` passage lock condition
3. Update `backend/data/objects.py` visibility requirements
4. Add automatic flag progression in `backend/engine/actions.py`
5. Update narrative prompts to reflect easier progression
6. Re-run test suite to validate completion rate improves

## Success Criteria

- At least 50% of test sessions reach an ending
- Average turns to ending < 50 (currently: never reached)
- Speedrunner persona can complete in < 20 turns

## Implementation Notes (2026-01-10)

**Approach taken:** Option A + C combined, further simplified.

### Changes Made

1. **`backend/data/rooms.py`**
   - Passage `locked_until` changed from `traveler_identity_revealed` → `found_companion_origin`
   - Added `creator_journal` to archive objects list

2. **`backend/data/objects.py`**
   - `creator_journal`: `requires_flag` changed from `found_companion_origin` → `found_technical_diagrams`, `hidden` → `False`
   - `old_letter`: `requires_flag` changed from `found_creator_journal` → `found_companion_origin`, `hidden` → `False`

3. **`backend/engine/actions.py`**
   - Added auto-reveal of `traveler_identity_revealed` flag when entering passage

### Results

- **Passage accessibility**: 0% → 100% (all test personas now reach passage)
- **Ending completion**: Still 0% (requires specific trigger phrases + additional flags; addressed in IMP-0008)

### New Critical Path

```
examine technical_diagrams → found_technical_diagrams
  └─> examine companion_origin_record → found_companion_origin
      └─> passage unlocked (7-8 turns minimum)
```

The original 12+ step critical path has been reduced to 2-3 key actions.
