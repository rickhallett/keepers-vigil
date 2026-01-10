"""
Testing configuration for the agentic testing framework.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import os


@dataclass
class TestConfig:
    """Configuration for test sessions."""

    # Server settings
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    server_startup_timeout: int = 30

    # API settings
    base_url: str = field(default="")
    request_timeout: int = 60

    # Session settings
    max_turns: int = 100
    turn_delay: float = 0.5  # Seconds between turns

    # Recording settings
    output_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "test_sessions")
    record_requests: bool = True
    record_responses: bool = True
    record_state_changes: bool = True

    # Agent settings
    agent_model: str = "claude-sonnet-4-20250514"
    agent_temperature: float = 0.7

    # Logging level
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://{self.server_host}:{self.server_port}"
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class PersonaConfig:
    """Configuration for a test persona."""

    name: str
    description: str
    behavior_traits: list[str] = field(default_factory=list)

    # Behavioral parameters
    exploration_thoroughness: float = 0.5  # 0-1, how much to explore
    error_rate: float = 0.0  # 0-1, chance of making mistakes
    patience: float = 0.5  # 0-1, how long before trying new approaches
    goal_orientation: float = 0.5  # 0-1, how focused on completing game

    # Command preferences
    preferred_actions: list[str] = field(default_factory=list)
    avoided_actions: list[str] = field(default_factory=list)

    # Special behaviors
    inject_typos: bool = False
    repeat_commands: bool = False
    use_synonyms: bool = True
