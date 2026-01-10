"""
Decision-making strategies for player agents.
"""
import random
import logging
from abc import ABC, abstractmethod
from typing import Optional

from anthropic import Anthropic

from ..personas.base import Persona, GameContext

logger = logging.getLogger(__name__)


class DecisionStrategy(ABC):
    """Base class for command decision strategies."""

    @abstractmethod
    async def decide_command(self, persona: Persona, context: GameContext) -> str:
        """Decide the next command to execute."""
        pass


class RuleBasedStrategy(DecisionStrategy):
    """Uses persona rules and priorities to decide commands."""

    async def decide_command(self, persona: Persona, context: GameContext) -> str:
        """Decide command based on persona's priority actions."""
        priority_actions = persona.get_priority_actions(context)

        if not priority_actions:
            # Default fallback actions
            fallbacks = ["look", "help", "inventory"]
            if context.exits:
                fallbacks.append(f"go {random.choice(context.exits)}")
            return random.choice(fallbacks)

        # Pick from top priorities with some randomness
        weights = [1.0 / (i + 1) for i in range(len(priority_actions))]
        total = sum(weights)
        weights = [w / total for w in weights]

        choice = random.choices(priority_actions, weights=weights, k=1)[0]
        return persona.modify_command(choice)


class LLMStrategy(DecisionStrategy):
    """Uses Claude to decide commands based on persona and context."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.client: Optional[Anthropic] = None

    def _ensure_client(self) -> Anthropic:
        """Lazily initialize the Anthropic client."""
        if self.client is None:
            self.client = Anthropic()
        return self.client

    async def decide_command(self, persona: Persona, context: GameContext) -> str:
        """Use Claude to decide the next command."""
        client = self._ensure_client()

        # Build context message
        context_msg = self._build_context_message(context)

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=100,
                temperature=self.temperature,
                system=persona.system_prompt,
                messages=[
                    {"role": "user", "content": context_msg}
                ],
            )

            command = response.content[0].text.strip()

            # Clean up the command - remove quotes, explanations
            command = self._clean_command(command)
            command = persona.modify_command(command)

            logger.debug("LLM decided: %s", command)
            return command

        except Exception as e:
            logger.warning("LLM decision failed: %s, falling back to rule-based", e)
            fallback = RuleBasedStrategy()
            return await fallback.decide_command(persona, context)

    def _build_context_message(self, context: GameContext) -> str:
        """Build the context message for the LLM."""
        parts = [
            f"**Turn {context.turn_number}**",
            f"",
            f"**Current Room:** {context.current_room}",
            f"**Available Exits:** {', '.join(context.exits) or 'None'}",
            f"**Objects Here:** {', '.join(context.available_objects) or 'None'}",
            f"**Characters Here:** {', '.join(context.available_characters) or 'None'}",
            f"**Inventory:** {', '.join(context.inventory) or 'Empty'}",
            f"",
            f"**Rooms Visited:** {', '.join(context.rooms_visited) or 'None yet'}",
            f"**Objects Examined:** {', '.join(context.objects_examined) or 'None yet'}",
            f"**Characters Talked To:** {', '.join(context.characters_talked_to) or 'None yet'}",
            f"",
        ]

        if context.last_narrative:
            # Truncate long narratives
            narrative = context.last_narrative
            if len(narrative) > 500:
                narrative = narrative[:500] + "..."
            parts.extend([
                f"**Last Narrative:**",
                f"{narrative}",
                f"",
            ])

        if context.last_command:
            parts.append(f"**Last Command:** {context.last_command}")

        if context.failed_commands:
            recent_failures = context.failed_commands[-3:]
            parts.append(f"**Recent Failed Commands:** {', '.join(recent_failures)}")

        parts.extend([
            f"",
            f"What is your next command? Respond with ONLY the command, nothing else.",
        ])

        return "\n".join(parts)

    def _clean_command(self, command: str) -> str:
        """Clean up LLM output to extract just the command."""
        # Remove common prefixes
        prefixes = [
            "command:",
            "next command:",
            "i will",
            "i'll",
            "let me",
            ">",
            "my command is:",
        ]
        lower = command.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                command = command[len(prefix):].strip()
                lower = command.lower()

        # Remove quotes
        if command.startswith('"') and command.endswith('"'):
            command = command[1:-1]
        if command.startswith("'") and command.endswith("'"):
            command = command[1:-1]

        # Take only first line if multi-line
        command = command.split("\n")[0].strip()

        return command


class HybridStrategy(DecisionStrategy):
    """Combines rule-based and LLM strategies."""

    def __init__(
        self,
        llm_probability: float = 0.7,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
    ):
        self.llm_probability = llm_probability
        self.llm_strategy = LLMStrategy(model=model, temperature=temperature)
        self.rule_strategy = RuleBasedStrategy()

    async def decide_command(self, persona: Persona, context: GameContext) -> str:
        """Use LLM most of the time, fall back to rules."""
        if random.random() < self.llm_probability:
            return await self.llm_strategy.decide_command(persona, context)
        else:
            return await self.rule_strategy.decide_command(persona, context)
