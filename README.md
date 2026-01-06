# The Last Vigil

A browser-based text adventure game with LLM-powered natural language input. Players type freeform commands; the system classifies intent and advances a deterministic state machine while the LLM generates atmospheric narrative.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Anthropic API key

### Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Using uv (recommended)
uv sync
uv run uvicorn main:app --reload

# Or using pip
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn main:app --reload
```

Backend runs at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173

## Architecture

```
Frontend (React)     -->    Backend (FastAPI)    -->    Claude API
- Narrative display         - Intent classification      - Structured output (intent)
- Command input             - Game state machine         - Creative output (narrative)
- Typewriter effect         - Validation layer
```

## Project Structure

```
keepers-vigil/
├── backend/
│   ├── api/           # FastAPI routes
│   ├── data/          # Game content (rooms, objects, conversations)
│   ├── engine/        # Game logic (validation, actions, state)
│   ├── llm/           # Claude API integration
│   ├── models/        # Pydantic models
│   └── main.py        # Application entry
├── frontend/
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/# React components
│   │   ├── hooks/     # Custom hooks
│   │   └── styles/    # CSS
│   └── index.html
└── docs/
    └── specs/         # Technical specifications
```

## Game Commands

Natural language is supported. Examples:

- `look around` - Describe current location
- `examine the diagrams` - Study an object
- `go to the archive` - Move to another room
- `talk to the companion` - Speak with a character
- `ask companion about the traveler` - Ask about a topic
- `inventory` - Check what you carry

## Development

See [docs/specs/implementation-plan.md](docs/specs/implementation-plan.md) for implementation details.

## License

MIT
