# the last vigil - implementation plan

## overview

Browser-based text adventure game with LLM-powered natural language input. FastAPI backend + React/TypeScript frontend + Claude API integration.

**stack:** Python (FastAPI) + React (TypeScript/Vite) + Anthropic Claude API

---

## phase 1: project scaffolding

### backend setup
- create `backend/` directory structure
- initialize python project with `pyproject.toml`
- dependencies: fastapi, uvicorn, anthropic, pydantic, python-dotenv
- create `.env.example` with required vars

### frontend setup
- create `frontend/` with vite + react + typescript
- dependencies: react, typescript, vite
- basic project structure

### root config
- `.gitignore` for python + node
- root `README.md` with setup instructions

---

## phase 2: backend core

### game state models (`backend/models/`)
```
models/
├── __init__.py
├── state.py      # GameState, GameFlags, Room enum
├── intent.py     # Intent classification schema
└── requests.py   # API request/response models
```

### game data (`backend/data/`)
```
data/
├── __init__.py
├── rooms.py      # ROOMS dictionary (5 rooms)
├── objects.py    # OBJECTS dictionary with discovery triggers
└── conversations.py  # Traveler + Companion topic handlers
```

### game engine (`backend/engine/`)
```
engine/
├── __init__.py
├── validation.py  # validate_intent()
├── actions.py     # execute_action() - deterministic state changes
└── state_store.py # In-memory session storage
```

### claude integration (`backend/llm/`)
```
llm/
├── __init__.py
├── intent.py     # classify_intent() - structured output
├── narrative.py  # generate_narrative() - creative text
└── prompts.py    # System prompts for both modes
```

### api endpoints (`backend/api/`)
```
api/
├── __init__.py
└── routes.py     # /new-game, /command, /state endpoints
```

### main app (`backend/main.py`)
- fastapi app creation
- cors middleware for frontend
- router mounting

---

## phase 3: frontend core

### components (`frontend/src/components/`)
```
components/
├── NarrativeDisplay.tsx  # Scrolling text log
├── CommandInput.tsx      # Text input + submit
├── StatusBar.tsx         # Room + inventory indicator
└── LoadingIndicator.tsx  # "..." while waiting
```

### hooks (`frontend/src/hooks/`)
```
hooks/
├── useGameState.ts   # Session management, API calls
└── useTypewriter.ts  # Typewriter effect
```

### api client (`frontend/src/api/`)
```
api/
└── client.ts  # Fetch wrapper for backend
```

### styling (`frontend/src/styles/`)
- dark theme, minimal chrome
- typography: monospace/serif
- speaker differentiation (narrator, companion, traveler)

---

## phase 4: game logic

### complete object system
- all 8 key objects with examine_base text
- flag triggers (sets_flag, requires_flag)
- hidden object revelation logic

### conversation state machine
- traveler conversation progression (4 stages)
- companion topic handler (12 topics)
- flag-gated responses

### ending system
- three endings: truth, peace, stay
- required flag checks
- ending narrative prompts

---

## phase 5: polish & integration

### error handling
- llm timeout fallbacks
- pre-written fallback descriptions
- invalid command graceful handling

### frontend polish
- typewriter effect tuning
- mobile responsiveness
- loading states

### testing
- full playthrough verification
- flag progression validation
- edge case handling

---

## file creation order

**backend (ordered):**
1. `backend/pyproject.toml`
2. `backend/.env.example`
3. `backend/models/state.py`
4. `backend/models/intent.py`
5. `backend/data/rooms.py`
6. `backend/data/objects.py`
7. `backend/engine/state_store.py`
8. `backend/engine/validation.py`
9. `backend/engine/actions.py`
10. `backend/llm/prompts.py`
11. `backend/llm/intent.py`
12. `backend/llm/narrative.py`
13. `backend/api/routes.py`
14. `backend/main.py`

**frontend (ordered):**
1. initialize with vite
2. `frontend/src/api/client.ts`
3. `frontend/src/hooks/useGameState.ts`
4. `frontend/src/hooks/useTypewriter.ts`
5. `frontend/src/components/NarrativeDisplay.tsx`
6. `frontend/src/components/CommandInput.tsx`
7. `frontend/src/components/StatusBar.tsx`
8. `frontend/src/App.tsx`
9. `frontend/src/styles/game.css`

---

## key architecture decisions

1. **two llm call patterns per command:**
   - intent classification (structured json, fast)
   - narrative generation (creative text, atmospheric)

2. **deterministic game engine:**
   - llm never controls game logic
   - all state changes through validated actions

3. **flag-based progression:**
   - hidden objects unlock via prerequisite flags
   - conversations gate behind discovery flags
   - endings require specific flag combinations

4. **in-memory sessions:**
   - simple dict storage for demo
   - easy swap to redis/sqlite later

---

## environment variables

```
ANTHROPIC_API_KEY=sk-ant-...
ENVIRONMENT=development
```

---

## run commands

```bash
# backend
cd backend && uv run uvicorn main:app --reload

# frontend
cd frontend && npm run dev
```
