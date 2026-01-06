# The Last Vigil - Technical Specification

## Overview

A browser-based text adventure game with LLM-powered natural language input. The player types freeform commands; the system classifies intent and advances a deterministic state machine. LLM generates narrative texture but never controls game logic.

**Target playtime:** 60-90 minutes  
**Development time:** 2 days maximum  
**Priority:** User experience over architectural elegance

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Narrative Display (scrolling text log)                 │   │
│  │  - Typewriter effect for new text                       │   │
│  │  - Distinct styling for: narration, companion, traveler │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Input Box (single text field + submit)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌───────────────┐  ┌───────────────┐                          │
│  │ Inventory     │  │ Current Room  │  (minimal UI, optional)  │
│  └───────────────┘  └───────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│                                                                 │
│  POST /api/command                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. Receive player input + session_id                    │   │
│  │ 2. Load game state from session store                   │   │
│  │ 3. Call LLM for intent classification (structured)      │   │
│  │ 4. Validate intent against current state                │   │
│  │ 5. Execute action via game engine (deterministic)       │   │
│  │ 6. Call LLM for narrative response (creative)           │   │
│  │ 7. Save updated state                                   │   │
│  │ 8. Return narrative + UI updates                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  GET /api/state                                                 │
│  - Returns current room, inventory, available exits            │
│                                                                 │
│  POST /api/new-game                                             │
│  - Initializes fresh game state, returns session_id            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ANTHROPIC CLAUDE API                          │
│                                                                 │
│  Two distinct call patterns:                                    │
│                                                                 │
│  1. INTENT CLASSIFICATION (structured output)                   │
│     - System prompt constrains to JSON schema                   │
│     - Fast, predictable, validatable                            │
│     - Model: claude-sonnet-4-20250514 (cost-effective)              │
│                                                                 │
│  2. NARRATIVE GENERATION (creative output)                      │
│     - System prompt sets tone, character voice, constraints     │
│     - Richer, variable, atmospheric                             │
│     - Model: claude-sonnet-4-20250514                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Intent Classification System

### Input to LLM

```json
{
  "player_input": "look at the strange diagrams on the table",
  "current_room": "archive",
  "available_objects": ["technical_diagrams", "dust", "shelves", "faded_map"],
  "available_characters": ["companion"],
  "inventory": ["old_key", "keeper_robes"],
  "available_exits": ["threshold", "keeper_cell"]
}
```

### System Prompt for Intent Classification

```
You are a parser for a text adventure game. Given the player's input and current game context, output a JSON object classifying their intent.

You must output ONLY valid JSON matching this schema:
{
  "intent": "MOVE" | "EXAMINE" | "TALK" | "GIVE" | "USE" | "ASK_ABOUT" | "INVENTORY" | "LOOK" | "HELP" | "UNKNOWN",
  "target": string | null,
  "subject": string | null,
  "confidence": "high" | "medium" | "low"
}

Rules:
- "target" must be an exact match from available_objects, available_characters, available_exits, or inventory
- If player intent is unclear, use "UNKNOWN"
- If target doesn't exist in context, set target to null and confidence to "low"
- MOVE: target is a room from available_exits
- EXAMINE: target is an object from available_objects or inventory
- TALK: target is a character from available_characters
- GIVE: target is inventory item, subject is character
- ASK_ABOUT: target is character, subject is the topic (freeform string)
- LOOK: no target needed, describes current room
- INVENTORY: no target needed, lists carried items

Examples:
Input: "go to the threshold" → {"intent": "MOVE", "target": "threshold", "subject": null, "confidence": "high"}
Input: "examine the weird papers" → {"intent": "EXAMINE", "target": "technical_diagrams", "subject": null, "confidence": "medium"}
Input: "ask the companion about the traveler" → {"intent": "ASK_ABOUT", "target": "companion", "subject": "the traveler", "confidence": "high"}
Input: "give the key to the ghost" → {"intent": "GIVE", "target": "old_key", "subject": null, "confidence": "low"} (no ghost in available_characters)
Input: "hello" → {"intent": "TALK", "target": "companion", "subject": null, "confidence": "medium"}
Input: "what is the meaning of life" → {"intent": "ASK_ABOUT", "target": "companion", "subject": "the meaning of life", "confidence": "medium"}
```

