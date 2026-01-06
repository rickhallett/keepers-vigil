ROOMS = {
    "threshold": {
        "name": "The Threshold",
        "description": "A liminal space where the station meets... elsewhere. Stone archways frame an entrance that seems to shift when you don't look directly at it. The Traveler stands here, flickering slightly, as if not fully present.",
        "objects": ["archway", "stone_floor", "strange_light"],
        "exits": ["keeper_cell", "archive"],
        "exit_aliases": {
            "cell": "keeper_cell", "keeper's cell": "keeper_cell", "bedroom": "keeper_cell", "rest": "keeper_cell",
            "library": "archive", "records": "archive", "shelves": "archive",
        },
        "characters": ["traveler", "companion"],
    },
    "keeper_cell": {
        "name": "The Keeper's Cell",
        "description": "A small, spare room. A simple bed, a writing desk, a window that looks out onto nothing. This is where keepers have rested between vigils. The desk holds papers and a worn journal.",
        "objects": ["bed", "desk", "keeper_journal", "window", "keeper_logs"],
        "exits": ["threshold", "letter_room"],
        "exit_aliases": {
            "back": "threshold", "entrance": "threshold", "main": "threshold", "archway": "threshold", "archways": "threshold",
            "letters": "letter_room", "letter": "letter_room", "writing": "letter_room",
        },
        "characters": ["companion"],
    },
    "archive": {
        "name": "The Archive",
        "description": "Fragments of the world outside wash up here—objects, documents, echoes. Shelves line the walls, holding centuries of accumulated debris. Most is mundane. Some is not. To the north, a soft glow hints at something beyond—the passage, though it seems to resist approach.",
        "objects": ["shelves", "technical_diagrams", "faded_map", "dust", "companion_origin_record", "creator_journal"],
        "exits": ["threshold", "passage"],
        "exit_aliases": {
            "back": "threshold", "entrance": "threshold", "main": "threshold", "archway": "threshold", "archways": "threshold",
            "door": "passage", "doorway": "passage", "light": "passage", "forward": "passage", "onward": "passage",
        },
        "characters": ["companion"],
    },
    "letter_room": {
        "name": "The Letter Room",
        "description": "Letters left by travelers, some collected, some waiting. The air feels heavy with words unsaid. A tradition holds that letters left here sometimes reach their destinations.",
        "objects": ["letter_collection", "old_letter", "writing_materials", "candles"],
        "exits": ["keeper_cell"],
        "exit_aliases": {
            "back": "keeper_cell", "cell": "keeper_cell", "bedroom": "keeper_cell", "out": "keeper_cell",
        },
        "characters": ["companion"],
    },
    "passage": {
        "name": "The Passage",
        "description": "Where travelers go when they're ready. A doorway of soft light. You cannot see what lies beyond, but it doesn't feel frightening. It feels like an answer.",
        "objects": ["doorway", "light"],
        "exits": ["archive"],
        "exit_aliases": {
            "back": "archive", "return": "archive", "out": "archive",
        },
        "characters": ["companion"],
        "locked_until": ["traveler_identity_revealed"],
    },
}

# Room name aliases for natural language matching
ROOM_ALIASES = {
    "threshold": ["threshold", "entrance", "main", "start", "beginning", "archway", "archways"],
    "keeper_cell": ["keeper_cell", "cell", "keeper's cell", "bedroom", "rest", "my room", "quarters"],
    "archive": ["archive", "library", "records", "shelves", "storage"],
    "letter_room": ["letter_room", "letters", "letter room", "writing room"],
    "passage": ["passage", "door", "doorway", "light", "exit", "beyond", "onward"],
}


def get_room(room_id: str) -> dict | None:
    return ROOMS.get(room_id)


def resolve_room_alias(text: str, current_room_id: str) -> str | None:
    """Resolve natural language room reference to actual room ID."""
    text = text.lower().strip()

    # Direct match
    if text in ROOMS:
        return text

    # Check current room's exit aliases first
    current_room = ROOMS.get(current_room_id, {})
    exit_aliases = current_room.get("exit_aliases", {})
    if text in exit_aliases:
        return exit_aliases[text]

    # Check global aliases
    for room_id, aliases in ROOM_ALIASES.items():
        if text in aliases:
            return room_id

    # Fuzzy match - check if text contains or is contained by alias
    for room_id, aliases in ROOM_ALIASES.items():
        for alias in aliases:
            if alias in text or text in alias:
                return room_id

    return None


def get_exit_descriptions(room_id: str) -> list[str]:
    """Get human-readable exit descriptions for a room."""
    room = ROOMS.get(room_id, {})
    exits = room.get("exits", [])
    descriptions = []
    for exit_id in exits:
        exit_room = ROOMS.get(exit_id, {})
        name = exit_room.get("name", exit_id)
        descriptions.append(f"{exit_id} ({name})")
    return descriptions


def get_visible_objects(room_id: str, flags: dict) -> list[str]:
    """Return objects visible in room based on current flags."""
    room = ROOMS.get(room_id)
    if not room:
        return []

    from .objects import OBJECTS

    visible = []
    for obj_id in room["objects"]:
        obj_def = OBJECTS.get(obj_id)
        if obj_def is None:
            visible.append(obj_id)
            continue

        # Check if hidden and requires flag
        if obj_def.get("hidden"):
            requires = obj_def.get("requires_flag")
            if requires and not flags.get(requires, False):
                continue

        # Check requires_flag for non-hidden objects too
        requires = obj_def.get("requires_flag")
        if requires and not flags.get(requires, False):
            continue

        visible.append(obj_id)

    return visible
