from pydantic import BaseModel
from .state import Room


class CommandRequest(BaseModel):
    session_id: str
    input: str


class CommandResponse(BaseModel):
    narrative: str
    current_room: Room
    inventory: list[str]
    exits: list[str]
    state_changed: bool


class NewGameResponse(BaseModel):
    session_id: str
    narrative: str
    current_room: Room
    inventory: list[str]
    exits: list[str]


class StateResponse(BaseModel):
    current_room: Room
    inventory: list[str]
    available_exits: list[str]
    available_objects: list[str]
    available_characters: list[str]
