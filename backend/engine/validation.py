"""Intent validation against current game state."""

from models.state import GameState, Room
from models.intent import Intent, IntentType
from data.rooms import ROOMS, get_visible_objects, resolve_room_alias, get_exit_descriptions
from data.objects import OBJECTS, can_examine_object
from engine.hints import (
    get_progressive_hint,
    should_show_hint,
    record_failure,
    record_hint_shown,
)


def validate_intent(intent: Intent, state: GameState) -> bool | str:
    """
    Validate an intent against current game state.

    Returns:
        True if valid, or an error message string if invalid.

    Side effects:
        May update state.repeated_failures and state.last_hint_turn for hint tracking.
    """
    room_id = state.current_room.value
    room = ROOMS.get(room_id, {})
    exit_names = [ROOMS.get(e, {}).get("name", e) for e in room.get("exits", [])]
    exits_str = " or ".join(exit_names) if exit_names else "nowhere"

    if intent.intent == IntentType.UNKNOWN:
        return f"I don't quite understand. You could go to {exits_str}, examine objects, or talk to someone here."

    if intent.confidence == "low" and intent.target is None:
        visible = get_visible_objects(room_id, state.flags.model_dump())
        chars = room.get("characters", [])
        return f"I'm not sure what you mean. Here you can see: {', '.join(visible[:5])}. Characters: {', '.join(chars)}."

    if not room:
        return "Something is wrong with the world. The room doesn't exist."

    flags_dict = state.flags.model_dump()

    # MOVE validation
    if intent.intent == IntentType.MOVE:
        if not intent.target:
            exit_descs = get_exit_descriptions(room_id)
            return f"Where would you like to go? From here you can reach: {', '.join(exit_descs)}."

        target = intent.target.lower()

        # Try to resolve alias
        resolved = resolve_room_alias(target, room_id)
        if resolved and resolved in room["exits"]:
            intent.target = resolved
            target = resolved
        elif resolved:
            # Valid room but not accessible from here
            exit_descs = get_exit_descriptions(room_id)
            return f"You can't reach {ROOMS.get(resolved, {}).get('name', resolved)} from here. Available: {', '.join(exit_descs)}."

        if target not in room["exits"]:
            exit_descs = get_exit_descriptions(room_id)
            return f"You can't go to '{intent.target}' from here. You can reach: {', '.join(exit_descs)}."

        # Check locked rooms
        target_room = ROOMS.get(target)
        if target_room and "locked_until" in target_room:
            for required_flag in target_room["locked_until"]:
                if not flags_dict.get(required_flag, False):
                    # Track this failure for progressive hints
                    # Use "passage_locked" key to match HINT_PROGRESSIONS
                    failure_key = "passage_locked"
                    record_failure(state, failure_key)

                    base_msg = "The way forward is not yet open to you."
                    if should_show_hint(state):
                        hint = get_progressive_hint(state, failure_key)
                        if hint:
                            record_hint_shown(state)
                            return f"{base_msg} {hint}"
                    return base_msg

        return True

    # EXAMINE validation
    if intent.intent == IntentType.EXAMINE:
        if not intent.target:
            return "What would you like to examine?"

        target = intent.target.lower()

        # Check if in inventory
        if target in [i.lower() for i in state.inventory]:
            return True

        # Check if in room's visible objects
        visible_objects = get_visible_objects(room_id, flags_dict)
        if target not in visible_objects:
            return "You don't see that here."

        # Check if object requires a flag
        if not can_examine_object(target, flags_dict):
            return "You don't see that here."

        return True

    # TALK validation
    if intent.intent == IntentType.TALK:
        if not intent.target:
            # Default to companion if available
            if "companion" in room.get("characters", []):
                intent.target = "companion"
                return True
            return "Who would you like to talk to?"

        target = intent.target.lower()
        if target not in room.get("characters", []):
            return f"You don't see {intent.target} here."

        return True

    # ASK_ABOUT validation
    if intent.intent == IntentType.ASK_ABOUT:
        if not intent.target:
            if "companion" in room.get("characters", []):
                intent.target = "companion"
            else:
                return "Who would you like to ask?"

        target = intent.target.lower()
        if target not in room.get("characters", []):
            return f"You don't see {intent.target} here."

        # Contextual guidance for asking about the player/keeper
        subject = (intent.subject or "").lower()
        if target == "companion" and any(word in subject for word in ["player", "keeper", "me", "myself", "who am i"]):
            if not flags_dict.get("found_keeper_logs", False):
                return "The companion tilts its head. 'You? There is much I could say, but... have you looked at the keeper's logs? In the cell. They might help you understand the question you're asking.'"

        return True

    # GIVE validation
    if intent.intent == IntentType.GIVE:
        if not intent.target:
            return "What would you like to give?"

        if not intent.subject:
            return "Who would you like to give it to?"

        target = intent.target.lower()
        if target not in [i.lower() for i in state.inventory]:
            return f"You don't have {intent.target}."

        subject = intent.subject.lower()
        if subject not in room.get("characters", []):
            return f"You don't see {intent.subject} here."

        return True

    # USE validation
    if intent.intent == IntentType.USE:
        if not intent.target:
            return "What would you like to use?"

        target = intent.target.lower()
        if target not in [i.lower() for i in state.inventory]:
            visible = get_visible_objects(room_id, flags_dict)
            if target not in visible:
                return f"You don't have {intent.target} and don't see it here."

        return True

    # LOOK, INVENTORY, HELP - always valid
    if intent.intent in [IntentType.LOOK, IntentType.INVENTORY, IntentType.HELP]:
        return True

    return True
