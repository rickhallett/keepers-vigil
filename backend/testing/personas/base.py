"""
Base persona class and registry.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GameContext:
    """Current game context for decision making."""

    current_room: str
    inventory: list[str]
    exits: list[str]
    available_objects: list[str] = field(default_factory=list)
    available_characters: list[str] = field(default_factory=list)
    turn_number: int = 0
    last_narrative: str = ""
    last_command: str = ""
    rooms_visited: set[str] = field(default_factory=set)
    objects_examined: set[str] = field(default_factory=set)
    characters_talked_to: set[str] = field(default_factory=set)
    flags_discovered: set[str] = field(default_factory=set)
    failed_commands: list[str] = field(default_factory=list)


class Persona(ABC):
    """Base class for test personas."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this persona."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of this persona's behavior."""
        pass

    @property
    def system_prompt(self) -> str:
        """System prompt for the LLM agent playing as this persona."""
        return f"""You are simulating a player with the following persona:

**Persona:** {self.name}
**Description:** {self.description}

{self.behavior_instructions}

You must respond with ONLY a single game command. Do not include any explanation,
quotes, or additional text. Just the command itself.

Example valid responses:
- look
- go keeper_cell
- examine diagrams
- talk to traveler
- ask companion about the station
"""

    @property
    @abstractmethod
    def behavior_instructions(self) -> str:
        """Specific instructions for how this persona behaves."""
        pass

    @property
    def max_turns(self) -> int:
        """Maximum turns before this persona gives up."""
        return 100

    @property
    def goal_conditions(self) -> list[str]:
        """Conditions that indicate the persona has achieved its goal."""
        return ["ending_chosen"]

    def should_continue(self, context: GameContext) -> bool:
        """Determine if the persona should continue playing."""
        if context.turn_number >= self.max_turns:
            return False
        return True

    def modify_command(self, command: str) -> str:
        """Optionally modify a command before sending (for error injection)."""
        return command.strip()

    def get_priority_actions(self, context: GameContext) -> list[str]:
        """Get prioritized actions for the current context."""
        return []


class PersonaRegistry:
    """Registry of available test personas."""

    _personas: dict[str, Persona] = {}

    @classmethod
    def register(cls, persona: Persona) -> None:
        """Register a persona."""
        cls._personas[persona.name] = persona

    @classmethod
    def get(cls, name: str) -> Optional[Persona]:
        """Get a persona by name."""
        return cls._personas.get(name)

    @classmethod
    def list_all(cls) -> list[str]:
        """List all registered persona names."""
        return list(cls._personas.keys())

    @classmethod
    def get_all(cls) -> list[Persona]:
        """Get all registered personas."""
        return list(cls._personas.values())
