# IMP-0003: Improve Hint System for found_companion_origin

**Priority:** MEDIUM
**Category:** ux_flow
**Effort:** medium
**Status:** proposed

## Affected Files

- `backend/data/objects.py`
- `backend/llm/prompts.py`

## Problem Statement

Flag `found_companion_origin` was discovered in 0/6 sessions (0%).

## Root Cause Analysis

1. Object requires `found_technical_diagrams` (83.3% discovery rate)
2. Object name is vague ("Strange Device" / `companion_origin_record`)
3. No hints connecting diagrams to the device

## Proposed Solution

### 1. Connect Diagrams to Device Narratively

```python
# backend/data/objects.py
"technical_diagrams": {
    ...
    "examine_extended": "Among the annotations, one symbol appears repeatedly—the same symbol you notice etched into a crystalline device resting on a nearby shelf.",
}
```

### 2. Make Object Name More Discoverable

```python
"companion_origin_record": {
    "name": "Crystalline Device",  # Was: "Strange Device"
    ...
}
```

### 3. Have Companion React to Diagram Discovery

```python
# backend/llm/prompts.py - add to narrative generation
When player examines technical_diagrams:
- Companion should shift attention toward the crystalline device
- Narrative should mention "The companion's gaze drifts to something on the shelves"
```

## Success Criteria

- Discovery rate increases to > 50%
- Players naturally progress from diagrams to device
