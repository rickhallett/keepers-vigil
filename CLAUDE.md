# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Last Vigil is a browser-based text adventure game with LLM-powered natural language input. Players type freeform commands; the system classifies intent and advances a deterministic state machine while Claude generates atmospheric narrative.

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend
uv sync                              # Install dependencies
uv run uvicorn main:app --reload     # Run dev server (port 8000)
uv run pytest                        # Run tests
```

### Frontend (React/TypeScript/Vite)
```bash
cd frontend
npm install                          # Install dependencies
npm run dev                          # Run dev server (port 5173)
npm run build                        # Build for production
npm run lint                         # Run ESLint
```

## Architecture

### Command Processing Flow
Each player command follows this sequence:
1. **Intent Classification** (`llm/intent.py`) - Claude parses natural language into structured intent (JSON)
2. **Validation** (`engine/validation.py`) - Checks if action is valid in current state
3. **Action Execution** (`engine/actions.py`) - Deterministic state machine updates game state
4. **Narrative Generation** (`llm/narrative.py`) - Claude generates atmospheric response text

The LLM never controls game logic directly; all state changes go through the deterministic engine.

### Two LLM Call Patterns
- **Intent classification**: Structured JSON output, fast, uses system prompt from `llm/prompts.py`
- **Narrative generation**: Creative text, atmospheric, context-aware

### Flag-Based Progression
Game progression uses boolean flags (`models/state.py:GameFlags`):
- Hidden objects unlock via prerequisite flags
- Conversations gate behind discovery flags
- Three endings require specific flag combinations

### Session Storage
In-memory dict storage in `engine/state_store.py`. Game state includes current room, inventory, flags, and turn count.

## Key Files

- `backend/api/routes.py` - Three endpoints: `/api/new-game`, `/api/command`, `/api/state/{session_id}`
- `backend/data/rooms.py` - Room definitions with exits, objects, characters
- `backend/data/objects.py` - Examinable objects with flag triggers
- `backend/data/conversations.py` - Traveler/Companion dialogue trees and endings
- `frontend/src/hooks/useGameState.ts` - React state management and API calls
- `frontend/src/hooks/useTypewriter.ts` - Typewriter text effect

## Environment Variables

Backend requires `ANTHROPIC_API_KEY` in `backend/.env` (copy from `.env.example`).
