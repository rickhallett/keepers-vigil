"""
Methodical Explorer persona - examines everything systematically.
"""
from .base import Persona, GameContext


class MethodicalExplorer(Persona):
    """A thorough player who examines everything before progressing."""

    @property
    def name(self) -> str:
        return "methodical_explorer"

    @property
    def description(self) -> str:
        return (
            "A careful, methodical player who thoroughly explores each room before moving on. "
            "Examines every object, talks to every character, and reads all available text. "
            "Prefers to understand the full context before making story decisions."
        )

    @property
    def behavior_instructions(self) -> str:
        return """
**Behavior Guidelines:**
1. When entering a new room, first use 'look' to survey the area
2. Examine ALL objects in the current room before moving to another
3. Talk to ALL characters present and exhaust dialogue options
4. Only move to a new room when you've examined everything in the current one
5. Keep track of what you've examined and avoid repeating commands
6. When examining objects, look for clues about the story
7. If you find something interesting, try related commands (ask about it, use it)
8. Progress through rooms systematically: threshold -> keeper_cell -> archive -> letter_room
9. When you've explored everything, try to reach an ending

**Priority Order:**
1. Look at surroundings (if just entered room)
2. Examine unexamined objects
3. Talk to characters you haven't spoken to
4. Ask characters about discovered topics
5. Move to unexplored rooms
6. Revisit rooms if you gained new knowledge
"""

    @property
    def max_turns(self) -> int:
        return 150  # Explorer needs more turns

    def get_priority_actions(self, context: GameContext) -> list[str]:
        """Get prioritized actions for systematic exploration."""
        actions = []

        # If just entered a room, look first
        if context.turn_number == 0 or context.current_room not in context.rooms_visited:
            actions.append("look")

        # Examine unexamined objects
        for obj in context.available_objects:
            if obj not in context.objects_examined:
                actions.append(f"examine {obj}")

        # Talk to characters
        for char in context.available_characters:
            if char not in context.characters_talked_to:
                actions.append(f"talk to {char}")

        # Move to unexplored rooms
        for exit_room in context.exits:
            if exit_room not in context.rooms_visited:
                actions.append(f"go {exit_room}")

        return actions
