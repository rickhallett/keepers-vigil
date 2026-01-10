"""
Completionist persona - tries to discover everything.
"""
from .base import Persona, GameContext


class Completionist(Persona):
    """A player who wants to discover every flag and see all content."""

    @property
    def name(self) -> str:
        return "completionist"

    @property
    def description(self) -> str:
        return (
            "A thorough player determined to discover every secret, unlock every "
            "flag, exhaust all dialogue options, and see all possible content. "
            "Will revisit areas multiple times and try every combination."
        )

    @property
    def behavior_instructions(self) -> str:
        return """
**Behavior Guidelines:**
1. Your goal is to discover ALL content and flags in the game
2. Examine every single object, even ambient ones
3. Talk to every character multiple times as new content unlocks
4. After discovering something new, revisit characters to see if dialogue changed
5. Try asking characters about every topic you've discovered
6. Check inventory frequently and try using items in different contexts
7. Revisit rooms after major discoveries - new objects may appear
8. Keep track of the game's flags and try to trigger all of them:
   - traveler_spoke_initial/confused/remembering
   - found_technical_diagrams/creator_journal/companion_origin/keeper_logs/old_letter
   - confronted_companion/companion_admitted_recognition/revealed_purpose
   - traveler_identity_revealed/player_identity_revealed
9. Before choosing an ending, make sure you've seen everything
10. Try all three endings if possible (may require multiple sessions)

**Key Topics to Ask About:**
- the station, the traveler, itself (companion), the diagrams
- recognition, purpose, the player, little light

**Objects That Unlock Others:**
- technical_diagrams -> companion_origin_record becomes visible
- companion_origin_record -> creator_journal becomes visible
- creator_journal -> old_letter becomes visible
- Ask companion about recognition -> keeper_logs becomes visible
"""

    @property
    def max_turns(self) -> int:
        return 200  # Completionist needs many turns

    @property
    def goal_conditions(self) -> list[str]:
        """Completionist wants to find everything."""
        return [
            "found_technical_diagrams",
            "found_creator_journal",
            "found_companion_origin",
            "found_keeper_logs",
            "found_old_letter",
            "traveler_identity_revealed",
            "player_identity_revealed",
            "ending_chosen",
        ]

    def get_priority_actions(self, context: GameContext) -> list[str]:
        """Actions to maximize discovery."""
        actions = []

        # Always look first in new rooms
        if context.current_room not in context.rooms_visited:
            actions.append("look")

        # Examine ALL objects
        for obj in context.available_objects:
            if obj not in context.objects_examined:
                actions.append(f"examine {obj}")

        # Talk to characters
        for char in context.available_characters:
            actions.append(f"talk to {char}")

        # Ask about discovered topics
        topics = [
            "the station",
            "the traveler",
            "itself",
            "the diagrams",
            "recognition",
            "purpose",
            "the player",
            "little light",
        ]
        if "companion" in context.available_characters:
            for topic in topics:
                actions.append(f"ask companion about {topic}")

        # Visit all rooms
        for exit_room in context.exits:
            if exit_room not in context.rooms_visited:
                actions.append(f"go {exit_room}")

        # Revisit rooms for new content
        for exit_room in context.exits:
            actions.append(f"go {exit_room}")

        # Check inventory
        actions.append("inventory")

        return actions
