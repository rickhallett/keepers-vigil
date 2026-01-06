"""Deterministic action execution - modifies game state."""

from models.state import GameState, Room
from models.intent import Intent, IntentType
from data.rooms import ROOMS, get_visible_objects
from data.objects import OBJECTS
from data.conversations import (
    TRAVELER_CONVERSATIONS,
    COMPANION_TOPICS,
    ENDINGS,
    get_traveler_conversation_state,
    get_companion_topic,
    can_trigger_ending,
)


class ActionResult:
    """Result of executing an action."""

    def __init__(
        self,
        success: bool,
        message: str = "",
        context: dict | None = None,
        narrative_prompt: str = "",
    ):
        self.success = success
        self.message = message
        self.context = context or {}
        self.narrative_prompt = narrative_prompt


def execute_action(intent: Intent, state: GameState) -> tuple[GameState, ActionResult]:
    """
    Execute a validated intent, modifying game state.

    Returns updated state and action result with context for narrative generation.
    """
    state.turn_count += 1

    if intent.intent == IntentType.MOVE:
        return _execute_move(intent, state)

    if intent.intent == IntentType.EXAMINE:
        return _execute_examine(intent, state)

    if intent.intent == IntentType.LOOK:
        return _execute_look(state)

    if intent.intent == IntentType.INVENTORY:
        return _execute_inventory(state)

    if intent.intent == IntentType.TALK:
        return _execute_talk(intent, state)

    if intent.intent == IntentType.ASK_ABOUT:
        return _execute_ask_about(intent, state)

    if intent.intent == IntentType.GIVE:
        return _execute_give(intent, state)

    if intent.intent == IntentType.USE:
        return _execute_use(intent, state)

    if intent.intent == IntentType.HELP:
        return _execute_help(state)

    # Unknown - shouldn't reach here after validation
    return state, ActionResult(
        success=False,
        message="I don't understand that action.",
    )


def _execute_move(intent: Intent, state: GameState) -> tuple[GameState, ActionResult]:
    """Move to a new room."""
    target = intent.target.lower()
    new_room = Room(target)
    old_room = state.current_room

    state.current_room = new_room
    room_data = ROOMS.get(target, {})

    return state, ActionResult(
        success=True,
        context={
            "action": "MOVE",
            "from_room": old_room.value,
            "to_room": target,
            "room_name": room_data.get("name", target),
            "room_description": room_data.get("description", ""),
            "characters_present": room_data.get("characters", []),
        },
        narrative_prompt=f"The keeper moves from {old_room.value} to {target}. Describe the transition and arrival.",
    )


def _execute_examine(intent: Intent, state: GameState) -> tuple[GameState, ActionResult]:
    """Examine an object."""
    target = intent.target.lower()
    flags_dict = state.flags.model_dump()

    obj = OBJECTS.get(target)

    if obj:
        # Check if examining sets a flag
        sets_flag = obj.get("sets_flag")
        if sets_flag and not flags_dict.get(sets_flag, False):
            setattr(state.flags, sets_flag, True)
            flag_newly_set = True
        else:
            flag_newly_set = False

        return state, ActionResult(
            success=True,
            context={
                "action": "EXAMINE",
                "target": target,
                "object_name": obj.get("name", target),
                "base_description": obj.get("examine_base", ""),
                "extended_description": obj.get("examine_extended", ""),
                "narrative_note": obj.get("narrative_note", ""),
                "flag_set": sets_flag if flag_newly_set else None,
                "is_discovery": flag_newly_set,
            },
            narrative_prompt=obj.get("examine_base", f"You examine the {target}."),
        )

    # Generic examination
    return state, ActionResult(
        success=True,
        context={
            "action": "EXAMINE",
            "target": target,
        },
        narrative_prompt=f"The keeper examines {target}.",
    )


def _execute_look(state: GameState) -> tuple[GameState, ActionResult]:
    """Look around the current room."""
    room_id = state.current_room.value
    room = ROOMS.get(room_id, {})
    flags_dict = state.flags.model_dump()

    visible_objects = get_visible_objects(room_id, flags_dict)

    # Build exit descriptions
    exits = room.get("exits", [])
    exit_descriptions = []
    for exit_id in exits:
        exit_room = ROOMS.get(exit_id, {})
        exit_descriptions.append(f"{exit_room.get('name', exit_id)}")

    return state, ActionResult(
        success=True,
        context={
            "action": "LOOK",
            "room_id": room_id,
            "room_name": room.get("name", room_id),
            "room_description": room.get("description", ""),
            "visible_objects": visible_objects,
            "characters": room.get("characters", []),
            "exits": exits,
            "exit_descriptions": exit_descriptions,
        },
        narrative_prompt=room.get("description", "You look around."),
    )


def _execute_inventory(state: GameState) -> tuple[GameState, ActionResult]:
    """List inventory items."""
    return state, ActionResult(
        success=True,
        context={
            "action": "INVENTORY",
            "items": state.inventory,
        },
        narrative_prompt="The keeper checks what they carry.",
    )


