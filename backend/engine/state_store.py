"""In-memory session storage for game state.

Simple dict-based storage that loses state on restart.
Can be swapped for Redis/SQLite for persistence.
"""

from models.state import GameState

# In-memory storage
_sessions: dict[str, GameState] = {}


async def save_state(session_id: str, state: GameState) -> None:
    """Save game state to session store."""
    _sessions[session_id] = state


async def load_state(session_id: str) -> GameState | None:
    """Load game state from session store."""
    return _sessions.get(session_id)


async def delete_state(session_id: str) -> bool:
    """Delete game state from session store."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def get_active_sessions() -> int:
    """Get count of active sessions."""
    return len(_sessions)