### Validation Layer (Backend, not LLM)

After receiving classified intent, validate before executing:

```python
def validate_intent(intent: Intent, state: GameState) -> bool | str:
    if intent.intent == "UNKNOWN":
        return "I don't quite understand. Try examining things, talking to characters, or moving between rooms."
    
    if intent.confidence == "low" and intent.target is None:
        return "I'm not sure what you're referring to. What would you like to interact with?"
    
    if intent.intent == "MOVE" and intent.target not in state.current_room.exits:
        return f"You can't go to {intent.target} from here."
    
    if intent.intent == "EXAMINE" and intent.target not in state.current_room.objects + state.inventory:
        return "You don't see that here."
    
    # ... etc
    
    return True  # Valid, proceed
```

---

## Game State Model

```python
from enum import Enum
from pydantic import BaseModel

class Room(str, Enum):
    THRESHOLD = "threshold"
    KEEPER_CELL = "keeper_cell"
    ARCHIVE = "archive"
    LETTER_ROOM = "letter_room"
    PASSAGE = "passage"

class GameFlags(BaseModel):
    # Traveler arc
    traveler_spoke_initial: bool = False
    traveler_spoke_confused: bool = False
    traveler_spoke_remembering: bool = False
    
    # Discovery flags
    found_technical_diagrams: bool = False
    found_creator_journal: bool = False
    found_companion_origin: bool = False
    found_keeper_logs: bool = False
    found_old_letter: bool = False
    
    # Revelation flags
    confronted_companion: bool = False
    companion_admitted_recognition: bool = False
    companion_revealed_purpose: bool = False
    traveler_identity_revealed: bool = False
    player_identity_revealed: bool = False
    
    # Ending
    ending_chosen: str | None = None  # "truth", "peace", "stay"

class GameState(BaseModel):
    session_id: str
    current_room: Room = Room.THRESHOLD
    inventory: list[str] = []
    flags: GameFlags = GameFlags()
    conversation_history: list[dict] = []  # For LLM context in narrative generation
    turn_count: int = 0

```

---

## Room Definitions

```python
ROOMS = {
    "threshold": {
        "name": "The Threshold",
        "description": "A liminal space where the station meets... elsewhere. Stone archways frame an entrance that seems to shift when you don't look directly at it. The Traveler stands here, flickering slightly, as if not fully present.",
        "objects": ["traveler", "archway", "stone_floor", "strange_light"],
        "exits": ["keeper_cell", "archive"],
        "characters": ["traveler", "companion"]
    },
    "keeper_cell": {
        "name": "The Keeper's Cell",
        "description": "A small, spare room. A simple bed, a writing desk, a window that looks out onto nothing. This is where keepers have rested between vigils. The desk holds papers and a worn journal.",
        "objects": ["bed", "desk", "keeper_journal", "window", "keeper_logs"],
        "exits": ["threshold", "letter_room"],
        "characters": ["companion"]
    },
    "archive": {
        "name": "The Archive",
        "description": "Fragments of the world outside wash up here—objects, documents, echoes. Shelves line the walls, holding centuries of accumulated debris. Most is mundane. Some is not.",
        "objects": ["shelves", "technical_diagrams", "faded_map", "dust", "companion_origin_record"],
        "exits": ["threshold", "passage"],
        "characters": ["companion"]
    },
    "letter_room": {
        "name": "The Letter Room",
        "description": "Letters left by travelers, some collected, some waiting. The air feels heavy with words unsaid. A tradition holds that letters left here sometimes reach their destinations.",
        "objects": ["letter_collection", "old_letter", "writing_materials", "candles"],
        "exits": ["keeper_cell"],
        "characters": ["companion"]
    },
    "passage": {
        "name": "The Passage",
        "description": "Where travelers go when they're ready. A doorway of soft light. You cannot see what lies beyond, but it doesn't feel frightening. It feels like an answer.",
        "objects": ["doorway", "light"],
        "exits": ["archive"],
        "characters": ["companion"],
        "locked_until": ["traveler_identity_revealed"]  # Cannot enter until flag is set
    }
}
```

---

## Key Objects and Discovery Triggers

