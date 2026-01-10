# Test Playthrough

Perform an automated test playthrough of The Last Vigil using the testing framework.

## Prerequisites
Ensure the backend server is running:
```bash
cd backend && uv run uvicorn main:app --reload
```

## Running Tests

### Quick Test (Rule-based, single persona)
```bash
cd backend
uv run python run_tests.py --personas speedrunner --strategy rules
```

### Full Test Suite (All personas)
```bash
cd backend
uv run python run_tests.py --strategy rules
```

### Analyze Existing Sessions
```bash
cd backend
uv run python run_tests.py --analyze-only
```

## Available Personas
- `methodical_explorer` - Examines everything systematically
- `speedrunner` - Rushes to ending via critical path
- `confused_user` - Makes mistakes, tests error handling
- `completionist` - Finds all flags and content
- `chaotic_player` - Random/unusual inputs

## What to Check

### 1. Completion Rate
- Can all personas reach an ending?
- What's the average turn count?
- Where do personas get stuck?

### 2. Error Handling
- Are validation errors helpful?
- Do progressive hints trigger?
- Are fallback narratives used?

### 3. Narrative Quality
- Is the LLM output atmospheric?
- Are responses contextually appropriate?
- Any hallucinations or inconsistencies?

### 4. Performance
- Intent classification time
- Narrative generation time
- Any timeouts?

## Output Location
Test sessions are saved to:
```
backend/test_sessions/{persona}_{timestamp}_{id}/
├── session.json      # Full session data
└── transcript.md     # Human-readable transcript
```

Analysis summaries:
```
backend/test_sessions/summary/
├── analysis.json
├── analysis_summary.md
├── improvements.json
└── improvements.md
```

## Reporting
After running tests, summarize:
1. Pass/fail rate by persona
2. Common failure points
3. Performance metrics
4. Narrative quality assessment
5. Recommended improvements
