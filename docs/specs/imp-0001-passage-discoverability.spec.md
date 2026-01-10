# IMP-0001: Improve Discoverability of Passage

**Priority:** MEDIUM
**Category:** ux_flow
**Effort:** low
**Status:** complete

## Affected Files

- `backend/data/rooms.py`
- `backend/llm/narrative.py`

## Problem Statement

The passage room was never visited across all test sessions (0% discovery rate).

## Root Cause Analysis

1. Passage is locked behind `traveler_identity_revealed` (addressed in IMP-0005)
2. No narrative mentions of the passage until very late game
3. Archive description doesn't emphasize the passage exit

## Proposed Solution

### 1. Enhance Archive Description

```python
# backend/data/rooms.py
"archive": {
    "description": "Fragments of the world outside wash up here—objects, documents, echoes. Shelves line the walls, holding centuries of accumulated debris. Most is mundane. Some is not. To the north, a soft glow hints at something beyond—the passage, though it seems to resist approach.",
    ...
}
```

### 2. Add Passage Foreshadowing in Narrative

```python
# backend/llm/prompts.py - add to narrative context
PASSAGE_FORESHADOWING = """
When generating narrative for the archive or when the player has found_technical_diagrams:
- Occasionally mention the soft glow from the northern passage
- If player has companion_revealed_purpose, the glow should feel "inviting" or "patient"
- The companion might glance toward it meaningfully
"""
```

### 3. Mention Passage in Companion Dialogue

Add passage references to companion topics when appropriate flags are set.

## Success Criteria

- Players aware of passage existence before attempting entry
- At least 50% of sessions attempt to visit passage