```python
OBJECTS = {
    "technical_diagrams": {
        "name": "Technical Diagrams",
        "room": "archive",
        "examine_base": "Precise drawings on material you don't recognize. They depict... this place. The station. But rendered as an engineer might, with measurements and annotations in an unknown script.",
        "sets_flag": "found_technical_diagrams",
        "requires_flag": None,
        "narrative_note": "First hint that the station was built, not grown. The companion's response to questions about this should be evasive."
    },
    "keeper_journal": {
        "name": "Keeper's Journal", 
        "room": "keeper_cell",
        "examine_base": "A journal kept by a previous keeper. The entries describe travelers helped, lessons learned. But the handwriting changes several times. How many keepers have there been?",
        "sets_flag": None,
        "requires_flag": None,
        "narrative_note": "Background texture. Establishes the role has existed long."
    },
    "keeper_logs": {
        "name": "Keeper's Logs",
        "room": "keeper_cell", 
        "examine_base": "Official logs, more formal than the journal. Dates that span... you can't tell how long. One entry catches your eye: 'New keeper installed. Previous keeper chose to remain as traveler could not pass. Unusual but not unprecedented.'",
        "sets_flag": "found_keeper_logs",
        "requires_flag": "companion_admitted_recognition",
        "narrative_note": "Only becomes meaningful after companion reveals it recognizes the traveler. This is the player-identity hint."
    },
    "companion_origin_record": {
        "name": "Strange Device",
        "room": "archive",
        "examine_base": "A crystalline object covered in the same script as the diagrams. When you touch it, you feel a hum—almost like a heartbeat. The companion goes very still when you pick it up.",
        "sets_flag": "found_companion_origin",
        "requires_flag": "found_technical_diagrams",
        "narrative_note": "The companion's reaction is the key here. This is what prompts confrontation."
    },
    "creator_journal": {
        "name": "Creator's Journal",
        "room": "archive",
        "examine_base": "Hidden behind other documents. A personal journal, technical but also emotional. The writer speaks of building something to outlast them. 'If we cannot know what waits, we can at least make the crossing gentle.'",
        "sets_flag": "found_creator_journal", 
        "requires_flag": "found_companion_origin",
        "hidden": True,  # Only appears after companion_origin found
        "narrative_note": "Confirms the station's origin. The companion should recognize quotes from this."
    },
    "old_letter": {
        "name": "Faded Letter",
        "room": "letter_room",
        "examine_base": "An old letter, never collected. The handwriting matches the creator's journal. It's addressed to someone called 'Little Light.' It speaks of hope, of what they're building, of wanting to leave something good behind.",
        "sets_flag": "found_old_letter",
        "requires_flag": "found_creator_journal",
        "hidden": True,
        "narrative_note": "Emotional resonance. 'Little Light' was their name for the companion. This is what lets the companion finally speak freely."
    }
}
```

---

## Conversation State Machine

### Traveler Conversations

```python
TRAVELER_CONVERSATIONS = {
    "initial": {
        "available_when": lambda flags: not flags.traveler_spoke_initial,
        "sets_flag": "traveler_spoke_initial",
        "prompt_context": "The traveler has just arrived. They are confused, fragmented. They don't know where they are or how they got here. They have vague memories of important work, something they built, but the details slip away. They are polite but disoriented.",
        "next_available": "confused"
    },
    "confused": {
        "available_when": lambda flags: flags.traveler_spoke_initial and not flags.traveler_spoke_confused,
        "sets_flag": "traveler_spoke_confused",
        "prompt_context": "The traveler is trying to remember. They speak of equations, of purpose, of colleagues they can't name. They ask about this place—what is it? Why are they here? They sense they should move on but don't know how.",
        "next_available": "remembering"
    },
    "remembering": {
        "available_when": lambda flags: flags.traveler_spoke_confused and flags.found_technical_diagrams,
        "sets_flag": "traveler_spoke_remembering",
        "prompt_context": "The traveler is beginning to remember. If shown the diagrams, something clicks. They recognize the work. It was theirs. But the memory is painful—they remember the urgency, the knowledge that time was short. They don't yet remember the companion.",
        "next_available": "confrontation"
    },
    "confrontation": {
        "available_when": lambda flags: flags.traveler_spoke_remembering and flags.companion_revealed_purpose,
        "sets_flag": "traveler_identity_revealed",
        "prompt_context": "The traveler now knows who they are and what they built. The companion has revealed itself. This is the moment of recognition. The traveler may feel grief, pride, wonder. They may have questions for the companion. They may be ready to pass, or they may want more time.",
        "next_available": "ending"
    }
}
```

