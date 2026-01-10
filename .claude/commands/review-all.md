# Full Code Review

Run a comprehensive review of The Last Vigil codebase covering all areas.

## Instructions

Perform reviews in this order, providing a summary for each:

1. **Backend Review** - Focus on LLM integration, API design, game engine
2. **Frontend Review** - Focus on React patterns, accessibility, performance
3. **UX Review** - Focus on player experience, discoverability, feedback
4. **Security Review** - Focus on API security, sessions, rate limiting

## Key Files to Review

### Backend
- `backend/api/routes.py` - API endpoints
- `backend/engine/actions.py` - Game logic
- `backend/engine/validation.py` - Input validation
- `backend/engine/hints.py` - Progressive hints
- `backend/llm/intent.py` - Intent classification
- `backend/llm/narrative.py` - Narrative generation
- `backend/models/state.py` - Game state model
- `backend/data/rooms.py`, `objects.py`, `conversations.py` - Game data

### Frontend
- `frontend/src/App.tsx` - Main app
- `frontend/src/components/*.tsx` - UI components
- `frontend/src/hooks/*.ts` - Custom hooks
- `frontend/src/styles/game.css` - Styling

## Known Issues Checklist

### Critical (Must Check)
- [ ] Blocking async calls in narrative generation
- [ ] No session expiration/cleanup
- [ ] No rate limiting on API

### High Priority
- [ ] Module-level `entryId` in useGameState
- [ ] NarrativeEntryComponent not memoized
- [ ] Missing aria-labels on inputs
- [ ] `print()` instead of logger in narrative.py

### Medium Priority
- [ ] Duplicate `get_client()` functions
- [ ] Quick actions hidden on desktop
- [ ] Object names show as snake_case in errors

## Output Format

Provide an executive summary followed by categorized findings:

```
## Executive Summary
[2-3 sentences on overall code health]

## Critical Issues
[List with file:line references]

## High Priority
[List with file:line references]

## Medium Priority
[List with file:line references]

## Low Priority
[List with file:line references]

## Recommendations
[Top 5 actionable items]
```
