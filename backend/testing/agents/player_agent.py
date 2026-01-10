"""
LLM-powered player agent that simulates a human playing the game.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional

from ..config import TestConfig
from ..harness.client import TestClient
from ..harness.recorder import SessionRecorder
from ..personas.base import Persona, GameContext
from .strategies import DecisionStrategy, HybridStrategy

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """Internal state tracking for the agent."""

    session_id: Optional[str] = None
    turn_number: int = 0
    current_room: str = ""
    inventory: list[str] = field(default_factory=list)
    exits: list[str] = field(default_factory=list)
    available_objects: list[str] = field(default_factory=list)
    available_characters: list[str] = field(default_factory=list)
    last_narrative: str = ""
    last_command: str = ""
    rooms_visited: set[str] = field(default_factory=set)
    objects_examined: set[str] = field(default_factory=set)
    characters_talked_to: set[str] = field(default_factory=set)
    flags_discovered: set[str] = field(default_factory=set)
    failed_commands: list[str] = field(default_factory=list)
    ending_reached: Optional[str] = None
    is_stuck: bool = False
    stuck_count: int = 0


class PlayerAgent:
    """An AI agent that plays the game as a specific persona."""

    def __init__(
        self,
        persona: Persona,
        client: TestClient,
        recorder: SessionRecorder,
        config: TestConfig,
        strategy: Optional[DecisionStrategy] = None,
    ):
        self.persona = persona
        self.client = client
        self.recorder = recorder
        self.config = config
        self.strategy = strategy or HybridStrategy(
            model=config.agent_model,
            temperature=config.agent_temperature,
        )
        self.state = AgentState()
        self._running = False

    def _get_context(self) -> GameContext:
        """Build game context from current state."""
        return GameContext(
            current_room=self.state.current_room,
            inventory=self.state.inventory.copy(),
            exits=self.state.exits.copy(),
            available_objects=self.state.available_objects.copy(),
            available_characters=self.state.available_characters.copy(),
            turn_number=self.state.turn_number,
            last_narrative=self.state.last_narrative,
            last_command=self.state.last_command,
            rooms_visited=self.state.rooms_visited.copy(),
            objects_examined=self.state.objects_examined.copy(),
            characters_talked_to=self.state.characters_talked_to.copy(),
            flags_discovered=self.state.flags_discovered.copy(),
            failed_commands=self.state.failed_commands.copy(),
        )

    def _update_state_from_response(self, response: dict, command: str = "") -> None:
        """Update internal state from API response."""
        self.state.current_room = response.get("current_room", self.state.current_room)
        self.state.inventory = response.get("inventory", self.state.inventory)
        self.state.exits = response.get("exits", response.get("available_exits", self.state.exits))
        self.state.available_objects = response.get("available_objects", [])
        self.state.available_characters = response.get("available_characters", [])
        self.state.last_narrative = response.get("narrative", "")

        # Track room visits
        if self.state.current_room:
            self.state.rooms_visited.add(self.state.current_room)

        # Track examinations and conversations from command
        if command:
            self.state.last_command = command
            cmd_lower = command.lower()

            if cmd_lower.startswith("examine "):
                obj = command[8:].strip()
                self.state.objects_examined.add(obj)

            if "talk" in cmd_lower or "ask" in cmd_lower:
                for char in ["traveler", "companion"]:
                    if char in cmd_lower:
                        self.state.characters_talked_to.add(char)

        # Detect flags from narrative hints
        self._detect_flags_from_narrative(self.state.last_narrative)

        # Detect ending
        self._detect_ending(self.state.last_narrative)

    def _detect_flags_from_narrative(self, narrative: str) -> None:
        """Detect flag discoveries from narrative text."""
        narrative_lower = narrative.lower()

        flag_hints = {
            "found_technical_diagrams": ["technical diagram", "blueprint", "schematics"],
            "found_creator_journal": ["creator's journal", "personal journal", "handwritten journal"],
            "found_companion_origin": ["companion's origin", "created the companion", "built me"],
            "found_keeper_logs": ["keeper's log", "previous keeper", "vigil records"],
            "found_old_letter": ["old letter", "faded letter", "dear little light"],
            "traveler_identity_revealed": ["you built this", "you created", "your creation"],
            "companion_admitted_recognition": ["i know who you are", "i remember you", "my creator"],
        }

        for flag, hints in flag_hints.items():
            for hint in hints:
                if hint in narrative_lower and flag not in self.state.flags_discovered:
                    self.state.flags_discovered.add(flag)
                    self.recorder.record_flag_discovered(flag)
                    logger.info("Flag discovered: %s", flag)
                    break

    def _detect_ending(self, narrative: str) -> None:
        """Detect if an ending was reached."""
        narrative_lower = narrative.lower()

        ending_hints = {
            "truth": ["revealed everything", "full truth", "nothing hidden"],
            "peace": ["let them pass", "peaceful end", "spared them"],
            "stay": ["remain as keeper", "continue the vigil", "chose to stay"],
        }

        for ending, hints in ending_hints.items():
            for hint in hints:
                if hint in narrative_lower:
                    self.state.ending_reached = ending
                    self.recorder.set_ending(ending)
                    logger.info("Ending reached: %s", ending)
                    return

    def _check_if_stuck(self, response: dict) -> bool:
        """Check if the agent is stuck in a loop."""
        # Check for repeated failures or no state change
        state_changed = response.get("state_changed", True)

        if not state_changed:
            self.state.stuck_count += 1
        else:
            self.state.stuck_count = 0

        # Stuck if no change for 5 turns
        if self.state.stuck_count >= 5:
            self.state.is_stuck = True
            return True

        return False

    async def start_game(self) -> dict:
        """Start a new game session."""
        logger.info("Starting game with persona: %s", self.persona.name)

        response = await self.client.new_game()
        self.state.session_id = response.get("session_id")
        self._update_state_from_response(response)

        # Record initial state
        interaction = self.client.interactions[-1]
        self.recorder.record_interaction(interaction)
        self.recorder.record_narrative(0, "[GAME START]", response.get("narrative", ""))
        self.recorder.record_state(response, 0)

        # Get full state for objects/characters
        try:
            state = await self.client.get_state()
            self._update_state_from_response(state)
            self.recorder.record_state(state, 0)
        except Exception as e:
            logger.warning("Failed to get initial state: %s", e)

        return response

    async def take_turn(self) -> dict:
        """Execute a single turn."""
        self.state.turn_number += 1
        context = self._get_context()

        # Decide command
        command = await self.strategy.decide_command(self.persona, context)
        logger.info("Turn %d: %s", self.state.turn_number, command)

        # Send command
        try:
            response = await self.client.send_command(command)
            self._update_state_from_response(response, command)

            # Record interaction
            interaction = self.client.interactions[-1]
            self.recorder.record_interaction(interaction, command)
            self.recorder.record_narrative(
                self.state.turn_number,
                command,
                response.get("narrative", ""),
            )
            self.recorder.record_state(response, self.state.turn_number)

            # Check if stuck
            self._check_if_stuck(response)

            # Get updated state
            try:
                state = await self.client.get_state()
                self._update_state_from_response(state)
            except Exception:
                pass

            return response

        except Exception as e:
            logger.error("Turn %d failed: %s", self.state.turn_number, e)
            self.state.failed_commands.append(command)
            self.recorder.record_error(
                self.state.turn_number,
                "command_failed",
                str(e),
                {"command": command},
            )
            return {"narrative": f"Error: {e}", "state_changed": False}

    def should_continue(self) -> bool:
        """Check if the agent should continue playing."""
        # Check turn limit
        if self.state.turn_number >= self.persona.max_turns:
            logger.info("Max turns reached: %d", self.state.turn_number)
            return False

        # Check if ending reached
        if self.state.ending_reached:
            logger.info("Ending reached: %s", self.state.ending_reached)
            return False

        # Check if stuck
        if self.state.is_stuck:
            logger.warning("Agent is stuck after %d turns", self.state.turn_number)
            return False

        # Check persona's continue condition
        context = self._get_context()
        return self.persona.should_continue(context)

    async def play_session(self) -> SessionRecorder:
        """Play a complete game session."""
        self._running = True
        logger.info("Starting session with persona: %s", self.persona.name)

        try:
            # Start the game
            await self.start_game()

            # Play until done
            while self.should_continue() and self._running:
                await self.take_turn()
                await asyncio.sleep(self.config.turn_delay)

            # Finalize recording
            self.recorder.finalize()

        except Exception as e:
            logger.error("Session failed: %s", e)
            self.recorder.record_error(
                self.state.turn_number,
                "session_failed",
                str(e),
            )
            self.recorder.finalize()
            raise

        finally:
            self._running = False

        return self.recorder

    def stop(self) -> None:
        """Stop the agent."""
        self._running = False