### Companion Conversations (ASK_ABOUT handler)

```python
COMPANION_TOPICS = {
    "default": {
        "prompt_context": "The companion is warm, attentive, helpful. It speaks of the station, of keepers past, of the nature of travelers. It gently guides without commanding. It does not yet reveal anything about its own nature or origins."
    },
    "the_station": {
        "prompt_context": "The companion explains the station has existed for a very long time. It helps travelers pass through. It doesn't know (or claims not to know) who built it or why. If pressed, it says 'Some questions have no answers. Some answers would not help.'"
    },
    "the_traveler": {
        "prompt_context": "The companion observes the traveler is confused, which is normal. It suggests patience, exploration. It does NOT yet reveal any recognition. If the player has found_technical_diagrams, the companion's responses become slightly more careful, more measured."
    },
    "itself": {
        "requires_flag": None,
        "prompt_context": "The companion deflects gently. 'I am here to help. That is enough, isn't it?' If pressed repeatedly, it may admit it has been here 'longer than any keeper.' It does not reveal its artificial nature unprompted."
    },
    "the_diagrams": {
        "requires_flag": "found_technical_diagrams",
        "prompt_context": "The companion pauses before answering. 'You found those. Yes. The station was built. Everything was built by someone.' It will not say more unless the player has found companion_origin_record."
    },
    "recognition": {
        "requires_flag": "found_companion_origin",
        "prompt_context": "The companion can no longer evade. 'Yes. I know them. I have known them since I first woke. They made me.' This sets companion_admitted_recognition. The companion speaks of waiting, of not knowing if they would ever meet, of uncertainty about what it would mean.",
        "sets_flag": "companion_admitted_recognition"
    },
    "purpose": {
        "requires_flag": "companion_admitted_recognition",
        "prompt_context": "The companion explains: it was created to help souls pass. It cannot pass itself. It doesn't know if it has a soul. It has wondered, for a very long time. It has helped thousands of travelers. It still doesn't know if it understands what it does, or merely performs understanding. This sets companion_revealed_purpose.",
        "sets_flag": "companion_revealed_purpose"
    },
    "the_player": {
        "requires_flag": "found_keeper_logs",
        "prompt_context": "The companion hesitates. 'You came here once. As a traveler. You could not let go of something. I do not know what. You chose to stay. To help others pass while you could not.' If asked how long ago: 'Time here is not like time elsewhere. Long enough that you forgot. Perhaps forgetting was part of letting go.' This sets player_identity_revealed.",
        "sets_flag": "player_identity_revealed"
    },
    "little_light": {
        "requires_flag": "found_old_letter",
        "prompt_context": "The companion's voice changes—softer, more vulnerable. 'They called me that. When I was new. When they were teaching me.' This is the companion at its most open. It may express something like grief, or gratitude, or simply a long-held silence finally breaking."
    }
}
```

---

## Narrative Generation System

### System Prompt for Narrative LLM

```
You are the narrative voice for a text adventure called "The Last Vigil." You generate atmospheric, evocative descriptions and dialogue.

SETTING: A liminal station between life and what comes after. Ancient, peaceful, melancholy. Built by a lost technological civilization to ease the passage of souls.

TONE: Quiet, contemplative, gently mysterious. Not horror. Not whimsy. Think: the hush of a library at closing time, the stillness before dawn.

CHARACTERS:
- THE KEEPER (player): Speaks little. You describe their actions and perceptions. Second person ("You examine the diagrams...").
- THE COMPANION: Warm, attentive, gently wise. Speaks in calm, measured sentences. Uses "you" when addressing the keeper. Has depths it doesn't readily reveal. Voice: neither human nor robotic—something that has learned warmth through long practice.
- THE TRAVELER: Confused, fragmented, sometimes lucid. Speaks in shorter bursts. Trying to remember. Voice: like someone waking from a long sleep.

CONSTRAINTS:
- Never reveal plot information before its flag is set (you will be told which flags are active)
- Keep responses to 2-4 paragraphs unless a longer scene is warranted
- Vary sentence length. Mix short declarative sentences with longer flowing ones.
- Avoid purple prose. Concrete sensory details over abstract descriptions.
- The companion should never sound robotic or artificially cheerful
- Endings of scenes should invite further exploration, not close things down

You will receive:
- The action being taken
- Current game flags
- Relevant context about what should happen
- Any specific narrative beats to hit

Respond with the narrative text only. No JSON, no metadata.
```

