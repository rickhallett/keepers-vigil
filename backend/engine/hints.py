"""Progressive hint system for stuck players."""

from models.state import GameState


# Hints are shown progressively - first attempt gets hint[0], second gets hint[1], etc.
HINT_PROGRESSIONS = {
    "passage_locked": [
        "Perhaps there is more to discover before the way opens.",
        "The archive holds secrets. Have you examined everything there?",
        "Try examining the technical diagrams in the archive, then look for related objects.",
        "Examine the technical_diagrams, then the strange device (companion_origin_record) in the archive.",
    ],
    "no_progress": [
        "There is much to discover here. Have you explored all the rooms?",
        "The keeper's cell and archive both hold secrets. Try examining objects closely.",
        "Speaking with the companion about different topics may reveal new paths.",
        "Try: go archive, examine technical_diagrams, examine companion_origin_record.",
    ],
    "stuck_in_room": [
        "Perhaps there's more to see here. Try 'look' to see what's around you.",
        "You might examine objects or talk to characters present.",
        "Try 'help' for a list of commands, or 'look' to see your surroundings.",
    ],
    "conversation_stuck": [
        "The companion knows many things. Try asking about different topics.",
        "Ask the companion about: the station, the traveler, or what you've discovered.",
        "Try: ask companion about the diagrams, or ask companion about the traveler.",
    ],
}


# Contextual suggestions based on game progress
def get_contextual_suggestions(state: GameState) -> list[str]:
    """Get suggestions based on current game progress."""
    suggestions = []
    flags = state.flags.model_dump()

    # Early game - haven't found anything yet
    if not flags.get("found_technical_diagrams"):
        suggestions.append("Try exploring the archive and examining what you find there.")

    # Found diagrams but not the device
    elif not flags.get("found_companion_origin"):
        suggestions.append("The archive may hold more secrets. Look for unusual objects.")

    # Found device but haven't talked about it
    elif not flags.get("companion_admitted_recognition"):
        suggestions.append("Perhaps you should ask the companion about what you've discovered.")

    # Ready for passage but might not know
    elif flags.get("found_companion_origin"):
        if state.current_room.value != "passage":
            suggestions.append("The passage in the archive may now be open to you.")

    # In passage - guide toward ending
    if state.current_room.value == "passage":
        if flags.get("traveler_identity_revealed"):
            suggestions.append("You could tell the traveler the truth, or let them pass in peace.")
        else:
            suggestions.append("Speaking with the traveler here may reveal important truths.")

    return suggestions


def get_progressive_hint(state: GameState, failure_type: str) -> str | None:
    """
    Get the next hint in progression based on how many times this failure has occurred.

    Returns None if no hint should be shown yet.
    """
    count = state.repeated_failures.get(failure_type, 0)
    hints = HINT_PROGRESSIONS.get(failure_type, [])

    if not hints:
        return None

    if count > 0 and count <= len(hints):
        return hints[count - 1]
    elif count > len(hints):
        return hints[-1]  # Repeat final hint

    return None


def should_show_hint(state: GameState, min_turns_between: int = 2) -> bool:
    """Check if enough turns have passed since last hint to show another."""
    return state.turn_count - state.last_hint_turn >= min_turns_between


def record_failure(state: GameState, failure_type: str) -> None:
    """Record a failure of the given type."""
    state.repeated_failures[failure_type] = state.repeated_failures.get(failure_type, 0) + 1


def clear_failure(state: GameState, failure_type: str) -> None:
    """Clear failure count when player succeeds or tries something new."""
    if failure_type in state.repeated_failures:
        del state.repeated_failures[failure_type]


def record_hint_shown(state: GameState) -> None:
    """Record that a hint was shown this turn."""
    state.last_hint_turn = state.turn_count
