from enum import Enum
from pydantic import BaseModel


class Room(str, Enum):
    THRESHOLD = "threshold"
    KEEPER_CELL = "keeper_cell"
    ARCHIVE = "archive"
    LETTER_ROOM = "letter_room"
    PASSAGE = "passage"


class GameFlags(BaseModel):
    # Traveler arc
    traveler_spoke_initial: bool = False
    traveler_spoke_confused: bool = False
    traveler_spoke_remembering: bool = False

    # Discovery flags
    found_technical_diagrams: bool = False
    found_creator_journal: bool = False
    found_companion_origin: bool = False
    found_keeper_logs: bool = False
    found_old_letter: bool = False

    # Revelation flags
    confronted_companion: bool = False
    companion_admitted_recognition: bool = False
    companion_revealed_purpose: bool = False
    traveler_identity_revealed: bool = False
    player_identity_revealed: bool = False

    # Ending
    ending_chosen: str | None = None  # "truth", "peace", "stay"


class GameState(BaseModel):
    session_id: str
    current_room: Room = Room.THRESHOLD
    inventory: list[str] = []
    flags: GameFlags = GameFlags()
    conversation_history: list[dict] = []
    turn_count: int = 0