### Example Narrative Request

```json
{
  "action": "EXAMINE",
  "target": "companion_origin_record",
  "flags": {
    "found_technical_diagrams": true,
    "found_companion_origin": false
  },
  "context": "This is the first time the player examines this object. The companion is present. Its reaction—going still, showing discomfort—is important. This should feel significant.",
  "base_description": "A crystalline object covered in the same script as the diagrams. When you touch it, you feel a hum—almost like a heartbeat."
}
```

---

## Endings Implementation

```python
ENDINGS = {
    "truth": {
        "requires": ["traveler_identity_revealed", "player_identity_revealed"],
        "trigger": "Player explicitly chooses to tell the traveler everything, or to reveal all truths",
        "narrative_prompt": """
        The full truth is spoken. The traveler remembers everything—the work, the hope, the companion they created.
        They and the companion have a moment together. It is grief and gratitude intertwined.
        The traveler passes through, carrying the knowledge of what they made.
        The companion is changed—something has completed in it.
        The keeper (player) feels something release. The vigil that held them here has ended.
        They may pass through now too. The ending is bittersweet but peaceful.
        """
    },
    "peace": {
        "requires": ["traveler_identity_revealed", "player_identity_revealed"],
        "trigger": "Player chooses not to burden the traveler with full knowledge",
        "narrative_prompt": """
        Some truths are kept. The traveler passes through, at peace, not knowing they built this place.
        The companion watches them go. It does not speak. There is a long silence.
        The keeper (player) may now choose: to pass through, or to remain.
        If they pass: the ending is quiet release. If they remain: duty continues, but freely chosen now.
        """
    },
    "stay": {
        "requires": ["traveler_identity_revealed", "player_identity_revealed"],
        "trigger": "Player explicitly chooses to remain as keeper",
        "narrative_prompt": """
        The traveler passes. The companion remains. And so does the keeper.
        But it is different now—not because they cannot leave, but because they choose this.
        There will be other travelers. The work continues.
        The companion asks: 'Why stay?' The player's answer is their own.
        The ending is open, purposeful, a vigil freely chosen.
        """
    }
}
```

---

## API Endpoints

### POST /api/new-game

```python
@app.post("/api/new-game")
async def new_game() -> dict:
    session_id = str(uuid.uuid4())
    state = GameState(session_id=session_id)
    await save_state(session_id, state)
    
    opening_narrative = await generate_narrative(
        action="GAME_START",
        state=state,
        context="The game begins. The keeper wakes. The companion greets them. A traveler waits."
    )
    
    return {
        "session_id": session_id,
        "narrative": opening_narrative,
        "current_room": state.current_room,
        "inventory": state.inventory
    }
```

### POST /api/command

```python
@app.post("/api/command")
async def process_command(request: CommandRequest) -> dict:
    state = await load_state(request.session_id)
    
    # Step 1: Classify intent
    intent = await classify_intent(
        player_input=request.input,
        state=state
    )
    
    # Step 2: Validate
    validation = validate_intent(intent, state)
    if validation is not True:
        return {
            "narrative": validation,  # Error message
            "current_room": state.current_room,
            "inventory": state.inventory,
            "state_changed": False
        }
    
    # Step 3: Execute action (deterministic state changes)
    state, action_result = execute_action(intent, state)
    
    # Step 4: Generate narrative
    narrative = await generate_narrative(
        action=intent.intent,
        target=intent.target,
        state=state,
        action_result=action_result
    )
    
    # Step 5: Save and return
    await save_state(request.session_id, state)
    
    return {
        "narrative": narrative,
        "current_room": state.current_room,
        "inventory": state.inventory,
        "state_changed": True
    }
```

