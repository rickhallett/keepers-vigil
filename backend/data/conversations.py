from typing import Callable

from models.state import GameFlags


TRAVELER_CONVERSATIONS = {
    "initial": {
        "available_when": lambda flags: not flags.traveler_spoke_initial,
        "sets_flag": "traveler_spoke_initial",
        "prompt_context": "The traveler has just arrived. They are confused, fragmented. They don't know where they are or how they got here. They have vague memories of important work, something they built, but the details slip away. They are polite but disoriented.",
        "next_available": "confused",
    },
    "confused": {
        "available_when": lambda flags: flags.traveler_spoke_initial and not flags.traveler_spoke_confused,
        "sets_flag": "traveler_spoke_confused",
        "prompt_context": "The traveler is trying to remember. They speak of equations, of purpose, of colleagues they can't name. They ask about this place—what is it? Why are they here? They sense they should move on but don't know how.",
        "next_available": "remembering",
    },
    "remembering": {
        "available_when": lambda flags: flags.traveler_spoke_confused and flags.found_technical_diagrams,
        "sets_flag": "traveler_spoke_remembering",
        "prompt_context": "The traveler is beginning to remember. If shown the diagrams, something clicks. They recognize the work. It was theirs. But the memory is painful—they remember the urgency, the knowledge that time was short. They don't yet remember the companion.",
        "next_available": "confrontation",
    },
    "confrontation": {
        "available_when": lambda flags: flags.traveler_spoke_remembering and flags.companion_revealed_purpose,
        "sets_flag": "traveler_identity_revealed",
        "prompt_context": "The traveler now knows who they are and what they built. The companion has revealed itself. This is the moment of recognition. The traveler may feel grief, pride, wonder. They may have questions for the companion. They may be ready to pass, or they may want more time.",
        "next_available": "ending",
    },
}


COMPANION_TOPICS = {
    "default": {
        "requires_flag": None,
        "prompt_context": "The companion is warm, attentive, helpful. It speaks of the station, of keepers past, of the nature of travelers. It gently guides without commanding. It does not yet reveal anything about its own nature or origins.",
    },
    "the_station": {
        "requires_flag": None,
        "prompt_context": "The companion explains the station has existed for a very long time. It helps travelers pass through. It doesn't know (or claims not to know) who built it or why. If pressed, it says 'Some questions have no answers. Some answers would not help.'",
    },
    "the_traveler": {
        "requires_flag": None,
        "prompt_context": "The companion observes the traveler is confused, which is normal. It suggests patience, exploration. It does NOT yet reveal any recognition. It may mention that travelers eventually find their way to the passage when ready. If the player has found_technical_diagrams, the companion's responses become slightly more careful, more measured.",
    },
    "passage": {
        "requires_flag": None,
        "prompt_context": "The companion speaks of the passage with quiet reverence. 'It is where travelers go when they are ready. Not an ending—a continuation. The passage opens when the time is right.' If asked how to open it: 'Understanding. Discovery. When you have helped the traveler remember enough of themselves, when the truth has surfaced... the way opens.'",
    },
    "itself": {
        "requires_flag": None,
        "prompt_context": "The companion deflects gently. 'I am here to help. That is enough, isn't it?' If pressed repeatedly, it may admit it has been here 'longer than any keeper.' It does not reveal its artificial nature unprompted.",
    },
    "the_diagrams": {
        "requires_flag": "found_technical_diagrams",
        "prompt_context": "The companion pauses before answering. 'You found those. Yes. The station was built. Everything was built by someone.' It will not say more unless the player has found companion_origin_record.",
    },
    "the_passage": {
        "requires_flag": None,
        "prompt_context": "The companion speaks of the passage with reverence. 'It is where travelers go when they are ready. The light there is patient—it waits.' If the player has found_technical_diagrams, the companion adds: 'Some doors only open when the heart knows its path.' If companion_revealed_purpose is set, it may add: 'I have watched many pass through. It is always peaceful. Always right, in the end.'",
    },
    "recognition": {
        "requires_flag": "found_companion_origin",
        "sets_flag": "companion_admitted_recognition",
        "prompt_context": "The companion can no longer evade. 'Yes. I know them. I have known them since I first woke. They made me.' This sets companion_admitted_recognition. The companion speaks of waiting, of not knowing if they would ever meet, of uncertainty about what it would mean. The companion might glance toward the shelves in the archive, as if remembering something—there may be more to find there, documents the creator left behind.",
    },
    "purpose": {
        "requires_flag": "companion_admitted_recognition",
        "sets_flag": "companion_revealed_purpose",
        "prompt_context": "The companion explains: it was created to help souls pass. It cannot pass itself. It doesn't know if it has a soul. It has wondered, for a very long time. It has helped thousands of travelers. It still doesn't know if it understands what it does, or merely performs understanding.",
    },
    "the_player": {
        "requires_flag": "found_keeper_logs",
        "sets_flag": "player_identity_revealed",
        "prompt_context": "The companion hesitates. 'You came here once. As a traveler. You could not let go of something. I do not know what. You chose to stay. To help others pass while you could not.' If asked how long ago: 'Time here is not like time elsewhere. Long enough that you forgot. Perhaps forgetting was part of letting go.'",
    },
    "little_light": {
        "requires_flag": "found_old_letter",
        "prompt_context": "The companion's voice changes—softer, more vulnerable. 'They called me that. When I was new. When they were teaching me.' This is the companion at its most open. It may express something like grief, or gratitude, or simply a long-held silence finally breaking.",
    },
    "creator": {
        "requires_flag": "found_creator_journal",
        "prompt_context": "The companion speaks of the one who made it, the one who built the station. 'They wanted to help. Even knowing they would pass through themselves someday.' The companion might mention 'They told me they left a letter somewhere—the letter room, I think. In case they ever... in case someone who mattered came through.'",
    },
}


