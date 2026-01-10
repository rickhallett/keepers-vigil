"""Narrative generation using Claude API."""

import hashlib
import logging
import time
from anthropic import Anthropic

from models.state import GameState
from engine.actions import ActionResult
from data.conversations import ENDINGS
from .prompts import (
    NARRATIVE_SYSTEM_PROMPT,
    OPENING_NARRATIVE_PROMPT,
    build_narrative_context,
)

logger = logging.getLogger(__name__)

# Cache for narrative responses (action + context hash -> response)
_narrative_cache: dict[str, str] = {}
_cache_stats = {"hits": 0, "misses": 0}


def _make_cache_key(action: str, context: dict, flags: dict) -> str:
    """Generate a cache key from action, context, and flags."""
    # Only cache deterministic actions (LOOK, EXAMINE with same object)
    # Don't cache TALK/ASK_ABOUT as they should feel varied
    if action not in ("LOOK", "EXAMINE", "MOVE"):
        return ""

    # Build key from relevant context
    key_parts = [
        action,
        context.get("room_id") or "",
        context.get("target") or "",
        str(sorted((k, v) for k, v in flags.items() if v)),  # Only true flags
    ]
    key_str = "|".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()


def get_cache_stats() -> dict:
    """Get cache statistics."""
    total = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = _cache_stats["hits"] / total if total > 0 else 0
    return {**_cache_stats, "total": total, "hit_rate": hit_rate}


def clear_cache():
    """Clear the narrative cache."""
    _narrative_cache.clear()
    _cache_stats["hits"] = 0
    _cache_stats["misses"] = 0


_client: Anthropic | None = None


def get_client() -> Anthropic:
    """Get or create Anthropic client."""
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


# Fallback descriptions for when LLM fails
FALLBACK_DESCRIPTIONS = {
    ("LOOK", "threshold"): "You stand at the threshold. The traveler waits nearby, flickering gently. The companion is here. Doorways lead to the keeper's cell and the archive.",
    ("LOOK", "keeper_cell"): "A small, spare room. A bed, a desk with papers, a window that looks onto nothing. Doorways lead to the threshold and the letter room.",
    ("LOOK", "archive"): "Shelves line the walls, holding centuries of objects and documents. The air is still. Doorways lead to the threshold and, beyond, the passage.",
    ("LOOK", "letter_room"): "Letters everywhere, left by travelers past. Candles burn with steady light. A doorway leads back to the keeper's cell.",
    ("LOOK", "passage"): "A doorway of soft light. Beyond it, something vast and patient waits. A doorway leads back to the archive.",
    ("EXAMINE", "technical_diagrams"): "Precise technical drawings. They seem to depict this very station, rendered with engineering precision.",
    ("EXAMINE", "keeper_journal"): "A journal with entries from many hands. Keepers past recording their experiences, their travelers, their thoughts.",
    ("EXAMINE", "keeper_logs"): "Formal logs spanning an unknowable time. One entry mentions a keeper who chose to stay when their traveler could not pass.",
    ("EXAMINE", "companion_origin_record"): "A crystalline object humming with something like life. The companion goes very still when you touch it.",
    ("EXAMINE", "creator_journal"): "A personal journal, technical and emotional. The writer built something to outlast them, to make crossing gentle.",
    ("EXAMINE", "old_letter"): "A faded letter addressed to 'Little Light.' Full of hope and love and the desire to leave something good behind.",
    ("INVENTORY", None): "You carry nothing but your purpose.",
    ("HELP", None): "Try: LOOK, EXAMINE [object], GO TO [place], TALK TO [character], ASK [character] ABOUT [topic], INVENTORY",
}


