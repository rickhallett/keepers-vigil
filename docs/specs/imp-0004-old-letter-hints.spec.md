# IMP-0004: Improve Hint System for found_old_letter

**Priority:** MEDIUM
**Category:** ux_flow
**Effort:** medium
**Status:** proposed

## Affected Files

- `backend/data/objects.py`
- `backend/llm/prompts.py`

## Problem Statement

Flag `found_old_letter` was discovered in 0/6 sessions (0%).

## Root Cause Analysis

1. Object hidden in letter_room, requires `found_creator_journal`
2. letter_room only visited 16.7% of time (1/6 sessions)
3. No connection drawn between creator_journal and letter_room

## Proposed Solution

### 1. Add Breadcrumb in Creator's Journal

```python
# backend/data/objects.py
"creator_journal": {
    ...
    "examine_extended": "The final entry mentions: 'I've left a letter in the letter room. If they ever come through here, if by some miracle they pass through... I want them to know.' The handwriting wavers at the end.",
}
```

### 2. Have Companion Mention Letter Room

When player has `found_creator_journal`:

```python
# backend/data/conversations.py
"little_light": {  # or add new topic
    ...
    "prompt_context": "... The companion might mention 'There was a letter. They told me they left it somewhere safe. The letter room, perhaps.'",
}
```

### 3. Make Letter Visible Earlier

Per IMP-0005, reduce requirement to `found_companion_origin` instead of `found_creator_journal`.

## Success Criteria

- letter_room visit rate increases to > 50%
- old_letter discovery rate increases to > 30%
