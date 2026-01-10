# IMP-0002: Improve Hint System for found_creator_journal

**Priority:** MEDIUM
**Category:** ux_flow
**Effort:** medium
**Status:** proposed

## Affected Files

- `backend/data/objects.py`
- `backend/llm/prompts.py`

## Problem Statement

Flag `found_creator_journal` was discovered in 0/6 sessions (0%).

## Root Cause Analysis

1. Object is hidden until `found_companion_origin` flag is set
2. No hints that it exists or where to look
3. Located in archive but blends with other objects

## Proposed Solution

### 1. Add Discovery Hint to companion_origin_record

```python
# backend/data/objects.py
"companion_origin_record": {
    ...
    "examine_extended": "The companion's stillness draws your attention. Behind where the device rested, you notice documents that weren't visible before—as if the device's removal revealed something hidden.",
}
```

### 2. Have Companion Mention It

When asked about "recognition" or "purpose" after finding companion_origin_record:

```python
# backend/data/conversations.py
"recognition": {
    ...
    "prompt_context": "... The companion might glance toward the shelves where the creator's journal is hidden, as if remembering something.",
}
```

### 3. Make Object Visible Earlier

Per IMP-0005, change `requires_flag` from `found_companion_origin` to `found_technical_diagrams`.

## Success Criteria

- Discovery rate increases to > 30%
- Clear path to discovery exists in game flow
