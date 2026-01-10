"""
HTTP client wrapper for test API interaction.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class APIRequest:
    """Captured API request."""

    timestamp: datetime
    method: str
    endpoint: str
    payload: Optional[dict] = None
    headers: dict = field(default_factory=dict)


@dataclass
class APIResponse:
    """Captured API response."""

    timestamp: datetime
    status_code: int
    body: Any
    elapsed_ms: float
    error: Optional[str] = None


@dataclass
class APIInteraction:
    """A complete request-response interaction."""

    request: APIRequest
    response: APIResponse
    turn_number: int = 0


class TestClient:
    """HTTP client for interacting with the game API during testing."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.interactions: list[APIInteraction] = []
        self._turn_number = 0
        self._session_id: Optional[str] = None

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id

    def _record_interaction(
        self,
        method: str,
        endpoint: str,
        payload: Optional[dict],
        response: httpx.Response,
        elapsed_ms: float,
        error: Optional[str] = None,
    ) -> APIInteraction:
        """Record a request-response interaction."""
        now = datetime.now()
        interaction = APIInteraction(
            request=APIRequest(
                timestamp=now,
                method=method,
                endpoint=endpoint,
                payload=payload,
            ),
            response=APIResponse(
                timestamp=now,
                status_code=response.status_code if response else 0,
                body=response.json() if response and response.status_code < 400 else None,
                elapsed_ms=elapsed_ms,
                error=error or (response.text if response and response.status_code >= 400 else None),
            ),
            turn_number=self._turn_number,
        )
        self.interactions.append(interaction)
        return interaction

    async def new_game(self) -> dict:
        """Start a new game session."""
        self._turn_number = 0
        endpoint = "/api/new-game"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            start = asyncio.get_event_loop().time()
            try:
                response = await client.post(f"{self.base_url}{endpoint}")
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                response.raise_for_status()
                data = response.json()
                self._session_id = data.get("session_id")
                self._record_interaction("POST", endpoint, None, response, elapsed)
                logger.info("New game started: session_id=%s", self._session_id)
                return data
            except Exception as e:
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                self._record_interaction("POST", endpoint, None, response if "response" in dir() else None, elapsed, str(e))
                raise

    async def send_command(self, command: str) -> dict:
        """Send a command to the game."""
        if not self._session_id:
            raise ValueError("No active session. Call new_game() first.")

        self._turn_number += 1
        endpoint = "/api/command"
        payload = {"session_id": self._session_id, "input": command}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            start = asyncio.get_event_loop().time()
            response = None
            try:
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                )
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                response.raise_for_status()
                data = response.json()
                self._record_interaction("POST", endpoint, payload, response, elapsed)
                logger.debug("Command sent: %s -> %s", command, data.get("current_room"))
                return data
            except Exception as e:
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                self._record_interaction("POST", endpoint, payload, response, elapsed, str(e))
                raise

    async def get_state(self) -> dict:
        """Get current game state."""
        if not self._session_id:
            raise ValueError("No active session. Call new_game() first.")

        endpoint = f"/api/state/{self._session_id}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            start = asyncio.get_event_loop().time()
            response = None
            try:
                response = await client.get(f"{self.base_url}{endpoint}")
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                response.raise_for_status()
                data = response.json()
                self._record_interaction("GET", endpoint, None, response, elapsed)
                return data
            except Exception as e:
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                self._record_interaction("GET", endpoint, response, response, elapsed, str(e))
                raise

    async def health_check(self) -> bool:
        """Check if the server is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/health")
                return response.status_code == 200
        except Exception:
            return False

    def get_all_interactions(self) -> list[APIInteraction]:
        """Get all recorded interactions."""
        return self.interactions.copy()

    def clear_interactions(self) -> None:
        """Clear recorded interactions."""
        self.interactions.clear()
        self._turn_number = 0
