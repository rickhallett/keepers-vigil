"""
Chaotic Player persona - random, unpredictable behavior.
"""
import random
from .base import Persona, GameContext


class ChaoticPlayer(Persona):
    """A completely unpredictable player who does random things."""

    @property
    def name(self) -> str:
        return "chaotic_player"

    @property
    def description(self) -> str:
        return (
            "An unpredictable player who makes random choices without clear logic. "
            "Tests edge cases and unexpected command sequences. May repeat commands, "
            "ignore context, or try unusual combinations."
        )

    @property
    def behavior_instructions(self) -> str:
        return """
**Behavior Guidelines:**
1. Make random choices - don't follow a logical path
2. Mix valid and semi-valid commands unpredictably
3. Sometimes repeat the same command multiple times
4. Ignore narrative hints and do your own thing
5. Jump between rooms randomly
6. Examine things in random order
7. Talk to characters at random times
8. Try weird command combinations
9. Occasionally do completely unexpected things
10. You might accidentally make progress or get stuck - both are fine

**Random Actions to Consider:**
- Standard: look, examine [random], go [random], talk [random], inventory, help
- Weird: scream, wait, think, remember, forget, sleep, dream
- Questions: what, why, who, where, how, when
- Emotional: cry, laugh, sigh, panic, relax

Your goal is to stress-test the game by being unpredictable.
"""

    @property
    def max_turns(self) -> int:
        return 75

    def get_priority_actions(self, context: GameContext) -> list[str]:
        """Generate random actions."""
        actions = []

        # Standard random actions
        standard = ["look", "inventory", "help"]
        actions.extend(standard)

        # Random object interactions
        if context.available_objects:
            obj = random.choice(context.available_objects)
            actions.append(f"examine {obj}")
            actions.append(f"use {obj}")
            actions.append(f"take {obj}")

        # Random character interactions
        if context.available_characters:
            char = random.choice(context.available_characters)
            actions.append(f"talk to {char}")
            actions.append(f"ask {char} about something")
            actions.append(f"give something to {char}")

        # Random movement
        if context.exits:
            actions.append(f"go {random.choice(context.exits)}")

        # Weird actions
        weird = [
            "wait",
            "think",
            "remember",
            "what is happening",
            "who am i",
            "scream into the void",
            "examine myself",
            "look up",
            "look down",
            "listen",
            "smell",
            "touch wall",
        ]
        actions.extend(random.sample(weird, min(3, len(weird))))

        # Shuffle to make selection random
        random.shuffle(actions)
        return actions