def _execute_talk(intent: Intent, state: GameState) -> tuple[GameState, ActionResult]:
    """Talk to a character."""
    target = intent.target.lower() if intent.target else "companion"

    if target == "traveler":
        return _talk_to_traveler(state)
    elif target == "companion":
        return _talk_to_companion(None, state)

    return state, ActionResult(
        success=True,
        context={
            "action": "TALK",
            "target": target,
        },
        narrative_prompt=f"You approach {target} to speak.",
    )


def _execute_ask_about(intent: Intent, state: GameState) -> tuple[GameState, ActionResult]:
    """Ask a character about a topic."""
    target = intent.target.lower() if intent.target else "companion"
    subject = intent.subject or "general"

    if target == "companion":
        return _talk_to_companion(subject, state)
    elif target == "traveler":
        return _talk_to_traveler(state, about=subject)

    return state, ActionResult(
        success=True,
        context={
            "action": "ASK_ABOUT",
            "target": target,
            "subject": subject,
        },
        narrative_prompt=f"You ask {target} about {subject}.",
    )


def _talk_to_traveler(state: GameState, about: str | None = None) -> tuple[GameState, ActionResult]:
    """Handle conversation with the traveler."""
    conv_stage = get_traveler_conversation_state(state.flags)

    if conv_stage:
        conv_data = TRAVELER_CONVERSATIONS[conv_stage]

        # Set the flag
        sets_flag = conv_data.get("sets_flag")
        if sets_flag:
            setattr(state.flags, sets_flag, True)

        return state, ActionResult(
            success=True,
            context={
                "action": "TALK",
                "target": "traveler",
                "conversation_stage": conv_stage,
                "about": about,
                "prompt_context": conv_data.get("prompt_context", ""),
            },
            narrative_prompt=conv_data.get("prompt_context", "The traveler speaks."),
        )

    # No new conversation available
    return state, ActionResult(
        success=True,
        context={
            "action": "TALK",
            "target": "traveler",
            "about": about,
            "no_new_dialogue": True,
        },
        narrative_prompt="The traveler has nothing new to say right now. Perhaps you should explore more, or help them remember.",
    )


def _talk_to_companion(subject: str | None, state: GameState) -> tuple[GameState, ActionResult]:
    """Handle conversation with the companion."""
    topic_data = get_companion_topic(subject or "default", state.flags)

    if not topic_data:
        topic_data = COMPANION_TOPICS["default"]

    # Set any flags
    sets_flag = topic_data.get("sets_flag")
    if sets_flag:
        setattr(state.flags, sets_flag, True)

    return state, ActionResult(
        success=True,
        context={
            "action": "ASK_ABOUT" if subject else "TALK",
            "target": "companion",
            "subject": subject,
            "topic_key": subject or "default",
            "prompt_context": topic_data.get("prompt_context", ""),
            "flag_set": sets_flag,
        },
        narrative_prompt=topic_data.get("prompt_context", "The companion responds."),
    )


def _execute_give(intent: Intent, state: GameState) -> tuple[GameState, ActionResult]:
    """Give an item to a character."""
    target = intent.target.lower()
    subject = intent.subject.lower() if intent.subject else ""

    # Remove from inventory
    state.inventory = [i for i in state.inventory if i.lower() != target]

    return state, ActionResult(
        success=True,
        context={
            "action": "GIVE",
            "item": target,
            "recipient": subject,
        },
        narrative_prompt=f"The keeper offers {target} to {subject}.",
    )


def _execute_use(intent: Intent, state: GameState) -> tuple[GameState, ActionResult]:
    """Use an item."""
    target = intent.target.lower()

    return state, ActionResult(
        success=True,
        context={
            "action": "USE",
            "target": target,
        },
        narrative_prompt=f"The keeper attempts to use {target}.",
    )


def _execute_help(state: GameState) -> tuple[GameState, ActionResult]:
    """Show help information."""
    help_text = """
You can interact with the world by typing natural language commands. Try:
- LOOK or LOOK AROUND to see your surroundings
- EXAMINE [object] to study something closely
- GO TO [place] or MOVE TO [place] to travel
- TALK TO [character] to speak with someone
- ASK [character] ABOUT [topic] to inquire about something specific
- INVENTORY to see what you carry
"""

    return state, ActionResult(
        success=True,
        context={
            "action": "HELP",
        },
        message=help_text,
        narrative_prompt="",
    )


def check_for_ending_trigger(player_input: str, state: GameState) -> str | None:
    """Check if player input triggers an ending."""
    input_lower = player_input.lower()

    # Check for truth ending trigger
    if any(phrase in input_lower for phrase in [
        "tell them everything",
        "reveal the truth",
        "tell the truth",
        "full truth",
    ]):
        if can_trigger_ending("truth", state.flags):
            return "truth"

    # Check for peace ending trigger
    if any(phrase in input_lower for phrase in [
        "let them go",
        "don't tell",
        "keep the secret",
        "let them pass",
        "spare them",
    ]):
        if can_trigger_ending("peace", state.flags):
            return "peace"

    # Check for stay ending trigger
    if any(phrase in input_lower for phrase in [
        "i will stay",
        "i choose to stay",
        "remain as keeper",
        "continue my vigil",
    ]):
        if can_trigger_ending("stay", state.flags):
            return "stay"

    return None
