"""Intent classification using Claude API."""

import json
import os
from anthropic import Anthropic

from models.intent import Intent, IntentType
from models.state import GameState
from data.rooms import ROOMS, get_visible_objects
from .prompts import INTENT_CLASSIFICATION_PROMPT, build_intent_context


_client: Anthropic | None = None


def get_client() -> Anthropic:
    """Get or create Anthropic client."""
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


async def classify_intent(player_input: str, state: GameState) -> Intent:
    """
    Classify player input into a structured intent using Claude.

    Returns an Intent object with the classified action.
    """
    room_id = state.current_room.value
    room = ROOMS.get(room_id, {})
    flags_dict = state.flags.model_dump()

    # Build context
    visible_objects = get_visible_objects(room_id, flags_dict)
    context = build_intent_context(
        player_input=player_input,
        current_room=room_id,
        available_objects=visible_objects,
        available_characters=room.get("characters", []),
        inventory=state.inventory,
        available_exits=room.get("exits", []),
    )

    try:
        client = get_client()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            system=INTENT_CLASSIFICATION_PROMPT,
            messages=[{"role": "user", "content": context}],
        )

        # Parse JSON response
        response_text = response.content[0].text.strip()

        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        parsed = json.loads(response_text)

        return Intent(
            intent=IntentType(parsed.get("intent", "UNKNOWN")),
            target=parsed.get("target"),
            subject=parsed.get("subject"),
            confidence=parsed.get("confidence", "medium"),
        )

    except json.JSONDecodeError:
        # Fallback for invalid JSON
        return Intent(intent=IntentType.UNKNOWN, confidence="low")

    except Exception as e:
        # Log error and return unknown intent
        print(f"Intent classification error: {e}")
        return Intent(intent=IntentType.UNKNOWN, confidence="low")


def classify_intent_sync(player_input: str, state: GameState) -> Intent:
    """Synchronous version of classify_intent."""
    import asyncio

    return asyncio.get_event_loop().run_until_complete(
        classify_intent(player_input, state)
    )
