"""Intent classification using Claude API."""

import asyncio
import json
import logging
import os
import time
from anthropic import Anthropic

from models.intent import Intent, IntentType
from models.state import GameState
from data.rooms import ROOMS, get_visible_objects
from .prompts import INTENT_CLASSIFICATION_PROMPT, build_intent_context

logger = logging.getLogger(__name__)

# Timeout for intent classification (seconds)
INTENT_TIMEOUT = 10.0


_client: Anthropic | None = None


def get_client() -> Anthropic:
    """Get or create Anthropic client."""
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


def _classify_intent_sync(player_input: str, state: GameState) -> Intent:
    """
    Synchronous implementation of intent classification.
    Called via asyncio.to_thread for proper async timeout support.
    """
    start_time = time.perf_counter()

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

    client = get_client()
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Faster model for structured output
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

    elapsed = (time.perf_counter() - start_time) * 1000
    logger.debug(f"Intent classified in {elapsed:.0f}ms: {parsed.get('intent')}")

    return Intent(
        intent=IntentType(parsed.get("intent", "UNKNOWN")),
        target=parsed.get("target"),
        subject=parsed.get("subject"),
        confidence=parsed.get("confidence", "medium"),
    )


async def classify_intent(player_input: str, state: GameState) -> Intent:
    """
    Classify player input into a structured intent using Claude.

    Returns an Intent object with the classified action.
    Includes timeout handling - returns UNKNOWN intent on timeout.
    """
    try:
        # Run the sync API call in a thread pool with timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(_classify_intent_sync, player_input, state),
            timeout=INTENT_TIMEOUT,
        )
        return result

    except asyncio.TimeoutError:
        logger.warning(f"Intent classification timed out after {INTENT_TIMEOUT}s")
        return Intent(intent=IntentType.UNKNOWN, confidence="low")

    except json.JSONDecodeError:
        # Fallback for invalid JSON
        return Intent(intent=IntentType.UNKNOWN, confidence="low")

    except Exception as e:
        # Log error and return unknown intent
        logger.error(f"Intent classification error: {e}")
        return Intent(intent=IntentType.UNKNOWN, confidence="low")


def classify_intent_sync(player_input: str, state: GameState) -> Intent:
    """Synchronous version of classify_intent."""
    import asyncio

    return asyncio.get_event_loop().run_until_complete(
        classify_intent(player_input, state)
    )
