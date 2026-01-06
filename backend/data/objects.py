OBJECTS = {
    "technical_diagrams": {
        "name": "Technical Diagrams",
        "room": "archive",
        "examine_base": "Precise drawings on material you don't recognize. They depict... this place. The station. But rendered as an engineer might, with measurements and annotations in an unknown script.",
        "sets_flag": "found_technical_diagrams",
        "requires_flag": None,
        "hidden": False,
        "narrative_note": "First hint that the station was built, not grown. The companion's response to questions about this should be evasive.",
    },
    "keeper_journal": {
        "name": "Keeper's Journal",
        "room": "keeper_cell",
        "examine_base": "A journal kept by a previous keeper. The entries describe travelers helped, lessons learned. But the handwriting changes several times. How many keepers have there been?",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
        "narrative_note": "Background texture. Establishes the role has existed long.",
    },
    "keeper_logs": {
        "name": "Keeper's Logs",
        "room": "keeper_cell",
        "examine_base": "Official logs, more formal than the journal. Dates that span... you can't tell how long. One entry catches your eye: 'New keeper installed. Previous keeper chose to remain as traveler could not pass. Unusual but not unprecedented.'",
        "sets_flag": "found_keeper_logs",
        "requires_flag": "companion_admitted_recognition",
        "hidden": False,
        "narrative_note": "Only becomes meaningful after companion reveals it recognizes the traveler. This is the player-identity hint.",
    },
    "companion_origin_record": {
        "name": "Strange Device",
        "room": "archive",
        "examine_base": "A crystalline object covered in the same script as the diagrams. When you touch it, you feel a hum—almost like a heartbeat. The companion goes very still when you pick it up.",
        "examine_extended": "The companion's stillness draws your attention. Behind where the device rested, you notice documents that weren't visible before—as if the device's removal revealed something hidden.",
        "sets_flag": "found_companion_origin",
        "requires_flag": "found_technical_diagrams",
        "hidden": False,
        "narrative_note": "The companion's reaction is the key here. This is what prompts confrontation.",
    },
    "creator_journal": {
        "name": "Creator's Journal",
        "room": "archive",
        "examine_base": "Hidden behind other documents. A personal journal, technical but also emotional. The writer speaks of building something to outlast them. 'If we cannot know what waits, we can at least make the crossing gentle.'",
        "sets_flag": "found_creator_journal",
        "requires_flag": "found_technical_diagrams",
        "hidden": True,
        "narrative_note": "Confirms the station's origin. The companion should recognize quotes from this.",
    },
    "old_letter": {
        "name": "Faded Letter",
        "room": "letter_room",
        "examine_base": "An old letter, never collected. The handwriting matches the creator's journal. It's addressed to someone called 'Little Light.' It speaks of hope, of what they're building, of wanting to leave something good behind.",
        "sets_flag": "found_old_letter",
        "requires_flag": "found_creator_journal",
        "hidden": True,
        "narrative_note": "Emotional resonance. 'Little Light' was their name for the companion. This is what lets the companion finally speak freely.",
    },
    # Ambient objects (no special flags)
    "archway": {
        "name": "Stone Archway",
        "room": "threshold",
        "examine_base": "Ancient stonework, worn smooth by time. The arch frames the entrance to this place. Strange symbols are carved into the keystone, faded but still visible.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "stone_floor": {
        "name": "Stone Floor",
        "room": "threshold",
        "examine_base": "Cold stone beneath your feet. It has the quality of something that has always been here, or at least long enough that the distinction no longer matters.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "strange_light": {
        "name": "Strange Light",
        "room": "threshold",
        "examine_base": "A soft luminescence that seems to come from everywhere and nowhere. It casts no shadows. It doesn't flicker. It simply is.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "bed": {
        "name": "Simple Bed",
        "room": "keeper_cell",
        "examine_base": "A narrow bed with clean linens. It looks comfortable enough. Many keepers have slept here before you.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "desk": {
        "name": "Writing Desk",
        "room": "keeper_cell",
        "examine_base": "A sturdy wooden desk, scarred with age. Inkwells and quills sit ready. Papers are stacked neatly—the journal and logs among them.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "window": {
        "name": "Window",
        "room": "keeper_cell",
        "examine_base": "The window looks out onto... nothing. Not darkness, not light. Simply an absence. It should be unsettling, but somehow it isn't.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "shelves": {
        "name": "Shelves",
        "room": "archive",
        "examine_base": "Floor-to-ceiling shelves, packed with objects and documents from countless eras. Some items you recognize. Others defy identification.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "faded_map": {
        "name": "Faded Map",
        "room": "archive",
        "examine_base": "A map of somewhere that no longer exists, or perhaps never did. The cartographer's hand was skilled, but the geography is impossible.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "dust": {
        "name": "Dust",
        "room": "archive",
        "examine_base": "Fine dust covers much of the archive. It settles slowly here, undisturbed by wind. Time moves differently in this place.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "letter_collection": {
        "name": "Letter Collection",
        "room": "letter_room",
        "examine_base": "Hundreds of letters, some sealed, some open. Final words, confessions, declarations of love. The weight of them is almost physical.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "writing_materials": {
        "name": "Writing Materials",
        "room": "letter_room",
        "examine_base": "Paper, ink, sealing wax. Everything needed to write one last letter. Some travelers do. Others don't.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "candles": {
        "name": "Candles",
        "room": "letter_room",
        "examine_base": "Candles that never seem to burn down. Their light is warm and steady. They've witnessed many farewells.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "doorway": {
        "name": "The Doorway",
        "room": "passage",
        "examine_base": "A doorway made of light. Beyond it, you sense something vast and patient. Not an ending, exactly. A continuation.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
    "light": {
        "name": "The Light",
        "room": "passage",
        "examine_base": "Soft, welcoming light. It doesn't hurt to look at. It feels like a question, not a demand.",
        "sets_flag": None,
        "requires_flag": None,
        "hidden": False,
    },
}


def get_object(obj_id: str) -> dict | None:
    return OBJECTS.get(obj_id)


def can_examine_object(obj_id: str, flags: dict) -> bool:
    """Check if an object can be examined given current flags."""
    obj = OBJECTS.get(obj_id)
    if not obj:
        return False

    requires = obj.get("requires_flag")
    if requires and not flags.get(requires, False):
        return False

    return True
