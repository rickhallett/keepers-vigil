"""
Session recording and persistence for test runs.
"""
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

from .client import APIInteraction

logger = logging.getLogger(__name__)


@dataclass
class StateSnapshot:
    """A snapshot of game state at a point in time."""

    turn_number: int
    current_room: str
    inventory: list[str]
    exits: list[str]
    available_objects: list[str] = field(default_factory=list)
    available_characters: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SessionRecord:
    """Complete record of a test session."""

    session_id: str
    persona_name: str
    persona_description: str
    started_at: str
    ended_at: Optional[str] = None

    # Interaction history
    interactions: list[dict] = field(default_factory=list)
    state_snapshots: list[dict] = field(default_factory=list)
    narratives: list[dict] = field(default_factory=list)

    # Outcome tracking
    ending_reached: Optional[str] = None
    total_turns: int = 0
    errors: list[dict] = field(default_factory=list)
    flags_discovered: list[str] = field(default_factory=list)
    rooms_visited: list[str] = field(default_factory=list)

    # Analysis metadata
    average_response_time_ms: float = 0.0
    commands_used: dict = field(default_factory=dict)


class SessionRecorder:
    """Records and persists test session data."""

    def __init__(self, output_dir: Path, session_id: str, persona_name: str, persona_description: str):
        self.output_dir = output_dir
        self.session_dir = output_dir / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.record = SessionRecord(
            session_id=session_id,
            persona_name=persona_name,
            persona_description=persona_description,
            started_at=datetime.now().isoformat(),
        )

        self._rooms_visited: set[str] = set()
        self._response_times: list[float] = []

    def record_interaction(self, interaction: APIInteraction, command: Optional[str] = None) -> None:
        """Record an API interaction."""
        interaction_dict = {
            "turn": interaction.turn_number,
            "timestamp": interaction.request.timestamp.isoformat(),
            "request": {
                "method": interaction.request.method,
                "endpoint": interaction.request.endpoint,
                "payload": interaction.request.payload,
            },
            "response": {
                "status_code": interaction.response.status_code,
                "body": interaction.response.body,
                "elapsed_ms": interaction.response.elapsed_ms,
                "error": interaction.response.error,
            },
        }
        self.record.interactions.append(interaction_dict)
        self._response_times.append(interaction.response.elapsed_ms)

        # Track command usage
        if command:
            cmd_type = command.split()[0].lower() if command else "unknown"
            self.record.commands_used[cmd_type] = self.record.commands_used.get(cmd_type, 0) + 1

    def record_narrative(self, turn: int, command: str, narrative: str, is_error: bool = False) -> None:
        """Record a narrative response."""
        self.record.narratives.append({
            "turn": turn,
            "command": command,
            "narrative": narrative,
            "is_error": is_error,
            "timestamp": datetime.now().isoformat(),
        })

    def record_state(self, state: dict, turn: int) -> None:
        """Record a state snapshot."""
        snapshot = StateSnapshot(
            turn_number=turn,
            current_room=state.get("current_room", "unknown"),
            inventory=state.get("inventory", []),
            exits=state.get("exits", state.get("available_exits", [])),
            available_objects=state.get("available_objects", []),
            available_characters=state.get("available_characters", []),
        )
        self.record.state_snapshots.append(asdict(snapshot))

        # Track room visits
        room = state.get("current_room")
        if room and room not in self._rooms_visited:
            self._rooms_visited.add(room)
            self.record.rooms_visited.append(room)

    def record_error(self, turn: int, error_type: str, message: str, context: Optional[dict] = None) -> None:
        """Record an error that occurred during the session."""
        self.record.errors.append({
            "turn": turn,
            "type": error_type,
            "message": message,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
        })

    def record_flag_discovered(self, flag: str) -> None:
        """Record a game flag that was discovered."""
        if flag not in self.record.flags_discovered:
            self.record.flags_discovered.append(flag)

    def set_ending(self, ending: str) -> None:
        """Record the ending that was reached."""
        self.record.ending_reached = ending

    def finalize(self) -> SessionRecord:
        """Finalize and save the session record."""
        self.record.ended_at = datetime.now().isoformat()
        self.record.total_turns = len([n for n in self.record.narratives if n.get("command")])

        if self._response_times:
            self.record.average_response_time_ms = sum(self._response_times) / len(self._response_times)

        # Save files
        self._save_json()
        self._save_transcript()

        logger.info(
            "Session %s finalized: %d turns, %d rooms, ending=%s",
            self.record.session_id,
            self.record.total_turns,
            len(self.record.rooms_visited),
            self.record.ending_reached,
        )

        return self.record

    def _save_json(self) -> None:
        """Save the full session record as JSON."""
        json_path = self.session_dir / "session.json"
        with open(json_path, "w") as f:
            json.dump(asdict(self.record), f, indent=2, default=str)
        logger.debug("Session JSON saved to %s", json_path)

    def _save_transcript(self) -> None:
        """Save a human-readable transcript as Markdown."""
        md_path = self.session_dir / "transcript.md"

        lines = [
            f"# Test Session Transcript",
            f"",
            f"**Session ID:** `{self.record.session_id}`",
            f"**Persona:** {self.record.persona_name}",
            f"**Description:** {self.record.persona_description}",
            f"**Started:** {self.record.started_at}",
            f"**Ended:** {self.record.ended_at}",
            f"**Total Turns:** {self.record.total_turns}",
            f"**Rooms Visited:** {', '.join(self.record.rooms_visited)}",
            f"**Ending:** {self.record.ending_reached or 'Not reached'}",
            f"",
            f"---",
            f"",
            f"## Session Transcript",
            f"",
        ]

        for narrative in self.record.narratives:
            turn = narrative.get("turn", 0)
            command = narrative.get("command", "")
            text = narrative.get("narrative", "")

            if command:
                lines.append(f"### Turn {turn}")
                lines.append(f"")
                lines.append(f"**Command:** `{command}`")
                lines.append(f"")
            lines.append(text)
            lines.append(f"")

        if self.record.errors:
            lines.extend([
                f"---",
                f"",
                f"## Errors Encountered",
                f"",
            ])
            for error in self.record.errors:
                lines.append(f"- **Turn {error['turn']}** [{error['type']}]: {error['message']}")
            lines.append(f"")

        lines.extend([
            f"---",
            f"",
            f"## Statistics",
            f"",
            f"- **Average Response Time:** {self.record.average_response_time_ms:.2f}ms",
            f"- **Commands Used:** {json.dumps(self.record.commands_used, indent=2)}",
            f"- **Flags Discovered:** {', '.join(self.record.flags_discovered) or 'None'}",
        ])

        with open(md_path, "w") as f:
            f.write("\n".join(lines))
        logger.debug("Transcript saved to %s", md_path)