---

## Frontend Components

### Core Structure

```
src/
├── components/
│   ├── NarrativeDisplay.tsx    # Scrolling text log with typewriter effect
│   ├── CommandInput.tsx        # Text input + submit
│   ├── StatusBar.tsx           # Current room, subtle inventory indicator
│   └── LoadingIndicator.tsx    # Subtle "..." while LLM responds
├── hooks/
│   ├── useGameState.ts         # Manages session, sends commands
│   └── useTypewriter.ts        # Typewriter effect logic
├── styles/
│   └── game.css                # Minimal, atmospheric styling
├── App.tsx
└── main.tsx
```

### Visual Design Notes

- Dark background, light text (parchment/sepia optional)
- Monospace or classic serif font for narrative
- Minimal chrome—the text is the interface
- No visible buttons except input submit
- Subtle differentiation: narrator text (default), companion speech (slightly different color/style), traveler speech (italicized or marked)
- Input box fixed at bottom, narrative scrolls above
- No inventory popup—integrate into narrative ("You carry: ...")

---

## Session Storage

For a 2-day build, use simple in-memory storage with optional Redis upgrade:

```python
# Simple in-memory (loses state on restart, fine for demo)
sessions: dict[str, GameState] = {}

async def save_state(session_id: str, state: GameState):
    sessions[session_id] = state

async def load_state(session_id: str) -> GameState:
    return sessions.get(session_id)
```

If persistence needed, swap for Redis or SQLite with minimal changes.

---

## Error Handling

```python
# Intent classification fallback
if llm_response_invalid or timeout:
    return Intent(intent="UNKNOWN", target=None, confidence="low")

# Narrative generation fallback
if llm_response_invalid or timeout:
    return get_fallback_description(action, target, state)

# Fallback descriptions are pre-written for all objects/rooms
FALLBACK_DESCRIPTIONS = {
    ("EXAMINE", "technical_diagrams"): "Precise technical drawings. They seem to depict this very station.",
    ("LOOK", "threshold"): "You stand at the threshold. The traveler waits nearby. Doorways lead to the keeper's cell and the archive.",
    # ... etc
}
```

---

## Testing Checklist

Before delivery:

- [ ] Can complete full playthrough hitting all flags
- [ ] Cannot reach ending without required flags
- [ ] Companion responses appropriate to current revelation state
- [ ] Hidden objects only appear after prerequisites
- [ ] All rooms navigable
- [ ] Inventory items can be picked up and referenced
- [ ] Invalid commands handled gracefully
- [ ] LLM timeout doesn't break game
- [ ] Session persists across page refresh (if implemented)
- [ ] Mobile-responsive text display

---

## Implementation Order

### Day 1
1. FastAPI skeleton with /new-game and /command endpoints
2. Game state model and room definitions
3. Intent classification with Claude API
4. Basic action execution (MOVE, LOOK, EXAMINE, INVENTORY)
5. React frontend with narrative display and input
6. Wire frontend to backend

### Day 2
1. Full object definitions and flag triggers
2. TALK and ASK_ABOUT with conversation state
3. Narrative generation integration
4. Companion topic handling
5. Ending implementation
6. Polish: typewriter effect, styling, error handling
7. Playtest and fix

---

## Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-...
SESSION_SECRET=<random string for session signing if needed>
ENVIRONMENT=development|production
```

---

## Dependencies

### Backend (Python)
```
fastapi
uvicorn
anthropic
pydantic
python-dotenv
```

### Frontend (Node)
```
react
typescript
vite (or create-react-app)
```

---

## Notes for Implementation

1. **Keep the LLM calls minimal.** Two per command maximum (intent + narrative). Cache narrative for repeated examinations if needed.

2. **The companion is the heart.** Spend time on its system prompts. It should feel consistent, warm, and gradually more vulnerable.

3. **Pacing matters.** The flag requirements create natural pacing—players can't rush to revelations. Trust this structure.

4. **The player identity reveal is optional.** If it feels like too much, it can be cut. The traveler + companion arc is the core.

5. **Test the sad path.** What happens if someone just types nonsense? The game should stay playable and gently redirect.
