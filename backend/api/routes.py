"""API routes for the game."""

import time
import uuid
from collections import defaultdict
from fastapi import APIRouter, HTTPException, Request

from models import (
    GameState,
    CommandRequest,
    CommandResponse,
    NewGameResponse,
    StateResponse,
)
from models.state import Room
from data.rooms import ROOMS, get_visible_objects
from engine import validate_intent, execute_action, save_state, load_state
from engine.actions import check_for_ending_trigger
from llm import classify_intent, generate_narrative
from llm.narrative import generate_opening_narrative, generate_ending_narrative

router = APIRouter(prefix="/api")


# Simple in-memory rate limiter
class RateLimiter:
    """Sliding window rate limiter."""

    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] if ts > window_start
        ]

        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False

        self.requests[client_id].append(now)
        return True


rate_limiter = RateLimiter(requests_per_minute=30)


def get_client_id(request: Request) -> str:
    """Extract client identifier from request."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/new-game", response_model=NewGameResponse)
async def new_game(request: Request) -> NewGameResponse:
    """Initialize a new game session."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Too many requests")

    session_id = str(uuid.uuid4())
    state = GameState(session_id=session_id)

    await save_state(session_id, state)

    # Generate opening narrative
    opening_narrative = await generate_opening_narrative()

    # Get exits for current room
    room = ROOMS.get(state.current_room.value, {})
    exits = room.get("exits", [])

    return NewGameResponse(
        session_id=session_id,
        narrative=opening_narrative,
        current_room=state.current_room,
        inventory=state.inventory,
        exits=exits,
    )


@router.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest, req: Request) -> CommandResponse:
    """Process a player command."""
    client_id = get_client_id(req)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Too many requests")

    state = await load_state(request.session_id)

    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get current room exits
    room = ROOMS.get(state.current_room.value, {})
    exits = room.get("exits", [])

    # Check if game has ended
    if state.flags.ending_chosen:
        return CommandResponse(
            narrative="The story has ended. Start a new game to play again.",
            current_room=state.current_room,
            inventory=state.inventory,
            exits=exits,
            state_changed=False,
        )

    # Check for ending trigger first
    ending = check_for_ending_trigger(request.input, state)
    if ending:
        state.flags.ending_chosen = ending
        await save_state(request.session_id, state)

        ending_narrative = await generate_ending_narrative(ending, state)

        return CommandResponse(
            narrative=ending_narrative,
            current_room=state.current_room,
            inventory=state.inventory,
            exits=exits,
            state_changed=True,
        )

    # Step 1: Classify intent
    intent = await classify_intent(request.input, state)

    # Step 2: Validate
    validation = validate_intent(intent, state)
    if validation is not True:
        return CommandResponse(
            narrative=validation,  # Error message
            current_room=state.current_room,
            inventory=state.inventory,
            exits=exits,
            state_changed=False,
        )

    # Step 3: Execute action
    state, action_result = execute_action(intent, state)

    # Step 4: Generate narrative
    narrative = await generate_narrative(
        action=intent.intent.value,
        state=state,
        action_result=action_result,
    )

    # Step 5: Save and return
    await save_state(request.session_id, state)

    # Get updated exits after potential room change
    new_room = ROOMS.get(state.current_room.value, {})
    new_exits = new_room.get("exits", [])

    return CommandResponse(
        narrative=narrative,
        current_room=state.current_room,
        inventory=state.inventory,
        exits=new_exits,
        state_changed=True,
    )


@router.get("/state/{session_id}", response_model=StateResponse)
async def get_state(session_id: str) -> StateResponse:
    """Get current game state for UI updates."""
    state = await load_state(session_id)

    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    room_id = state.current_room.value
    room = ROOMS.get(room_id, {})
    flags_dict = state.flags.model_dump()

    visible_objects = get_visible_objects(room_id, flags_dict)

    return StateResponse(
        current_room=state.current_room,
        inventory=state.inventory,
        available_exits=room.get("exits", []),
        available_objects=visible_objects,
        available_characters=room.get("characters", []),
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