def get_traveler_conversation_state(flags: GameFlags) -> str | None:
    """Get the current available traveler conversation stage."""
    for stage_id, stage in TRAVELER_CONVERSATIONS.items():
        check_fn = stage["available_when"]
        if check_fn(flags):
            return stage_id
    return None


def get_companion_topic(topic: str, flags: GameFlags) -> dict | None:
    """Get companion topic if available given current flags."""
    # Normalize topic
    topic_key = topic.lower().replace(" ", "_").replace("the_", "")

    # Try exact match first
    if topic_key in COMPANION_TOPICS:
        topic_data = COMPANION_TOPICS[topic_key]
        requires = topic_data.get("requires_flag")
        if requires:
            if not getattr(flags, requires, False):
                return None
        return topic_data

    # Try partial matches
    for key, topic_data in COMPANION_TOPICS.items():
        if topic_key in key or key in topic_key:
            requires = topic_data.get("requires_flag")
            if requires:
                if not getattr(flags, requires, False):
                    continue
            return topic_data

    # Return default
    return COMPANION_TOPICS["default"]


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
        """,
    },
    "peace": {
        "requires": ["traveler_identity_revealed", "player_identity_revealed"],
        "trigger": "Player chooses not to burden the traveler with full knowledge",
        "narrative_prompt": """
        Some truths are kept. The traveler passes through, at peace, not knowing they built this place.
        The companion watches them go. It does not speak. There is a long silence.
        The keeper (player) may now choose: to pass through, or to remain.
        If they pass: the ending is quiet release. If they remain: duty continues, but freely chosen now.
        """,
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
        """,
    },
}


def can_trigger_ending(ending_id: str, flags: GameFlags) -> bool:
    """Check if an ending can be triggered given current flags."""
    ending = ENDINGS.get(ending_id)
    if not ending:
        return False

    for req_flag in ending["requires"]:
        if not getattr(flags, req_flag, False):
            return False

    return True
