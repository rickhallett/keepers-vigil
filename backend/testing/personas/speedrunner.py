"""
Speedrunner persona - tries to complete the game quickly.
"""
from .base import Persona, GameContext


class Speedrunner(Persona):
    """A player who tries to reach an ending as quickly as possible."""

    @property
    def name(self) -> str:
        return "speedrunner"

    @property
    def description(self) -> str:
        return (
            "An experienced player who knows the game mechanics and tries to reach "
            "an ending with minimal turns. Skips optional content and focuses on "
            "the critical path to unlock the ending."
        )

    @property
    def behavior_instructions(self) -> str:
        return """
**Behavior Guidelines:**
1. Focus on the critical path to reach an ending
2. Minimize exploration - only examine essential objects
3. Key objectives in order:
   - Talk to traveler to start their arc
   - Find technical_diagrams in archive (triggers recognition)
   - Find companion_origin_record (reveals companion's nature)
   - Talk to companion about recognition
   - Find creator_journal (requires companion origin found)
   - Find old_letter (requires creator journal found)
   - Talk to traveler again to trigger identity reveal
   - Go to passage and choose an ending
4. Skip ambient objects like archway, stone_floor, strange_light
5. Use efficient commands - go directly to objectives
6. When ending is available, choose one immediately

**Critical Path:**
threshold -> archive (examine diagrams, companion_origin) ->
talk companion about recognition -> archive (creator_journal) ->
letter_room (old_letter) -> threshold (talk traveler) -> passage -> ending
"""

    @property
    def max_turns(self) -> int:
        return 50  # Speedrunner should finish quickly

    def get_priority_actions(self, context: GameContext) -> list[str]:
        """Get actions for the critical path."""
        actions = []

        # Early game: talk to traveler first
        if context.turn_number < 5 and "traveler" in context.available_characters:
            actions.append("talk to traveler")

        # Go to archive for key items
        if "archive" in context.exits and "archive" not in context.rooms_visited:
            actions.append("go archive")

        # In archive, examine key items
        if context.current_room == "archive":
            for obj in ["technical_diagrams", "companion_origin_record", "creator_journal"]:
                if obj in context.available_objects and obj not in context.objects_examined:
                    actions.append(f"examine {obj}")

        # After discoveries, talk to companion
        if "companion" in context.available_characters:
            if "found_companion_origin" in context.flags_discovered:
                actions.append("ask companion about recognition")

        # Letter room for old_letter
        if "letter_room" in context.exits and "letter_room" not in context.rooms_visited:
            actions.append("go letter_room")

        # End game
        if "passage" in context.exits:
            actions.append("go passage")

        return actions
