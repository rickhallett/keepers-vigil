"""
Server lifecycle management for test sessions.
"""
import asyncio
import subprocess
import sys
import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class ServerManager:
    """Manages the FastAPI server lifecycle for testing."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        startup_timeout: int = 30,
    ):
        self.host = host
        self.port = port
        self.startup_timeout = startup_timeout
        self.process: Optional[subprocess.Popen] = None
        self.backend_dir = Path(__file__).parent.parent.parent

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    async def start(self) -> bool:
        """Start the FastAPI server."""
        if await self.is_running():
            logger.info("Server already running at %s", self.base_url)
            return True

        logger.info("Starting server at %s", self.base_url)

        # Use uvicorn to run the FastAPI app
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            self.host,
            "--port",
            str(self.port),
            "--log-level",
            "warning",
        ]

        self.process = subprocess.Popen(
            cmd,
            cwd=self.backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for server to be ready
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            if await self.is_running():
                logger.info("Server started successfully")
                return True
            await asyncio.sleep(0.5)

        # Server failed to start
        self.stop()
        logger.error("Server failed to start within %d seconds", self.startup_timeout)
        return False

    def stop(self) -> None:
        """Stop the FastAPI server."""
        if self.process:
            logger.info("Stopping server")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            logger.info("Server stopped")

    async def is_running(self) -> bool:
        """Check if the server is responding."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/health",
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    @asynccontextmanager
    async def running(self):
        """Context manager for running the server."""
        started = await self.start()
        if not started:
            raise RuntimeError("Failed to start server")
        try:
            yield self
        finally:
            self.stop()

    async def restart(self) -> bool:
        """Restart the server (clears all sessions)."""
        self.stop()
        await asyncio.sleep(1)
        return await self.start()
