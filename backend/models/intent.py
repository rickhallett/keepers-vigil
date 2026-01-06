from enum import Enum
from typing import Literal
from pydantic import BaseModel


class IntentType(str, Enum):
    MOVE = "MOVE"
    EXAMINE = "EXAMINE"
    TALK = "TALK"
    GIVE = "GIVE"
    USE = "USE"
    ASK_ABOUT = "ASK_ABOUT"
    INVENTORY = "INVENTORY"
    LOOK = "LOOK"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"


class Intent(BaseModel):
    intent: IntentType
    target: str | None = None
    subject: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"