async def generate_narrative(
    action: str,
    state: GameState,
    action_result: ActionResult | None = None,
    context: str = "",
) -> str:
    """
    Generate narrative text for an action using Claude.

    Returns atmospheric narrative text.
    """
    start_time = time.perf_counter()

    # Check for help - return fixed text
    if action == "HELP":
        if action_result and action_result.message:
            return action_result.message
        return FALLBACK_DESCRIPTIONS.get(("HELP", None), "")

    # Check for inventory with no items
    if action == "INVENTORY":
        if not state.inventory:
            return "You carry nothing but your purpose here. The station provides what is needed."
        items = ", ".join(state.inventory)
        return f"You carry: {items}"

    # Build context for LLM
    result_context = action_result.context if action_result else {}
    flags_dict = state.flags.model_dump()

    # Check cache first
    cache_key = _make_cache_key(action, result_context, flags_dict)
    if cache_key and cache_key in _narrative_cache:
        _cache_stats["hits"] += 1
        elapsed = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Narrative cache hit for {action}: {elapsed:.0f}ms")
        return _narrative_cache[cache_key]

    _cache_stats["misses"] += 1

    narrative_context = build_narrative_context(
        action=action,
        context=result_context,
        flags=flags_dict,
    )

    try:
        client = get_client()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,  # Reduced from 1024 - most responses are < 300 tokens
            system=NARRATIVE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": narrative_context}],
        )

        result = response.content[0].text.strip()

        # Cache the result if cacheable
        if cache_key:
            _narrative_cache[cache_key] = result

        elapsed = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Narrative generated for {action}: {elapsed:.0f}ms")

        return result

    except Exception as e:
        logger.error(f"Narrative generation error: {e}")
        # Return fallback
        return get_fallback_narrative(action, result_context, state)


def get_fallback_narrative(action: str, context: dict, state: GameState) -> str:
    """Get fallback narrative when LLM fails."""
    target = context.get("target")

    # Try specific fallback
    fallback = FALLBACK_DESCRIPTIONS.get((action, target))
    if fallback:
        return fallback

    # Try room-based fallback for LOOK
    if action == "LOOK":
        room_id = state.current_room.value
        fallback = FALLBACK_DESCRIPTIONS.get(("LOOK", room_id))
        if fallback:
            return fallback

    # Generic fallbacks
    if action == "EXAMINE":
        base = context.get("base_description", "")
        if base:
            return base
        return f"You examine it carefully."

    if action == "MOVE":
        room_name = context.get("room_name", "the room")
        return f"You make your way to {room_name}."

    if action == "TALK":
        target = context.get("target", "them")
        return f"You speak with {target}. They listen, considering your words."

    if action == "ASK_ABOUT":
        target = context.get("target", "them")
        subject = context.get("subject", "that")
        return f"You ask {target} about {subject}. They pause before responding."

    return "You do that."


async def generate_opening_narrative() -> str:
    """Generate the opening scene narrative."""
    try:
        client = get_client()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=NARRATIVE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": OPENING_NARRATIVE_PROMPT}],
        )

        return response.content[0].text.strip()

    except Exception as e:
        print(f"Opening narrative error: {e}")
        return FALLBACK_OPENING


async def generate_ending_narrative(ending_id: str, state: GameState) -> str:
    """Generate the ending narrative."""
    ending = ENDINGS.get(ending_id)
    if not ending:
        return "The story ends."

    context = f"""Generate the ending sequence for the "{ending_id}" ending.

{ending['narrative_prompt']}

Current flags: {state.flags.model_dump()}

This is the conclusion. Make it meaningful, earned, and emotionally resonant.
End with a sense of completion but also possibility."""

    try:
        client = get_client()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=NARRATIVE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": context}],
        )

        return response.content[0].text.strip()

    except Exception as e:
        print(f"Ending narrative error: {e}")
        return ending["narrative_prompt"]


FALLBACK_OPENING = """You wake, as you have many times before.

The threshold stretches before you—stone archways framing an entrance that shifts at the edges of your vision. Light comes from everywhere and nowhere. The air is still, patient. This is the station between, and you are its keeper.

The companion is here, as always. A presence more than a form, warm and attentive. "Another has arrived," it says. "They are... confused. As they often are."

Near the archway, a figure waits. The traveler. They flicker slightly, not quite solid, not quite here. They look around with the expression of someone trying to remember a dream.

You know what to do. You have always known. But something about this one feels different.

Perhaps you should speak to the traveler, or ask your companion what they've observed. You could explore the keeper's cell or the archive. The station holds many secrets, and some of them may matter now."""
