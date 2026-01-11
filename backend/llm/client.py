"""Shared Anthropic client for LLM modules."""

from anthropic import Anthropic

_client: Anthropic | None = None


def get_client() -> Anthropic:
    """Get or create Anthropic client singleton."""
    global _client
    if _client is None:
        _client = Anthropic()
    return _client
