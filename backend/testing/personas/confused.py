"""
Confused User persona - makes mistakes and tests error handling.
"""
import random
from .base import Persona, GameContext


class ConfusedUser(Persona):
    """A confused player who makes mistakes, typos, and invalid commands."""

    @property
    def name(self) -> str:
        return "confused_user"

    @property
    def description(self) -> str:
        return (
            "A new player who doesn't fully understand the game mechanics. "
            "Makes typos, uses wrong command syntax, tries invalid actions, "
            "and sometimes gets confused about what to do next. Tests the "
            "game's error handling and help systems."
        )

    @property
    def behavior_instructions(self) -> str:
        return """
**Behavior Guidelines:**
1. Sometimes make typos in commands (e.g., "examin" instead of "examine")
2. Use incorrect syntax occasionally (e.g., "look at thing" vs "examine thing")
3. Try actions that might not work (e.g., "eat the journal", "attack traveler")
4. Repeat commands sometimes as if you forgot you did them
5. Ask for help when confused
6. Try to use items incorrectly (e.g., "use door" when you should "go")
7. Reference objects that don't exist or aren't visible
8. Mix up character names occasionally
9. About 30% of your commands should be intentionally wrong or weird
10. Eventually try to make progress but struggle along the way

**Error Types to Test:**
- Typos: "exmaine", "talkto", "goo"
- Wrong syntax: "pick up journal", "speak with traveler"
- Invalid actions: "climb wall", "break window", "steal item"
- Non-existent targets: "examine dragon", "go to bathroom"
- Gibberish: "asdf", "???", "what do i do"
"""

    @property
    def max_turns(self) -> int:
        return 80

    def modify_command(self, command: str) -> str:
        """Inject errors into commands occasionally."""
        # 30% chance of modification
        if random.random() > 0.3:
            return command

        error_type = random.choice(["typo", "syntax", "invalid"])

        if error_type == "typo":
            return self._inject_typo(command)
        elif error_type == "syntax":
            return self._change_syntax(command)
        else:
            return self._make_invalid(command)

    def _inject_typo(self, command: str) -> str:
        """Inject a typo into the command."""
        typos = {
            "examine": ["examin", "exmaine", "examien", "exame"],
            "look": ["lok", "loook", "lokk"],
            "talk": ["takl", "talkk", "tak"],
            "go": ["goo", "g0", "og"],
            "ask": ["akk", "asl", "aks"],
        }
        for word, replacements in typos.items():
            if word in command.lower():
                return command.lower().replace(word, random.choice(replacements))
        return command

    def _change_syntax(self, command: str) -> str:
        """Change command syntax to something less standard."""
        alternatives = {
            "examine": ["look at", "inspect", "check out", "see"],
            "talk to": ["speak with", "chat with", "talk with", "converse with"],
            "go": ["walk to", "move to", "head to", "go to"],
        }
        for standard, alts in alternatives.items():
            if standard in command.lower():
                return command.lower().replace(standard, random.choice(alts))
        return command

    def _make_invalid(self, command: str) -> str:
        """Return a completely invalid command."""
        invalid_commands = [
            "help me",
            "what do i do",
            "???",
            "i don't understand",
            "eat journal",
            "climb wall",
            "attack companion",
            "fly away",
            "dance",
            "sing a song",
            "examine dragon",
            "go to bathroom",
            "pick up floor",
        ]
        return random.choice(invalid_commands)

    def get_priority_actions(self, context: GameContext) -> list[str]:
        """Mix valid and invalid actions."""
        actions = []

        # Sometimes ask for help
        if context.turn_number % 10 == 0:
            actions.append("help")

        # Try some valid actions
        if context.available_objects:
            actions.append(f"examine {random.choice(context.available_objects)}")

        if context.available_characters:
            actions.append(f"talk to {random.choice(context.available_characters)}")

        if context.exits:
            actions.append(f"go {random.choice(context.exits)}")

        # Add some invalid ones
        actions.append("what is this place")
        actions.append("i'm confused")

        return actions
